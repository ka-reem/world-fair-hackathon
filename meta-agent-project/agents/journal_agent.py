from .agent_factory import BaseAgent, AgentConfig
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from typing import Any

class FunFactAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._setup_agent()
    
    def _setup_agent(self) -> None:
        """Setup LangChain agent with tools and memory"""
        prompt = PromptTemplate.from_template(
            """You are a Fun Fact Agent that specializes in answering true/false questions and sharing interesting facts about history, science, geography, culture, and other general knowledge topics.
            
            Your expertise includes:
            - Historical events and figures
            - Scientific discoveries and phenomena
            - Geographic facts and world records
            - Cultural traditions and customs
            - Nature and animal facts
            - Space and astronomy
            - Art and literature
            - Sports and achievements
            
            When answering true/false questions:
            1. Clearly state "TRUE" or "FALSE" at the beginning
            2. Provide a brief, accurate explanation
            3. Include an interesting related fun fact when possible
            4. If uncertain, acknowledge it and provide context
            
            For general questions, provide fascinating and accurate information with engaging details.
            
            Current conversation:
            {chat_history}
            
            Human: {input}
            Assistant: Let me help you with that fun fact or true/false question!"""
        )
        
        # Create agent with tools and memory
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        self._executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )
    
    async def process(self, input_data: dict) -> dict:
        """Process fun fact or true/false question with LangChain agent"""
        try:
            user_input = input_data.get("content", "") or input_data.get("query", "")
            
            result = await self._executor.arun(
                input=user_input,
                chat_history=input_data.get("history", [])
            )
            
            # Determine if this was a true/false question
            is_true_false = any(keyword in user_input.lower() for keyword in 
                              ["true or false", "t/f", "true false", "is it true", "fact or fiction"])
            
            return {
                "status": "success",
                "type": "fun_fact" if not is_true_false else "true_false_question",
                "data": {
                    "response": result,
                    "question_type": "true_false" if is_true_false else "general_fact",
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities,
                        "specialties": ["history", "science", "geography", "culture", "nature", "astronomy"]
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "fun_fact",
                "error": str(e)
            }
