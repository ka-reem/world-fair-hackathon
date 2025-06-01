#!/usr/bin/env python3
"""
FastAPI Server for Meta Agent System
Web API interface for the meta-agent system with dashboard and reporting
"""

import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field

# Import from local modules (now in same directory)
from meta_agent.controller import MetaAgentController
from meta_agent.registry import AgentRegistry
from config.llm_config import LLAMA_MODELS

# Define schemas
class AgentBlueprint(BaseModel):
    """Schema for agent blueprint"""
    type: str
    name: str
    capabilities: List[str]
    config: Dict[str, Any]
    description: Optional[str] = None

class AgentRequest(BaseModel):
    """Schema for agent processing request"""
    blueprint_id: str
    input_data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Schema for agent processing response"""
    status: str
    response: Optional[str] = None
    agent_used: Optional[str] = None
    was_agent_created: Optional[bool] = False
    task_type: Optional[str] = None
    retry_count: Optional[int] = 0
    review_notes: Optional[str] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None

class BlueprintResponse(BaseModel):
    """Schema for blueprint registration response"""
    blueprint_id: str
    status: str
    message: str

# Initialize FastAPI app
app = FastAPI(title="Meta Agent API - Llama Edition", version="1.0.0")

# Initialize controller and registry
model_name = os.getenv("LLAMA_MODEL", "tinyllama")
controller = MetaAgentController(model_name=model_name, use_full_supervisor=True)
registry = AgentRegistry()

# Global conversation log for markdown reporting
conversation_log = []

def log_conversation(query, result, execution_details=None):
    """Log conversation for markdown report generation"""
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
    conversation_log.append(conversation_entry)
    return conversation_entry

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Meta Agent API",
        "version": "1.0.0",
        "model": model_name,
        "status": "active",
        "endpoints": {
            "process": "/agents/process",
            "dashboard": "/workflow/dashboard", 
            "models": "/models",
            "report": "/workflow/report"
        }
    }

@app.post("/blueprints", response_model=BlueprintResponse)
async def register_blueprint(blueprint: AgentBlueprint):
    """Register a new agent blueprint"""
    try:
        blueprint_id = str(uuid.uuid4())
        registry.register_blueprint(blueprint_id, blueprint.dict())
        
        return BlueprintResponse(
            blueprint_id=blueprint_id,
            status="success",
            message="Blueprint registered successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/models")
async def get_available_models():
    """Get list of available Llama models"""
    return {
        "available_models": list(LLAMA_MODELS.keys()),
        "current_model": model_name,
        "model_info": LLAMA_MODELS
    }

@app.post("/agents/process", response_model=AgentResponse)
async def process_agent_request(
    request: AgentRequest,
    model: str = Query(None, description="Override model for this request")
):
    """Process a request using the specified agent blueprint"""
    try:
        start_time = datetime.now()
        
        # Use different controller if model override is specified
        if model and model in LLAMA_MODELS and model != controller.model_name:
            temp_controller = MetaAgentController(model_name=model, use_full_supervisor=True)
            result = await temp_controller.process_request(
                blueprint_id=request.blueprint_id,
                input_data=request.input_data,
                metadata=request.metadata
            )
        else:
            result = await controller.process_request(
                blueprint_id=request.blueprint_id,
                input_data=request.input_data,
                metadata=request.metadata
            )
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Log the conversation for reporting
        execution_details = {
            "execution_time": execution_time,
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
        
        log_conversation(
            query=str(request.input_data),
            result=result,
            execution_details=execution_details
        )
        
        return AgentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/available")
async def get_available_agents():
    """Get list of available agent blueprints"""
    return registry.get_available_blueprints()

@app.get("/workflow/visualization")
async def get_workflow_visualization():
    """Get the LangGraph workflow visualization data"""
    try:
        supervisor = controller.supervisor
        if hasattr(supervisor, 'supervisor_graph'):
            visualization = supervisor.supervisor_graph.get_graph_visualization()
            stats = supervisor.supervisor_graph.get_execution_stats()
            
            return {
                "workflow_graph": visualization,
                "execution_stats": stats,
                "timestamp": controller._get_timestamp()
            }
        else:
            return {"error": "Full supervisor not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/mermaid")
async def get_mermaid_diagram():
    """Get the workflow as a Mermaid diagram"""
    try:
        supervisor = controller.supervisor
        if hasattr(supervisor, 'supervisor_graph'):
            mermaid = supervisor.supervisor_graph.get_mermaid_diagram()
            return {"mermaid": mermaid}
        else:
            return {"error": "Full supervisor not available"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/report")
async def generate_markdown_report():
    """Generate a comprehensive markdown report of conversations, workflow, logic, and metrics"""
    try:
        supervisor = controller.supervisor
        if not hasattr(supervisor, 'supervisor_graph'):
            raise HTTPException(status_code=500, detail="Full supervisor not available")
        
        # Get current stats
        stats = supervisor.supervisor_graph.get_execution_stats()
        mermaid = supervisor.supervisor_graph.get_mermaid_diagram()
        
        # Generate timestamp
        timestamp = datetime.now()
        report_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        filename = f"meta_agent_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        
        # Calculate aggregate metrics
        total_conversations = len(conversation_log)
        new_agents_created = sum(1 for conv in conversation_log if conv['was_new_agent'])
        avg_execution_time = sum(conv['execution_time'] for conv in conversation_log) / max(1, total_conversations)
        success_rate = sum(1 for conv in conversation_log if conv['status'] == 'success') / max(1, total_conversations) * 100
        
        # Agent usage stats
        agent_usage = {}
        for conv in conversation_log:
            agent = conv['agent_used']
            if agent not in agent_usage:
                agent_usage[agent] = 0
            agent_usage[agent] += 1
        
        # Generate markdown content
        markdown_content = f"""# Meta-Agent System Report

