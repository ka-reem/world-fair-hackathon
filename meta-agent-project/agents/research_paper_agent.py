from .agent_factory import BaseAgent, AgentConfig
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
import re

class ResearchPaperAgent(BaseAgent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        self._setup_agent()
    
    def _setup_agent(self):
        # Research paper analysis prompt template
        prompt = PromptTemplate(
            input_variables=["input", "agent_scratchpad", "chat_history"],
            template="""You are a research paper analysis agent. You can analyze academic papers, extract citations, and generate summaries.

Available tools: {tools}
Tool names: {tool_names}

Chat History:
{chat_history}

Question: {input}
Thought: I need to analyze this research paper request and use appropriate tools.
{agent_scratchpad}"""
        )
        
        # Define research paper tools
        def extract_citations(text: str) -> str:
            """Extract citations from academic text"""
            try:
                # Simple regex patterns for common citation formats
                patterns = [
                    r'\(([^)]+\d{4}[^)]*)\)',  # (Author, Year) format
                    r'\[(\d+)\]',              # [1] format
                    r'([A-Z][a-z]+ et al\., \d{4})',  # Author et al., Year
                ]
                
                citations = []
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    citations.extend(matches)
                
                return f"Found {len(citations)} citations: {', '.join(citations[:10])}" if citations else "No citations found"
            except Exception as e:
                return f"Error extracting citations: {str(e)}"
        
        def summarize_abstract(text: str) -> str:
            """Generate a concise summary of an abstract"""
            try:
                # Simple summarization - extract key sentences
                sentences = text.split('.')
                key_sentences = [s.strip() for s in sentences if len(s.strip()) > 50][:3]
                summary = '. '.join(key_sentences)
                return f"Summary: {summary}"
            except Exception as e:
                return f"Error summarizing: {str(e)}"
        
        def analyze_methodology(text: str) -> str:
            """Identify methodology keywords in research text"""
            try:
                method_keywords = [
                    'experiment', 'survey', 'case study', 'qualitative', 'quantitative',
                    'statistical analysis', 'machine learning', 'deep learning',
                    'regression', 'classification', 'clustering'
                ]
                
                found_methods = [keyword for keyword in method_keywords if keyword.lower() in text.lower()]
                return f"Identified methodologies: {', '.join(found_methods)}" if found_methods else "No clear methodology identified"
            except Exception as e:
                return f"Error analyzing methodology: {str(e)}"
        
        tools = [
            Tool(name="extract_citations", func=extract_citations, description="Extract citations from academic text"),
            Tool(name="summarize_abstract", func=summarize_abstract, description="Summarize an abstract or paper section"),
            Tool(name="analyze_methodology", func=analyze_methodology, description="Identify research methodologies in text")
        ]
        
        # Setup memory and agent
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        agent = create_react_agent(self.llm, tools, prompt)
        self.agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)
    
    async def process(self, input_data: dict) -> dict:
        try:
            query = input_data.get("query", "")
            paper_text = input_data.get("paper_text", "")
            
            # Combine query with paper text if provided
            full_input = f"{query}\n\nPaper text: {paper_text}" if paper_text else query
            
            result = await self.agent_executor.ainvoke({"input": full_input})
            
            return {
                "status": "success",
                "type": "research_analysis",
                "data": {
                    "response": result["output"],
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities,
                        "query": query,
                        "has_paper_text": bool(paper_text)
                    }
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "type": "research_analysis",
                "data": {
                    "error": str(e),
                    "metadata": {
                        "agent": self.name,
                        "capabilities_used": self.capabilities
                    }
                }
            }
