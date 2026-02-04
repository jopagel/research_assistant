"""
LLM utility for agentic workflow.
Uses Hugging Face Inference API with open-source models.
"""
from typing import Optional
from huggingface_hub import InferenceClient

from modules.config import LLM_CONFIG, get_api_key


# Singleton client instance
_client: Optional[InferenceClient] = None


def get_client() -> InferenceClient:
    """Get or create the Hugging Face Inference client."""
    global _client
    if _client is None:
        _client = InferenceClient(token=get_api_key())
    return _client


def hf_llm_generate(
    prompt: str,
    model: Optional[str] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None
) -> str:
    """
    Call Hugging Face Inference API for chat-based LLM generation.
    
    Args:
        prompt: The input prompt for the LLM
        model: Model name (defaults to config)
        max_tokens: Maximum tokens to generate (defaults to config)
        temperature: Sampling temperature (defaults to config)
    
    Returns:
        Generated text response
    
    Raises:
        ValueError: If API key is not set
        Exception: If API call fails
    """
    client = get_client()
    
    model = model or LLM_CONFIG.model
    max_tokens = max_tokens or LLM_CONFIG.max_tokens
    temperature = temperature or LLM_CONFIG.temperature
    
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return completion.choices[0].message.content
    except Exception as e:
        raise Exception(f"LLM generation failed: {e}")
