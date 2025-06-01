from .agent_factory import BaseAgent, AgentConfig
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
import math
import statistics

class MathAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._setup_agent()
    
    def _setup_agent(self):
        # Math-specific prompt template
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "chat_history"],
            template="""You are a mathematical analysis agent. You can perform calculations, solve equations, and conduct statistical analysis.

Available tools: {tools}
Tool names: {tool_names}

Chat History:
{chat_history}

Question: {input}
Thought: I need to analyze this mathematical problem and use appropriate tools.
{agent_scratchpad}"""
        )
        
        # Define math tools
        def calculator(expression: str) -> str:
            """Evaluate mathematical expressions safely"""
            try:
                # Basic safety check - only allow math operations
                allowed_chars = set('0123456789+-*/().e ')
                if not all(c in allowed_chars for c in expression.replace(' ', '')):
                    return "Error: Invalid characters in expression"
                result = eval(expression)
                return str(result)
            except Exception as e:
                return f"Error: {str(e)}"
        
        def statistics_tool(data_str: str) -> str:
            """Calculate basic statistics for a list of numbers"""
            try:
                data = [float(x.strip()) for x in data_str.split(',')]
                mean = statistics.mean(data)
                median = statistics.median(data)
                stdev = statistics.stdev(data) if len(data) > 1 else 0
                return f"Mean: {mean}, Median: {median}, Std Dev: {stdev}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        tools = [
            Tool(name="calculator", func=calculator, description="Evaluate mathematical expressions"),
            Tool(name="statistics", func=statistics_tool, description="Calculate statistics for comma-separated numbers")
        ]
        
        # Setup memory and agent
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
    
    async def process(self, input_data: dict) -> dict:
        try:
            query = input_data.get("query", "")
            result = await self.agent_executor.ainvoke({"input": query})
            
            return {
                "status": "success",
                "type": "math_result",
                "data": {
                    "response": result["output"],
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities,
                        "query": query
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "math_result",
                "data": {
                    "error": str(e),
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities
                    }
                }
            }
