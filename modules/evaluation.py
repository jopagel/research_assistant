"""
Module for evaluating results for the GenAI/LLM take-home test.
"""
def evaluate(results):
    """
    Evaluates and prints model responses.
    Args:
        results (list): List of model responses.
    """
    print("Evaluating results...")
    for i, r in enumerate(results, 1):
        print(f"{i}. {r}")
    print(f"Total responses: {len(results)}")
