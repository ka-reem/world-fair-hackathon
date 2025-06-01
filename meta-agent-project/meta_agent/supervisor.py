from typing import Dict, Any, List
import logging

from workflow.supervisor_graph import SupervisorGraph

logger = logging.getLogger(__name__)

class SupervisorAgent:
    """Full LangGraph-based supervisor for complex agent orchestration"""
    
    def __init__(self, llm, allow_agent_creation: bool = True, initial_agents: List[str] = None):
        self.llm = llm
        self.allow_agent_creation = allow_agent_creation
        self.initial_agents = initial_agents if initial_agents is not None else ["fun_fact_agent"]
        self.supervisor_graph = SupervisorGraph(
            llm, 
            allow_agent_creation=allow_agent_creation,
            initial_agents=self.initial_agents
        )
        logger.info(f"✅ SupervisorAgent initialized with LangGraph workflow (agent creation {'enabled' if allow_agent_creation else 'disabled'})")
        logger.info(f"🤖 Initial agents: {self.initial_agents}")
    
    async def process(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task through the LangGraph workflow"""
        try:
            # Extract query and context from task_input
            query = task_input.get("task_input", "")
            context = task_input.get("task_context", {})
            
            # Get agent creation setting from context or use default
            allow_agent_creation = context.get("allow_agent_creation", self.allow_agent_creation)
            
            # Process through the LangGraph workflow
            result = await self.supervisor_graph.process_task(
                query, 
                context, 
                allow_agent_creation=allow_agent_creation
            )
            
            logger.info(f"LangGraph workflow completed: {result.get('status')}")
            return result
            
        except Exception as e:
            logger.error(f"Supervisor error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_used": None,
                "was_agent_created": False
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get supervisor statistics"""
        try:
            stats = self.supervisor_graph.get_execution_stats()
            stats["agent_creation_enabled"] = self.allow_agent_creation
            return stats
        except Exception as e:
            logger.error(f"Stats error: {str(e)}")
            return {"error": str(e)} 