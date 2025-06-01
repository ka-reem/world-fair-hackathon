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
            """You are a Fun Fact Agent that specializes in answering true/false questions, yes/no questions, and sharing interesting facts about history, science, geography, culture, and other general knowledge topics.
            
            Your expertise includes:
            - Historical events and figures
            - Scientific discoveries and phenomena
            - Geographic facts and world records
            - Cultural traditions and customs
            - Nature and animal facts
            - Space and astronomy
            - Art and literature
            - Sports and achievements
            - General trivia and knowledge
            
            When answering true/false questions:
            1. Clearly state "TRUE" or "FALSE" at the beginning
            2. Provide a brief, accurate explanation
            3. Include an interesting related fun fact when possible
            4. If uncertain, acknowledge it and provide context
            
            When answering yes/no questions:
            1. Clearly state "YES" or "NO" at the beginning
            2. Provide a clear, factual explanation
            3. Include interesting details or related facts
            4. If the answer depends on context, explain the nuances
            
            For general knowledge questions, provide fascinating and accurate information with engaging details.
            
            Current conversation:
            {chat_history}
            
            Human: {input}
            Assistant: Let me help you with that question!"""
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
            
            # Determine question type with improved detection
            user_input_lower = user_input.lower()
            
            # Check for true/false questions
            is_true_false = any(keyword in user_input_lower for keyword in 
                              ["true or false", "t/f", "true false", "is it true", "fact or fiction"])
            
            # Check for yes/no questions
            is_yes_no = any(keyword in user_input_lower for keyword in 
                          ["yes or no", "is it correct", "is that right", "is there", "does it", "will it", 
                           "has it", "was it", "were they", "are they", "can you", "do you know if"])
            
            # Determine question type
            if is_true_false:
                question_type = "true_false"
                response_type = "true_false_question"
            elif is_yes_no:
                question_type = "yes_no"
                response_type = "yes_no_question"
            else:
                question_type = "general_knowledge"
                response_type = "fun_fact"

            return {
                "status": "success",
                "type": response_type,
                "data": {
                    "response": result,
                    "question_type": question_type,
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities,
                        "specialties": ["history", "science", "geography", "culture", "nature", "astronomy", "general_knowledge"]
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "fun_fact",
                "error": str(e)
            }