**Generated:** {report_time}
**System Model:** {model_name}
**Report Type:** Comprehensive Workflow & Conversation Analysis

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total Conversations | {total_conversations} |
| New Agents Created | {new_agents_created} |
| Average Execution Time | {avg_execution_time:.3f}s |
| Success Rate | {success_rate:.1f}% |
| Available Agents | {stats['available_agents']} |
| Workflow Nodes | {stats['total_nodes']} |
| Decision Points | {stats['decision_points']} |

---

## 🏗️ System Architecture

### LangGraph Workflow Structure

```mermaid
{mermaid}
```

### Workflow Configuration

- **Total Nodes:** {stats['total_nodes']}
- **Decision Points:** {stats['decision_points']}
- **Max Retries per Agent:** {stats['max_retries_per_agent']}
- **Max Spawnable Agents:** {stats['max_agents_spawnable']}
- **Recursion Limit:** {stats['recursion_limit']}

### Agent Registry

| Agent Type | Uses | Status |
|------------|------|--------|
"""

        # Add agent usage table
        for agent in stats['agent_types']:
            uses = agent_usage.get(agent, 0)
            status = "🟢 Active" if uses > 0 else "🟡 Available"
            markdown_content += f"| `{agent}` | {uses} | {status} |\n"

        # Add dynamic agents
        for agent, uses in agent_usage.items():
            if agent not in stats['agent_types']:
                markdown_content += f"| `{agent}` | {uses} | 🆕 Dynamic |\n"

        markdown_content += f"""

---

## 💬 Conversation Log

"""

        # Add each conversation
        for i, conv in enumerate(conversation_log, 1):
            status_emoji = "✅" if conv['status'] == 'success' else "❌"
            agent_emoji = "🆕" if conv['was_new_agent'] else "♻️"
            
            markdown_content += f"""### Conversation {i}: {conv['timestamp_readable']}

**Status:** {status_emoji} {conv['status'].upper()}  
**Agent:** {agent_emoji} `{conv['agent_used']}`  
**Task Type:** `{conv['task_type']}`  
**Execution Time:** {conv['execution_time']:.3f}s  
**Retries:** {conv['retry_count']}  

