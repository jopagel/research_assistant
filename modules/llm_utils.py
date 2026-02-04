"""
LLM utility for agentic workflow.
Uses Hugging Face Inference API with open-source models.
"""
import os
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


def _mock_llm_response(prompt: str, iteration: int = 0) -> str:
    """
    Generate mock LLM responses for testing without API access.
    Simulates a realistic ReAct agent conversation.
    """
    # Detect which iteration we're on based on prompt content
    if "Observation:" not in prompt:
        # First iteration - call get_company_info
        return """I need to get company information first.
Action: get_company_info
Action Input: Tesla"""
    
    elif prompt.count("Observation:") == 1:
        # Second iteration - we have company info, generate document or finish
        if "German" in prompt or "translate" in prompt.lower():
            return """I have the company info. Now I need to generate a briefing and translate it.
Action: generate_document
Action Input: {"template": "briefing", "content_dict": {"company_name": "Tesla", "industry": "Electric Vehicles"}}"""
        else:
            return """I have gathered the information. Now I will provide the final answer.
Final Answer: Tesla is an Electric Vehicles & Clean Energy company founded in 2003. The CEO is Elon Musk and the headquarters are in Austin, Texas. Key products include Model S, Model 3, Model X, Model Y, and Cybertruck. The company is a leader in electric vehicle manufacturing and sustainable energy solutions."""
    
    elif prompt.count("Observation:") == 2:
        # Third iteration - translate if needed or finish
        if "German" in prompt:
            return """Now I need to translate the document to German.
Action: translate_document
Action Input: {"document": "Tesla Company Briefing...", "target_language": "German"}"""
        else:
            return """I have gathered the information. Now I will provide the final answer.
Final Answer: Tesla is an Electric Vehicles & Clean Energy company founded in 2003. The CEO is Elon Musk and the headquarters are in Austin, Texas. Key products include Model S, Model 3, Model X, Model Y, and Cybertruck."""
    
    else:
        # Final iteration - always finish
        return """I have gathered the information. Now I will provide the final answer.
Final Answer: Based on the research, Tesla is a leading Electric Vehicles & Clean Energy company founded in 2003 by Elon Musk. Headquartered in Austin, Texas, Tesla produces innovative electric vehicles including the Model S, Model 3, Model X, Model Y, and Cybertruck."""


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
    # Check for mock mode (for testing without API)
    if os.getenv("USE_MOCK_LLM", "").lower() == "true":
        return _mock_llm_response(prompt)
    
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
