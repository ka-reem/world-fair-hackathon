from typing import Dict, Any, Optional, List
import sys
import os
import logging
from datetime import datetime
from pathlib import Path
import json

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.llm_config import LlamaConfig, LLAMA_MODELS
from config.simple_system_detector import SystemDetector

logger = logging.getLogger(__name__)

class MetaAgentController:
    def __init__(self, model_name: str = None, use_full_supervisor: bool = True, enable_logging: bool = True, allow_agent_creation: bool = True, initial_agents: List[str] = None):
        # Auto-detect best model if none specified
        if not model_name:
            model_name, reason = SystemDetector.recommend_model()
            logger.info(f"Auto-selected model '{model_name}': {reason}")
        
        # Get system info for logging
        system_info = SystemDetector.get_system_info()
        logger.info(f"System: {system_info['cpu_count']} CPUs")
        
        # Get model configuration
        model_config = LLAMA_MODELS.get(model_name, LLAMA_MODELS["tinyllama"])
        
        # Initialize Llama LLM with CPU optimizations
        if model_config["type"] == "ollama":
            self.llm = LlamaConfig.get_ollama_llm(
                model_name=model_config["model"],
                temperature=0.7,
                num_ctx=1024,
                num_predict=256
            )
        else:
            self.llm = LlamaConfig.get_ollama_llm("tinyllama")
        
        self.model_name = model_name
        self.use_full_supervisor = use_full_supervisor
        self.enable_logging = enable_logging
        self.allow_agent_creation = allow_agent_creation
        self.initial_agents = initial_agents if initial_agents is not None else ["fun_fact_agent"]
        
        # Initialize conversation logging
        self.conversation_log: List[Dict[str, Any]] = []
        self.reports_dir = Path("reports")
        if enable_logging:
            self.reports_dir.mkdir(exist_ok=True)
        
        # Choose supervisor type
        if use_full_supervisor:
            try:
                from meta_agent.supervisor import SupervisorAgent
                self.supervisor = SupervisorAgent(
                    self.llm, 
                    allow_agent_creation=allow_agent_creation,
                    initial_agents=self.initial_agents
                )
                logger.info("✅ Using full LangGraph supervisor")
            except Exception as e:
                logger.warning(f"⚠️ Full supervisor failed to initialize: {e}")
                logger.info("🔄 Falling back to simple supervisor")
                from meta_agent.simple_supervisor import SimpleSupervisor
                self.supervisor = SimpleSupervisor(self.llm)
        else:
            from meta_agent.simple_supervisor import SimpleSupervisor
            self.supervisor = SimpleSupervisor(self.llm)
            logger.info("✅ Using simple supervisor")
        
        speed_estimate = SystemDetector.estimate_inference_time(model_name)
        logger.info(f"Initialized controller with {model_name} model (estimated speed: {speed_estimate})")
        logger.info(f"🤖 Initial agents: {self.initial_agents}")
    
    def log_conversation(self, query: str, result: dict, execution_details: dict = None) -> dict:
        """Log conversation for markdown report generation"""
        if not self.enable_logging:
            return {}
            
        timestamp = datetime.now()
        conversation_entry = {
            "timestamp": timestamp.isoformat(),
            "timestamp_readable": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "agent_used": result.get('agent_used'),
            "was_new_agent": result.get('was_agent_created', False),
            "status": result.get('status'),
            "retry_count": result.get('retry_count', 0),
            "task_type": result.get('task_type'),
            "response": result.get('response', ''),
            "execution_time": execution_details.get('execution_time', 0) if execution_details else 0,
            "workflow_path": execution_details.get('workflow_path', []) if execution_details else [],
            "decision_points": execution_details.get('decision_points', []) if execution_details else [],
            "metrics": execution_details.get('metrics', {}) if execution_details else {}
        }
        self.conversation_log.append(conversation_entry)
        return conversation_entry

    async def process_request(self, blueprint_id: Optional[str] = None, 
                            input_data: dict = None, metadata: dict = None, 
                            allow_agent_creation: Optional[bool] = None) -> dict:
        """Main entry point with automatic conversation logging"""
        start_time = datetime.now()
        
        try:
            # Use provided setting or default
            creation_setting = allow_agent_creation if allow_agent_creation is not None else self.allow_agent_creation
            
            task_input = {
                "task_input": input_data.get("query", "") if input_data else "",
                "task_context": {
                    "blueprint_id": blueprint_id,
                    "metadata": metadata or {},
                    "allow_agent_creation": creation_setting,  # Pass to context
                    **(input_data.get("context", {}) if input_data else {})
                }
            }
            
            result = await self.supervisor.process(task_input)
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Log the conversation if enabled
            if self.enable_logging:
                execution_details = {
                    "execution_time": execution_time,
                    "allow_agent_creation": creation_setting,
                    "workflow_path": ["analyze_task", "check_registry", "delegate_task", "evaluate_output", "return_output"],
                    "decision_points": [
                        {"decision": "agent_selection", "outcome": result.get('agent_used')},
                        {"decision": "agent_creation", "outcome": result.get('was_agent_created', False)},
                        {"decision": "output_quality", "outcome": result.get('status')}
                    ],
                    "metrics": {
                        "execution_time_ms": execution_time * 1000,
                        "retry_count": result.get('retry_count', 0),
                        "agent_type": "new" if result.get('was_agent_created') else "existing"
                    }
                }
                
                self.log_conversation(
                    query=task_input["task_input"],
                    result=result,
                    execution_details=execution_details
                )
            
            # Add execution time to result
            result["execution_time"] = execution_time
            
            logger.info(f"Request processed by {result.get('agent_used', 'unknown')} agent")
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Request processing failed: {str(e)}")
            
            error_result = {
                "status": "error",
                "error": str(e),
                "agent_used": None,
                "was_agent_created": False,
                "execution_time": execution_time
            }
            
            # Log error if enabled
            if self.enable_logging:
                self.log_conversation(
                    query=task_input.get("task_input", "") if 'task_input' in locals() else "unknown",
                    result=error_result,
                    execution_details={"execution_time": execution_time, "error": True}
                )
            
            return error_result

    def generate_markdown_report(self, filename: str = None) -> str:
        """Generate a comprehensive markdown report from conversation logs"""
        if not self.enable_logging:
            raise ValueError("Logging must be enabled to generate reports")
            
        if not self.conversation_log:
            raise ValueError("No conversations logged yet")
        
        timestamp = datetime.now()
        if not filename:
            filename = f"meta_agent_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        
        filepath = self.reports_dir / filename
        
        # Generate report content
        report_content = self._generate_report_content(timestamp)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"Markdown report generated: {filepath}")
        return str(filepath)

    def _generate_report_content(self, timestamp: datetime) -> str:
        """Generate the markdown report content"""
        # Calculate analytics
        total_conversations = len(self.conversation_log)
        successful_conversations = sum(1 for log in self.conversation_log if log['status'] == 'success')
        success_rate = (successful_conversations / total_conversations * 100) if total_conversations > 0 else 0
        
        # Agent usage analysis
        agent_usage = {}
        new_agents_created = 0
        total_execution_time = 0
        
        for log in self.conversation_log:
            agent = log['agent_used']
            if agent:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
            if log['was_new_agent']:
                new_agents_created += 1
            total_execution_time += log['execution_time']
        
        avg_execution_time = total_execution_time / total_conversations if total_conversations > 0 else 0
        
        # Generate Mermaid workflow diagram
        mermaid_diagram = self._get_workflow_mermaid()
        
        # Build the report
        report = f"""# Meta Agent System Execution Report

## Executive Summary
**Generated:** {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Report Period:** {self.conversation_log[0]['timestamp_readable']} to {self.conversation_log[-1]['timestamp_readable']}  
**Total Conversations:** {total_conversations}  
**Success Rate:** {success_rate:.1f}%  
**New Agents Created:** {new_agents_created}  
**Average Execution Time:** {avg_execution_time:.2f} seconds  

## System Architecture

### LangGraph Workflow
```mermaid
{mermaid_diagram}
```

### Agent Registry
- **Model:** {self.model_name}
- **Supervisor Type:** {"Full LangGraph" if self.use_full_supervisor else "Simple"}
- **Total Agent Types:** {len(agent_usage)}

## Conversation Log

"""
        
        # Add each conversation
        for i, log in enumerate(self.conversation_log, 1):
            status_emoji = "✅" if log['status'] == 'success' else "❌"
            new_agent_emoji = "🆕" if log['was_new_agent'] else "♻️"
            
            report += f"""### Conversation {i} {status_emoji} {new_agent_emoji}
**Time:** {log['timestamp_readable']}  
**Agent:** {log['agent_used']}  
**Status:** {log['status']}  
**Execution Time:** {log['execution_time']:.2f}s  
**Retries:** {log['retry_count']}  

**Query:**
```
{log['query']}
```

**Response:**
```
{log['response']}
```

**Workflow Path:** {' → '.join(log['workflow_path'])}

---

"""
        
        # Add analytics section
        report += f"""## Performance Analytics

### Agent Usage Distribution
"""
        for agent, count in sorted(agent_usage.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_conversations * 100)
            report += f"- **{agent}:** {count} uses ({percentage:.1f}%)\n"
        
        report += f"""
### Execution Metrics
- **Total Execution Time:** {total_execution_time:.2f} seconds
- **Average per Conversation:** {avg_execution_time:.2f} seconds
- **Fastest Conversation:** {min(log['execution_time'] for log in self.conversation_log):.2f} seconds
- **Slowest Conversation:** {max(log['execution_time'] for log in self.conversation_log):.2f} seconds

### System Insights
- **Agent Creation Rate:** {(new_agents_created / total_conversations * 100):.1f}% of requests spawned new agents
- **Error Rate:** {((total_conversations - successful_conversations) / total_conversations * 100):.1f}%
- **System Efficiency:** {"High" if success_rate > 90 else "Medium" if success_rate > 70 else "Low"}

## Recommendations

Based on the execution data:

"""
        
        # Add recommendations
        if success_rate > 90:
            report += "- ✅ System is performing excellently with high success rate\n"
        elif success_rate > 70:
            report += "- ⚠️ Consider investigating failed conversations to improve success rate\n"
        else:
            report += "- 🔴 Success rate is low - system needs attention\n"
        
        if avg_execution_time > 5:
            report += "- ⚡ Consider optimizing for faster response times\n"
        
        if new_agents_created / total_conversations > 0.5:
            report += "- 🤖 High agent creation rate - consider expanding base agent capabilities\n"
        
        report += f"""
## Technical Details

**System Configuration:**
- Model: {self.model_name}
- Supervisor: {"Full LangGraph" if self.use_full_supervisor else "Simple"}
- Logging: {"Enabled" if self.enable_logging else "Disabled"}

**Report Generated by:** Meta Agent Controller v1.0  
**Total Conversations Analyzed:** {total_conversations}
"""
        
        return report

    def _get_workflow_mermaid(self) -> str:
        """Get Mermaid diagram for the workflow"""
        if hasattr(self.supervisor, 'supervisor_graph'):
            try:
                return self.supervisor.supervisor_graph.get_mermaid_diagram()
            except:
                pass
        
        # Fallback simple diagram
        return """graph TD
    A[Start] --> B[Analyze Task]
    B --> C[Check Agent Registry]
    C --> D{Agent Available?}
    D -->|Yes| E[Delegate to Agent]
    D -->|No| F[Create New Agent]
    F --> E
    E --> G[Evaluate Output]
    G --> H{Output OK?}
    H -->|Yes| I[Return Result]
    H -->|No| J[Retry/Spawn]
    J --> E
    I --> K[End]"""

    def get_conversation_summary(self) -> dict:
        """Get a summary of logged conversations"""
        if not self.enable_logging:
            return {"error": "Logging not enabled"}
        
        total = len(self.conversation_log)
        if total == 0:
            return {"total_conversations": 0}
        
        successful = sum(1 for log in self.conversation_log if log['status'] == 'success')
        new_agents = sum(1 for log in self.conversation_log if log['was_new_agent'])
        total_time = sum(log['execution_time'] for log in self.conversation_log)
        
        return {
            "total_conversations": total,
            "successful_conversations": successful,
            "success_rate": (successful / total * 100),
            "new_agents_created": new_agents,
            "total_execution_time": total_time,
            "average_execution_time": total_time / total,
            "agent_usage": self._get_agent_usage_stats()
        }

    def _get_agent_usage_stats(self) -> dict:
        """Get agent usage statistics"""
        usage = {}
        for log in self.conversation_log:
            agent = log['agent_used']
            if agent:
                usage[agent] = usage.get(agent, 0) + 1
        return usage

    def clear_conversation_log(self):
        """Clear the conversation log"""
        self.conversation_log.clear()
        logger.info("Conversation log cleared")

    def export_conversation_log(self, filename: str = None) -> str:
        """Export conversation log as JSON"""
        timestamp = datetime.now()
        if not filename:
            filename = f"conversation_log_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.conversation_log, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversation log exported: {filepath}")
        return str(filepath)

    def get_supervisor_stats(self) -> dict:
        """Get statistics"""
        try:
            system_info = SystemDetector.get_system_info()
            
            # Try to get real stats from supervisor
            if hasattr(self.supervisor, 'supervisor_graph'):
                # Full supervisor with LangGraph
                stats = self.supervisor.supervisor_graph.get_execution_stats()
                available_agents = stats.get('available_agents', 0)
                agent_types = ["fun_fact_agent", "math_agent", "research_agent"]
                if 'agent_types' in stats:
                    agent_types = stats['agent_types']
                supervisor_type = "full_langgraph"
            elif hasattr(self.supervisor, 'get_stats'):
                # Any supervisor with get_stats method
                supervisor_stats = self.supervisor.get_stats()
                available_agents = supervisor_stats.get('available_agents', 0)
                agent_types = ["fun_fact_agent", "math_agent", "research_agent"]
                supervisor_type = "full" if self.use_full_supervisor else "simple"
            else:
                # Fallback defaults
                available_agents = 3
                agent_types = ["fun_fact_agent", "math_agent", "research_agent"]
                supervisor_type = "simple"
            
            return {
                "available_agents": available_agents,
                "available_blueprints": 0,
                "agent_types": agent_types,
                "llm_model": self.model_name,
                "llm_type": "llama-cpu",
                "supervisor_type": supervisor_type,
                "system_info": system_info,
                "estimated_speed": SystemDetector.estimate_inference_time(self.model_name)
            }
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {
                "available_agents": 0,
                "error": str(e)
            }
    
    def _get_timestamp(self):
        """Get current timestamp for API responses"""
        return datetime.now().isoformat()
