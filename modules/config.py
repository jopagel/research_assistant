"""
Configuration settings for the Research Assistant Chatbot.
"""
import os
from dataclasses import dataclass
from typing import List


@dataclass
class LLMConfig:
    """LLM configuration settings."""
    model: str = "meta-llama/Llama-3.2-3B-Instruct"
    max_tokens: int = 512
    temperature: float = 0.7


@dataclass
class AgentConfig:
    """Agent configuration settings."""
    max_iterations: int = 10
    verbose: bool = True


@dataclass  
class SecurityConfig:
    """Security filter configuration."""
    sensitive_terms: List[str] = None
    
    def __post_init__(self):
        if self.sensitive_terms is None:
            self.sensitive_terms = [
                "Project Falcon",
                "Internal-Only", 
                "Confidential",
                "SECRET",
                "CLASSIFIED"
            ]


# Default configurations
LLM_CONFIG = LLMConfig()
AGENT_CONFIG = AgentConfig()
SECURITY_CONFIG = SecurityConfig()


def get_api_key() -> str:
    """Get Hugging Face API key from environment."""
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError(
            "HUGGINGFACE_API_KEY not set. "
            "Please create a .env file with your API key."
        )
    return api_key
