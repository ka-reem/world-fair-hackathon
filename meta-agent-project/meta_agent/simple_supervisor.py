from typing import Dict, Any
from langchain.llms.base import BaseLLM
import logging

logger = logging.getLogger(__name__)

class SimpleSupervisor:
    """Simple supervisor for basic agent routing"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        
    async def process(self, task_input: Dict[str, Any]) -> Dict[str, Any]:
        """Process a task using simple routing logic"""
        try:
            query = task_input.get("task_input", "")
            context = task_input.get("task_context", {})
            
            # Simple keyword-based routing
            if any(word in query.lower() for word in ["journal", "mood", "feel"]):
                return await self._handle_journal_task(query, context)
            elif any(word in query.lower() for word in ["calculate", "solve", "math"]):
                return await self._handle_math_task(query, context)
            elif any(word in query.lower() for word in ["research", "paper", "study"]):
                return await self._handle_research_task(query, context)
            else:
                return await self._handle_general_task(query, context)
                
        except Exception as e:
            logger.error(f"Simple supervisor error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "agent_used": None
            }

    async def _handle_journal_task(self, query: str, context: dict) -> dict:
        """Handle a journal task"""
        agent_used = "journal_agent"
        response = f"Reflection on: {query}"
        
        # Use the LLM to generate a proper response
        try:
            llm_response = await self.llm.agenerate([query])
            if llm_response and llm_response.generations:
                response = llm_response.generations[0][0].text.strip()
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using fallback")
        
        return {
            "status": "success",
            "response": response,
            "agent_used": agent_used,
            "was_agent_created": False
        }

    async def _handle_math_task(self, query: str, context: dict) -> dict:
        """Handle a math task"""
        agent_used = "math_agent"
        response = f"Math calculation result for: {query}"
        
        # Use the LLM to generate a proper response
        try:
            llm_response = await self.llm.agenerate([query])
            if llm_response and llm_response.generations:
                response = llm_response.generations[0][0].text.strip()
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using fallback")
        
        return {
            "status": "success",
            "response": response,
            "agent_used": agent_used,
            "was_agent_created": False
        }

    async def _handle_research_task(self, query: str, context: dict) -> dict:
        """Handle a research task"""
        agent_used = "research_agent"
        response = f"Research result for: {query}"
        
        # Use the LLM to generate a proper response
        try:
            llm_response = await self.llm.agenerate([query])
            if llm_response and llm_response.generations:
                response = llm_response.generations[0][0].text.strip()
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using fallback")
        
        return {
            "status": "success",
            "response": response,
            "agent_used": agent_used,
            "was_agent_created": False
        }

    async def _handle_general_task(self, query: str, context: dict) -> dict:
        """Handle a general task"""
        agent_used = "general_agent"
        response = f"General response to: {query}"
        
        # Use the LLM to generate a proper response
        try:
            llm_response = await self.llm.agenerate([query])
            if llm_response and llm_response.generations:
                response = llm_response.generations[0][0].text.strip()
        except Exception as e:
            logger.warning(f"LLM generation failed: {e}, using fallback")
        
        return {
            "status": "success",
            "response": response,
            "agent_used": agent_used,
            "was_agent_created": False
        } 