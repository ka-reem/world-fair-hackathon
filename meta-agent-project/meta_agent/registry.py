from typing import Dict, List, Any, Optional
from agents.agent_factory import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Manages agent blueprints and results"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.blueprints: Dict[str, Dict[str, Any]] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the registry"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(name)
    
    def get_available_agents(self) -> List[BaseAgent]:
        """Get all available agents"""
        return list(self.agents.values())
    
    def find_agents_by_capability(self, capability: str) -> List[BaseAgent]:
        """Find agents that have a specific capability"""
        matching_agents = []
        for agent in self.agents.values():
            if hasattr(agent, 'capabilities') and capability in agent.capabilities:
                matching_agents.append(agent)
        return matching_agents
    
    def register_blueprint(self, blueprint_id: str, blueprint: Dict[str, Any]):
        """Register an agent blueprint"""
        self.blueprints[blueprint_id] = blueprint
        logger.info(f"Registered blueprint: {blueprint_id}")
    
    def get_blueprint(self, blueprint_id: str) -> Optional[Dict[str, Any]]:
        """Get a blueprint by ID"""
        return self.blueprints.get(blueprint_id)
    
    def get_available_blueprints(self) -> List[Dict[str, Any]]:
        """Get all available blueprints"""
        return list(self.blueprints.values())
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the registry"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            logger.info(f"Removed agent: {agent_id}")
            return True
        return False
    
    def store_result(self, blueprint_id: str, result: dict) -> None:
        """Store an agent execution result"""
        # Implementation needed
        pass