#### Query
```
{conv['query']}
```

#### Response
```
{conv['response'][:500]}{'...' if len(conv['response']) > 500 else ''}
```

#### Workflow Execution
- **Path:** {' → '.join(conv['workflow_path'])}
- **Decision Points:**
"""
            
            for decision in conv['decision_points']:
                markdown_content += f"  - **{decision['decision']}:** {decision['outcome']}\n"
            
            markdown_content += f"""
#### Metrics
- Execution Time: {conv['metrics'].get('execution_time_ms', 0):.1f}ms
- Agent Type: {conv['metrics'].get('agent_type', 'unknown')}
- Retry Count: {conv['metrics'].get('retry_count', 0)}

---

"""

        markdown_content += f"""## 📈 Performance Analysis

### Execution Time Distribution

| Conversation | Agent | Time (s) | Status |
|--------------|-------|----------|--------|
"""

        for i, conv in enumerate(conversation_log, 1):
            status_icon = "✅" if conv['status'] == 'success' else "❌"
            markdown_content += f"| {i} | `{conv['agent_used']}` | {conv['execution_time']:.3f} | {status_icon} |\n"

        markdown_content += f"""

### Agent Performance Summary

| Agent | Total Uses | Avg Time (s) | Success Rate |
|-------|------------|--------------|--------------|
"""

        # Calculate agent performance
        agent_performance = {}
        for conv in conversation_log:
            agent = conv['agent_used']
            if agent not in agent_performance:
                agent_performance[agent] = {
                    'uses': 0,
                    'total_time': 0,
                    'successes': 0
                }
            
            agent_performance[agent]['uses'] += 1
            agent_performance[agent]['total_time'] += conv['execution_time']
            if conv['status'] == 'success':
                agent_performance[agent]['successes'] += 1

        for agent, perf in agent_performance.items():
            avg_time = perf['total_time'] / perf['uses']
            success_rate = (perf['successes'] / perf['uses']) * 100
            markdown_content += f"| `{agent}` | {perf['uses']} | {avg_time:.3f} | {success_rate:.1f}% |\n"

        markdown_content += f"""

---

## 🔍 System Insights

### Workflow Patterns Observed

1. **Agent Selection Logic:**
   - New agent creation rate: {(new_agents_created/max(1,total_conversations)*100):.1f}%
   - Existing agent reuse rate: {((total_conversations-new_agents_created)/max(1,total_conversations)*100):.1f}%

2. **Performance Characteristics:**
   - Average execution time: {avg_execution_time:.3f}s
   - System success rate: {success_rate:.1f}%

3. **Scalability Metrics:**
   - Current agent count: {stats['available_agents']}
   - Dynamic agent creation: {'Active' if new_agents_created > 0 else 'Inactive'}

### Recommendations

- **Performance:** {'Good' if avg_execution_time < 1.0 else 'Consider optimization'}
- **Reliability:** {'Excellent' if success_rate > 90 else 'Good' if success_rate > 80 else 'Needs improvement'}
- **Agent Efficiency:** {'Optimal' if new_agents_created/max(1,total_conversations) < 0.3 else 'Review agent matching logic'}

---

## 📋 Technical Details

**System Configuration:**
- Model: `{model_name}`
- API Version: FastAPI
- Workflow Engine: LangGraph
- Agent Registry: Dynamic
- Report Generated: {report_time}

**Data Sources:**
- Conversation logs: {total_conversations} entries
- Workflow metrics: Real-time
- Agent registry: Live state

---

