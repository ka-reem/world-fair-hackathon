from typing import Dict, Any
from langchain.llms.base import BaseLLM
import logging

logger = logging.getLogger(__name__)

class ResponseValidator:
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def validate_response(self, task_input: str, agent_output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if an agent's response is acceptable"""
        if not agent_output or not agent_output.get("data"):
            return {
                "is_valid": False,
                "confidence": 0.0,
                "issues": ["No output provided"],
                "suggestions": ["Retry with different approach"]
            }
        
        response_text = agent_output.get("data", {}).get("response", "")
        
        # STRICT validation criteria
        issues = []
        confidence = 1.0
        
        # Check for generic fallback responses (MAJOR ISSUE)
        fallback_indicators = [
            "i'm having trouble generating",
            "having trouble generating a detailed response",
            "understand your request about the topic",
            "but I'm having trouble",
            "can't generate a detailed response",
            "trouble generating a response"
        ]
        
        response_lower = response_text.lower()
        for indicator in fallback_indicators:
            if indicator in response_lower:
                issues.append("Generic fallback response - agent failed to process task")
                confidence = 0.0  # Immediate failure
                break
        
        # Check minimum length (increased)
        if len(response_text.strip()) < 20:
            issues.append("Response too short - needs more detail")
            confidence -= 0.8
        
        # Check for actual task completion
        task_lower = task_input.lower()
        
        # Math task validation
        if any(word in task_lower for word in ["calculate", "math", "+", "-", "*", "/", "="]):
            # Must contain numbers and/or mathematical operations
            if not any(char.isdigit() for char in response_text):
                issues.append("Math task requires numerical answer")
                confidence -= 0.9
            
            # Look for actual calculation
            math_indicators = ["=", "answer", "result", "calculation", "solve"]
            if not any(indicator in response_lower for indicator in math_indicators):
                issues.append("Math response lacks calculation details")
                confidence -= 0.7
        
        # Reflection/journal task validation
        if any(word in task_lower for word in ["feel", "reflect", "stress", "emotion", "journal"]):
            empathy_words = ["understand", "sounds", "difficult", "challenging", "feel", "emotions"]
            if not any(word in response_lower for word in empathy_words):
                issues.append("Reflection response lacks empathetic content")
                confidence -= 0.8
            
            # Should have some advice or questions
            advice_indicators = ["try", "consider", "might", "could", "suggest", "help", "?"]
            if not any(indicator in response_lower for indicator in advice_indicators):
                issues.append("Reflection response lacks guidance")
                confidence -= 0.6
        
        # Explanation task validation
        if any(word in task_lower for word in ["explain", "how", "what", "why", "describe"]):
            explanation_words = ["process", "works", "because", "therefore", "first", "then", "when"]
            if not any(word in response_lower for word in explanation_words):
                issues.append("Explanation lacks educational content")
                confidence -= 0.8
        
        # Planning task validation
        if any(word in task_lower for word in ["plan", "schedule", "organize", "workout", "meal"]):
            planning_words = ["step", "first", "then", "next", "schedule", "time", "daily", "weekly"]
            if not any(word in response_lower for word in planning_words):
                issues.append("Planning response lacks structured approach")
                confidence -= 0.8
        
        # Check for error indicators
        error_indicators = ["error", "failed", "couldn't", "unable", "sorry", "can't", "cannot"]
        if any(indicator in response_lower for indicator in error_indicators):
            issues.append("Response indicates failure or inability")
            confidence -= 0.9
        
        # Check for substantive content
        word_count = len(response_text.split())
        if word_count < 10:
            issues.append("Response lacks substantial content")
            confidence -= 0.7
        elif word_count < 5:
            issues.append("Response is extremely brief")
            confidence -= 0.9
        
        # Final confidence adjustment
        confidence = max(0.0, min(1.0, confidence))
        
        # STRICT acceptance criteria - no tolerance for garbage
        is_valid = confidence >= 0.7 and len(issues) == 0
        
        result = {
            "is_valid": is_valid,
            "confidence": confidence,
            "issues": issues,
            "suggestions": ["Provide actual task completion", "Include relevant details", "Avoid generic responses"] if not is_valid else []
        }
        
        logger.info(f"🔍 Validation result: valid={is_valid}, confidence={confidence:.2f}")
        if issues:
            logger.warning(f"⚠️ Quality issues found: {issues}")
        
        return result 