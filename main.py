#!/usr/bin/env python3
"""
Research Assistant Chatbot - Entry Point

An agentic AI chatbot that uses a ReAct workflow to autonomously
execute research tasks like generating company briefings.

Usage:
    python main.py
    
Example instructions:
    - "Generate a company briefing on Tesla in German"
    - "Get information about Apple and create a briefing"
    - "Search for news about Tesla and summarize"
"""
from modules.agent_framework import agentic_workflow


def main():
    """Run the Research Assistant Chatbot interactively."""
    print("\n" + "="*60)
    print("  RESEARCH ASSISTANT CHATBOT")
    print("  Powered by ReAct Agentic Workflow")
    print("="*60)
    print("\nAvailable tools: company lookup, web search, document")
    print("generation, translation, and security filtering.\n")
    
    instruction = input("Enter your instruction:\n> ")
    
    if not instruction.strip():
        print("No instruction provided. Exiting.")
        return
    
    result = agentic_workflow(instruction)
    
    print("\n" + "="*60)
    print("  FINAL OUTPUT")
    print("="*60)
    print(result)


if __name__ == "__main__":
    main()
