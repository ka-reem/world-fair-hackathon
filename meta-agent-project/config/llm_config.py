from typing import Dict, Any
from langchain_community.llms import Ollama, LlamaCpp
from langchain.llms.base import BaseLLM
import os

class LlamaConfig:
    """Configuration for different Llama model setups - CPU optimized"""
    
    @staticmethod
    def get_ollama_llm(model_name: str, **kwargs) -> Ollama:
        """Get configured Ollama LLM instance"""
        return Ollama(
            model=model_name,
            temperature=kwargs.get("temperature", 0.7),
            num_ctx=kwargs.get("num_ctx", 1024),
            num_predict=kwargs.get("num_predict", 256)
        )
    
    @staticmethod
    def get_llamacpp_llm(model_path: str, **kwargs) -> BaseLLM:
        """Get LlamaCpp-based local model (CPU optimized)"""
        cpu_optimized_config = {
            "temperature": 0.7,
            "max_tokens": 512,  # Shorter for faster CPU inference
            "n_ctx": 2048,      # Reduced context window
            "n_batch": 8,       # Smaller batch size for CPU
            "n_threads": os.cpu_count(),  # Use all CPU cores
            "verbose": False,
            "use_mlock": True,  # Keep model in memory
            "n_gpu_layers": 0,  # Force CPU-only
        }
        cpu_optimized_config.update(kwargs)
        
        return LlamaCpp(
            model_path=model_path,
            **cpu_optimized_config
        )
    
    @staticmethod
    def get_huggingface_llm(model_name: str = "meta-llama/Llama-2-7b-chat-hf", **kwargs):
        """Get HuggingFace Transformers-based Llama model"""
        from langchain_community.llms import HuggingFacePipeline
        from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
        
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype="auto",
            device_map="auto"
        )
        
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=1000,
            temperature=0.7,
            **kwargs
        )
        
        return HuggingFacePipeline(pipeline=pipe)

# CPU-friendly model configurations
LLAMA_MODELS = {
    "tinyllama": {
        "type": "ollama",
        "model": "tinyllama:latest",
        "description": "Lightweight model for basic tasks"
    },
    "llama2-7b": {
        "type": "ollama",
        "model": "tinyllama:latest",
        "description": "Balanced model for general tasks (using tinyllama)"
    },
    "llama2-13b": {
        "type": "ollama",
        "model": "tinyllama:latest",
        "description": "Advanced model for complex tasks (using tinyllama)"
    },
    # Smaller, faster models for CPU
    "llama2-7b-q4": {"model": "tinyllama:latest", "type": "ollama"},
    "llama2-7b-q8": {"model": "tinyllama:latest", "type": "ollama"},
    "codellama-7b": {"model": "tinyllama:latest", "type": "ollama"},
    "llama2-chat-7b": {"model": "tinyllama:latest", "type": "ollama"},
    
    # Tiny models for very limited CPU
    "phi": {"model": "tinyllama:latest", "type": "ollama"},
}

# Recommended models by CPU capability
CPU_RECOMMENDATIONS = {
    "low_end": "tinyllama",      # 4GB RAM, older CPUs
    "mid_range": "phi",          # 8GB RAM, modern CPUs  
    "high_end": "llama2-7b-q4",  # 16GB+ RAM, powerful CPUs
} 