*This report was automatically generated by the Meta-Agent System API*
"""

        # Save to file
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        report_path = reports_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return {
            "status": "success",
            "filename": filename,
            "path": str(report_path),
            "conversations_logged": total_conversations,
            "report_size_bytes": len(markdown_content.encode('utf-8')),
            "download_url": f"/workflow/report/download/{filename}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@app.get("/workflow/report/download/{filename}")
async def download_report(filename: str):
    """Download a generated markdown report"""
    try:
        reports_dir = Path("reports")
        report_path = reports_dir / filename
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=str(report_path),
            filename=filename,
            media_type="text/markdown"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/workflow/dashboard", response_class=HTMLResponse)
async def get_workflow_dashboard():
    """Get an HTML dashboard showing the workflow visualization"""
    try:
        supervisor = controller.supervisor
        if hasattr(supervisor, 'supervisor_graph'):
            mermaid = supervisor.supervisor_graph.get_mermaid_diagram()
            stats = supervisor.supervisor_graph.get_execution_stats()
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Meta Agent Workflow Dashboard</title>
                <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .content {{ display: grid; grid-template-columns: 1fr 300px; gap: 20px; }}
                    .diagram-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stats-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    .stat-item {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 4px; }}
                    .stat-label {{ font-weight: bold; color: #666; }}
                    .stat-value {{ color: #2196f3; font-size: 1.2em; }}
                    h1 {{ color: #333; margin: 0; }}
                    h2 {{ color: #666; margin-top: 0; }}
                    .badge {{ background: #2196f3; color: white; padding: 4px 8px; border-radius: 12px; font-size: 0.8em; }}
                    .report-section {{ margin-top: 20px; padding: 15px; background: #e8f5e8; border-radius: 4px; }}
                    .report-button {{ background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 Meta Agent Workflow Dashboard</h1>
                        <p>LangGraph-based agent orchestration system visualization</p>
                        <span class="badge">Model: {model_name}</span>
                        <span class="badge">Status: Active</span>
                        <span class="badge">Conversations: {len(conversation_log)}</span>
                    </div>
                    
                    <div class="content">
                        <div class="diagram-container">
                            <h2>🔄 Workflow Diagram</h2>
                            <div class="mermaid">
                                {mermaid}
                            </div>
                            
                            <div class="report-section">
                                <h3>📊 Generate Report</h3>
                                <p>Create a comprehensive markdown report with conversations, workflow execution, and metrics.</p>
                                <a href="/workflow/report" class="report-button">Generate Markdown Report</a>
                            </div>
                        </div>
                        
                        <div class="stats-container">
                            <h2>📊 System Statistics</h2>
                            <div class="stat-item">
                                <div class="stat-label">Total Nodes</div>
                                <div class="stat-value">{stats['total_nodes']}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Decision Points</div>
                                <div class="stat-value">{stats['decision_points']}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Available Agents</div>
                                <div class="stat-value">{stats['available_agents']}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Max Retries</div>
                                <div class="stat-value">{stats['max_retries_per_agent']}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Recursion Limit</div>
                                <div class="stat-value">{stats['recursion_limit']}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Conversations Logged</div>
                                <div class="stat-value">{len(conversation_log)}</div>
                            </div>
                            
                            <h3>🤖 Agent Types</h3>
                            {''.join([f'<div class="stat-item"><span class="badge">{agent}</span></div>' for agent in stats['agent_types']])}
                            
                            <div style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 4px;">
                                <strong>Real-time Monitoring</strong><br>
                                <small>This dashboard shows the current state of your LangGraph workflow. The diagram illustrates how tasks flow through the system from analysis to completion.</small>
                            </div>
                        </div>
                    </div>
                </div>
                
                <script>
                    mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
                </script>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        else:
            error_html = """
            <html><body>
                <h1>Error: Full supervisor not available</h1>
                <p>Please ensure the controller is initialized with use_full_supervisor=True</p>
            </body></html>
            """
            return HTMLResponse(content=error_html, status_code=500)
    except Exception as e:
        error_html = f"""
        <html><body>
            <h1>Error loading dashboard</h1>
            <p>{str(e)}</p>
        </body></html>
        """
        return HTMLResponse(content=error_html, status_code=500)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Meta Agent FastAPI Server...")
    print(f"📊 Model: {model_name}")
    print(f"🌐 Dashboard: http://localhost:8000/workflow/dashboard")
    print(f"📚 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000) 