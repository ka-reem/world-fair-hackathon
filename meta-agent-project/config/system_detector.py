import psutil
import platform
import os

class SystemDetector:
    """Detect system capabilities and recommend appropriate models"""
    
    @staticmethod
    def get_system_info():
        """Get system specifications"""
        return {
            "cpu_count": os.cpu_count(),
            "cpu_freq": psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown",
            "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "available_ram_gb": round(psutil.virtual_memory().available / (1024**3), 1),
            "platform": platform.system(),
            "architecture": platform.machine(),
        }
    
    @staticmethod
    def recommend_model():
        """Recommend the best model for current system"""
        system_info = SystemDetector.get_system_info()
        ram_gb = system_info["available_ram_gb"]
        cpu_count = system_info["cpu_count"]
        
        if ram_gb < 6:
            return "tinyllama", "Your system has limited RAM. TinyLlama will be fastest."
        elif ram_gb < 12:
            return "phi", "Good balance of speed and capability for your system."
        elif ram_gb >= 12 and cpu_count >= 8:
            return "llama2-7b-q4", "Your system can handle the full Llama2 7B model."
        else:
            return "phi", "Recommended for your system configuration."
    
    @staticmethod
    def estimate_inference_time(model_name: str):
        """Estimate inference time based on model and system"""
        system_info = SystemDetector.get_system_info()
        
        # Rough estimates for CPU inference (tokens per second)
        model_speeds = {
            "tinyllama": {"low": 15, "mid": 25, "high": 40},
            "phi": {"low": 8, "mid": 15, "high": 25},
            "llama2-7b-q4": {"low": 2, "mid": 5, "high": 10},
        }
        
        if system_info["cpu_count"] < 4:
            tier = "low"
        elif system_info["cpu_count"] < 8:
            tier = "mid"
        else:
            tier = "high"
        
        speed = model_speeds.get(model_name, {"low": 5, "mid": 10, "high": 15})[tier]
        return f"~{speed} tokens/second" 