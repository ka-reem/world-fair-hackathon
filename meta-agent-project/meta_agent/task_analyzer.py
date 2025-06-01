from typing import Dict, Any, List
from langchain.llms.base import BaseLLM
import logging

logger = logging.getLogger(__name__)

class TaskAnalyzer:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def analyze_task(self, task_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze a task to determine required capabilities"""
        task_lower = task_input.lower()
        
        # More comprehensive keyword matching
        math_keywords = ['calculate', 'math', 'solve', '+', '-', '*', '/', 'compound', 'interest', 'formula', 'equation', 'percentage', 'rate']
        reflection_keywords = ['feel', 'reflect', 'journal', 'emotion', 'stress', 'overwhelmed', 'thoughts', 'feelings', 'clarity', 'myself']
        research_keywords = ['research', 'analyze', 'analysis', 'paper', 'study', 'impacts', 'consider', 'potential', 'future', 'trends']
        planning_keywords = ['plan', 'create', 'meal', 'schedule', 'organize', 'budget', 'prepare', 'week', 'daily']
        fun_fact_keywords = ['true or false', 't/f', 'true false', 'is it true', 'fact or fiction', 'fun fact', 'did you know', 'trivia', 'history', 'historical', 'science fact', 'geography', 'culture', 'nature fact', 'space', 'astronomy', 'art history', 'sports fact', 'yes or no', 'is it correct', 'is that right', 'can you tell me', 'do you know', 'what about', 'is there', 'does it', 'will it', 'has it', 'was it', 'were they', 'are they', 'general knowledge', 'interesting fact', 'is the', 'is china', 'is america', 'is africa', 'is europe', 'miles', 'kilometers', 'longer than', 'bigger than', 'taller than', 'wall of china', 'great wall', 'do elephants', 'do animals', 'do humans', 'can animals', 'can humans', 'will animals', 'have good memory', 'memory', 'elephant', 'animal fact', 'do they', 'can they', 'will they', 'animal', 'nature', 'wildlife']
        
        # Count keyword matches
        math_score = sum(1 for word in math_keywords if word in task_lower)
        reflection_score = sum(1 for word in reflection_keywords if word in task_lower)
        research_score = sum(1 for word in research_keywords if word in task_lower)
        planning_score = sum(1 for word in planning_keywords if word in task_lower)
        fun_fact_score = sum(1 for word in fun_fact_keywords if word in task_lower)
        
        # Determine task type based on highest score
        scores = {
            "mathematics": math_score,
            "personal_development": reflection_score,
            "academic": research_score,
            "planning": planning_score,
            "fun_facts": fun_fact_score
        }
        
        task_type = max(scores, key=scores.get)
        max_score = scores[task_type]
        
        # If no clear winner, default to general
        if max_score == 0:
            task_type = "general"
        
        # Map task types to capabilities
        capability_map = {
            "mathematics": ["calculation", "arithmetic", "algebra", "statistics"],
            "personal_development": ["reflect", "write", "emotional_support"],
            "academic": ["analyze", "summarize", "research"],
            "planning": ["organize", "plan", "create"],
            "fun_facts": ["true_false_questions", "yes_no_questions", "historical_facts", "general_knowledge", "trivia"],
            "general": ["general"]
        }
        
        result = {
            "task_type": task_type,
            "capabilities_required": capability_map.get(task_type, ["general"]),
            "complexity": "medium",
            "estimated_time": "45s",
            "confidence": max_score / max(1, len(task_input.split())),  # Confidence based on keyword density
            "keyword_scores": scores
        }
        
        logger.info(f"📊 Task analysis: {task_type} (confidence: {result['confidence']:.2f})")
        logger.info(f"🔍 Keyword scores: {scores}")
        
        return result 