from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from langchain.llms.base import BaseLLM
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    name: str
    capabilities: List[str]
    llm: BaseLLM
    memory: Optional[Any] = None
    tools: Optional[List[Any]] = None

class BaseAgent(ABC):
    """Base class for all agents with LangChain integration"""
    
    def __init__(self, config: AgentConfig):
        self.name = config.name
        self.capabilities = config.capabilities
        self.memory = config.memory or ConversationBufferMemory()
        self.tools = config.tools or []
        self.llm = config.llm
        self._executor: Optional[AgentExecutor] = None
    
    @abstractmethod
    async def process(self, input_data: dict) -> dict:
        """Process the input data and return results"""
        pass

class AgentFactory:
    """Factory for creating new agents dynamically"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def generate_blueprint(self, analysis: dict) -> dict:
        """Generate a blueprint for a new agent based on task analysis"""
        task_type = analysis.get("task_type", "general")
        required_capabilities = analysis.get("required_capabilities", [])
        domain = analysis.get("domain", "general")
        
        # Create blueprint based on analysis
        blueprint = {
            "name": f"{task_type}_agent",
            "type": task_type,
            "capabilities": required_capabilities,
            "domain": domain,
            "config": {
                "memory_type": "conversation_buffer",
                "tools": self._get_tools_for_domain(domain)
            },
            "description": f"Dynamically created agent for {task_type} tasks"
        }
        
        return blueprint
    
    async def create_agent(self, blueprint: dict) -> BaseAgent:
        """Create an agent instance from a blueprint"""
        from .dynamic_agent import DynamicAgent
        
        config = AgentConfig(
            name=blueprint["name"],
            capabilities=blueprint["capabilities"],
            llm=self.llm,
            memory=ConversationBufferMemory(),
            tools=[]
        )
        
        return DynamicAgent(config, blueprint)
    
    def _get_tools_for_domain(self, domain: str) -> List[str]:
        """Get appropriate tools for a domain"""
        tool_mapping = {
            "mathematics": ["calculator", "equation_solver"],
            "personal_development": ["mood_analyzer", "reflection_guide"],
            "academic": ["citation_extractor", "summarizer"],
            "general": ["web_search", "text_analyzer"]
        }
        return tool_mapping.get(domain, tool_mapping["general"])

class BaseAgent:
    """Base class for all agents"""
    def __init__(self, name: str, llm: BaseLLM, capabilities: list = None, description: str = ""):
        self.name = name
        self.llm = llm
        self.capabilities = capabilities or []
        self.description = description
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return response"""
        try:
            query = input_data.get("query", "")
            context = input_data.get("context", {})
            task_type = input_data.get("task_type", "general")
            
            # Create a specialized prompt based on agent type
            prompt = self._create_prompt(query, context, task_type)
            
            # Generate response using LLM
            response = await self._generate_response(prompt)
            
            return {
                "status": "success",
                "response": response,
                "agent": self.name,
                "capabilities_used": self.capabilities
            }
            
        except Exception as e:
            logger.error(f"Agent {self.name} processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }
    
    def _create_prompt(self, query: str, context: Dict[str, Any], task_type: str) -> str:
        """Create a specialized prompt based on agent capabilities"""
        if "calculate" in self.capabilities or "mathematics" in self.capabilities:
            return f"""You are a mathematics expert. Solve this problem step by step:

Problem: {query}

Please provide:
1. The solution process
2. The final answer
3. Any relevant explanations

Response:"""
        
        elif "reflect" in self.capabilities or "emotional_support" in self.capabilities:
            return f"""You are a thoughtful reflection companion. Help the user process their thoughts and feelings:

User's reflection: {query}

Please provide:
1. Acknowledgment of their feelings
2. Thoughtful questions for deeper reflection
3. Supportive guidance

Response:"""
        
        elif "analyze" in self.capabilities or "research" in self.capabilities:
            return f"""You are a research and analysis expert. Analyze this topic thoroughly:

Topic: {query}

Please provide:
1. Key points and analysis
2. Important considerations
3. Structured insights

Response:"""
        
        else:
            return f"""You are a helpful assistant. Please respond to this query:

Query: {query}

Response:"""
    
    async def _generate_response(self, prompt: str) -> str:
        """Generate response using the LLM"""
        try:
            # Use agenerate for async generation
            result = await self.llm.agenerate([prompt])
            if result and result.generations and result.generations[0]:
                return result.generations[0][0].text.strip()
            else:
                return f"I'm {self.name}, and I've processed your request, but I couldn't generate a detailed response."
        except Exception as e:
            logger.warning(f"LLM generation failed for {self.name}: {e}")
            return f"I'm {self.name}, and I understand your request about the topic, but I'm having trouble generating a detailed response right now."

class AgentFactory:
    """Factory for creating agents"""
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    def create_agent(self, blueprint: Dict[str, Any]) -> BaseAgent:
        """Create an agent from a blueprint"""
        name = blueprint.get("name", "default_agent")
        capabilities = blueprint.get("capabilities", [])
        description = blueprint.get("description", "")
        
        return BaseAgent(
            name=name, 
            llm=self.llm, 
            capabilities=capabilities,
            description=description
        )
