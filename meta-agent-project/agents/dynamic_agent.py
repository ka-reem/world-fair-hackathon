from .agent_factory import BaseAgent, AgentConfig
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool

class DynamicAgent(BaseAgent):
    """Dynamically created agent based on task requirements"""
    
    def __init__(self, config: AgentConfig, blueprint: dict):
        super().__init__(config)
        self.blueprint = blueprint
        self._setup_agent()
    
    def _setup_agent(self):
        """Setup the agent based on its blueprint"""
        task_type = self.blueprint.get("type", "general")
        
        # Create domain-specific prompt
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "chat_history"],
            template=f"""You are a {task_type} agent with capabilities: {', '.join(self.capabilities)}.

Available tools: {{tools}}
Tool names: {{tool_names}}

Chat History:
{{chat_history}}

Question: {{input}}
Thought: I need to analyze this {task_type} task and use appropriate tools.
{{agent_scratchpad}}"""
        )
        
        # Create basic tools based on capabilities
        tools = self._create_tools_from_capabilities()
        
        # Setup memory and agent
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
    
    def _create_tools_from_capabilities(self):
        """Create tools based on agent capabilities"""
        tools = []
        
        if "analyze" in self.capabilities:
            def analyze_text(text: str) -> str:
                return f"Analysis: {text[:100]}... [Key themes and patterns identified]"
            tools.append(Tool(name="analyze", func=analyze_text, description="Analyze text content"))
        
        if "calculate" in self.capabilities:
            def calculate(expression: str) -> str:
                try:
                    result = eval(expression)
                    return str(result)
                except:
                    return "Error in calculation"
            tools.append(Tool(name="calculate", func=calculate, description="Perform calculations"))
        
        if "reflect" in self.capabilities:
            def reflect(topic: str) -> str:
                return f"Reflection on {topic}: Consider the deeper meaning and personal connections..."
            tools.append(Tool(name="reflect", func=reflect, description="Provide reflective insights"))
        
        return tools
    
    async def process(self, input_data: dict) -> dict:
        """Process input using the dynamically created agent"""
        try:
            query = input_data.get("query", "")
            result = await self.agent_executor.ainvoke({"input": query})
            
            return {
                "status": "success",
                "type": self.blueprint.get("type", "dynamic"),
                "data": {
                    "response": result["output"],
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities,
                        "query": query,
                        "dynamically_created": True
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": self.blueprint.get("type", "dynamic"),
                "data": {
                    "error": str(e),
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities
                    }
                }
            } 