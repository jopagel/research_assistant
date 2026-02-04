"""
Module for running model inference for the GenAI/LLM take-home test.
"""
def run_inference(processed_data):
    """
    Simulates LLM inference by generating mock responses.
    Args:
        processed_data (list): List of tokenized samples.
    Returns:
        list: List of model responses.
    """
    print("Running inference...")
    results = []
    for tokens in processed_data:
        # Simulate a response (in reality, call an LLM API)
        response = f"Response to: {' '.join(tokens)}"
        results.append(response)
    return results
