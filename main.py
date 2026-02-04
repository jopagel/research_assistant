# main.py
"""
Entry point for the Research Assistant Chatbot with agentic workflow.
"""
from modules.agent_framework import agentic_workflow

def main():
    print("Research Assistant Chatbot - Agentic Agent Workflow Demo")
    instruction = input("Enter your instruction (e.g. 'Generate a company briefing on Tesla in German'): ")
    result = agentic_workflow(instruction)
    print("\n--- Briefing Document ---\n")
    print(result)

if __name__ == "__main__":
    main()
