import platform
import psutil
import logging

logger = logging.getLogger(__name__)

class SystemDetector:
    """Simple system detection without external dependencies"""
    
    @staticmethod
    def get_system_info() -> dict:
        """Get system information for model selection"""
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "platform": platform.platform(),
            "python_version": platform.python_version()
        }
    
    @staticmethod
    def recommend_model() -> tuple[str, str]:
        """Recommend best model based on system capabilities"""
        system_info = SystemDetector.get_system_info()
        
        if system_info["memory_gb"] >= 16:
            return "llama2-13b", "Sufficient memory for large model"
        elif system_info["memory_gb"] >= 8:
            return "llama2-7b", "Good balance of performance and resource usage"
        else:
            return "tinyllama", "Limited resources, using lightweight model"
    
    @staticmethod
    def estimate_inference_time(model_name: str) -> str:
        """Estimate inference time based on model and system"""
        system_info = SystemDetector.get_system_info()
        
        if model_name == "tinyllama":
            return "~100ms per token"
        elif model_name == "llama2-7b":
            return "~200ms per token"
        elif model_name == "llama2-13b":
            return "~400ms per token"
        else:
            return "unknown" 