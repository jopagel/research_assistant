"""
LLM utility for agentic workflow.
Uses Hugging Face Inference API with open-source models.
"""
import os
from huggingface_hub import InferenceClient

def hf_llm_generate(prompt):
    """Call Hugging Face Inference API for chat-based LLM generation.
    
    Uses open-source models via Hugging Face's serverless inference.
    """
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        raise ValueError("HUGGINGFACE_API_KEY not set in environment.")
    
    client = InferenceClient(token=api_key)
    
    # Use a capable open-source model
    model = "meta-llama/Llama-3.2-3B-Instruct"
    
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        max_tokens=512
    )
    
    return completion.choices[0].message.content
