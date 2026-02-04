"""
Minimal agent framework for the Research Assistant Chatbot.
Uses a custom ReAct-style agent loop with LLM-based planning.
"""
import os
import json
import re
from modules.agent_tools import (
    get_company_info, mock_web_search, translate_document,
    generate_document, security_filter
)
from modules.llm_utils import hf_llm_generate
from dotenv import load_dotenv

load_dotenv()

# Define available tools as a dictionary
TOOLS = {
    "get_company_info": {
        "func": get_company_info,
        "description": "Get company info from internal DB. Input: company_name (string). Example: Tesla"
    },
    "mock_web_search": {
        "func": mock_web_search,
        "description": "Search for public products and partnerships. Input: company_name (string). Example: Tesla"
    },
    "translate_document": {
        "func": translate_document,
        "description": 'Translate document to target language. Input JSON: {"document": "text", "target_language": "German"}'
    },
    "generate_document": {
        "func": generate_document,
        "description": 'Generate briefing document. Input JSON: {"template": "briefing", "content_dict": {"key": "value"}}'
    },
    "security_filter": {
        "func": security_filter,
        "description": "Filter sensitive terms from document. Input: document (string)"
    }
}


def get_tools_description():
    """Generate a description of available tools for the LLM."""
    desc = []
    for name, tool in TOOLS.items():
        desc.append(f"- {name}: {tool['description']}")
    return "\n".join(desc)


def parse_agent_response(response):
    """Parse the agent's response to extract action and action input."""
    # Truncate response at first "Observation:" if model generates fake ones
    if "Observation:" in response:
        response = response.split("Observation:")[0]
    
    # Check for Final Answer first
    final_answer_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
    if final_answer_match:
        return {"type": "final", "answer": final_answer_match.group(1).strip()}
    
    # Look for Action: and Action Input: patterns
    action_match = re.search(r"Action:\s*(\w+)", response)
    action_input_match = re.search(r"Action Input:\s*(.+?)(?=\n|$)", response, re.DOTALL)
    
    if action_match:
        action = action_match.group(1).strip()
        action_input = action_input_match.group(1).strip() if action_input_match else ""
        return {"type": "action", "action": action, "input": action_input}
    return {"type": "unknown"}


def parse_tool_input(tool_input):
    """
    Robustly parse tool input that should be JSON.
    Handles common LLM output issues like missing quotes, single quotes, etc.
    """
    tool_input = tool_input.strip()
    
    # Try direct JSON parse first
    try:
        return json.loads(tool_input)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON object from the text (handles nested braces)
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', tool_input, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try fixing single quotes to double quotes
            fixed = json_str.replace("'", '"')
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass
    
    # Try to parse key-value pairs manually for simple cases
    kv_pattern = r'["\']?(\w+)["\']?\s*:\s*["\']?([^,}\n]+)["\']?'
    matches = re.findall(kv_pattern, tool_input)
    if matches:
        result = {}
        for key, value in matches:
            result[key] = value.strip().strip('"').strip("'")
        if result:
            return result
    
    return None


def execute_tool(tool_name, tool_input):
    """Execute a tool with the given input."""
    if tool_name not in TOOLS:
        available = ', '.join(TOOLS.keys())
        return f"Error: Tool '{tool_name}' not found. Available: {available}"
    
    try:
        tool_input = tool_input.strip()
        
        # For tools requiring JSON arguments
        if tool_name in ["translate_document", "generate_document"]:
            args = parse_tool_input(tool_input)
            
            if args is None:
                return f"Error: Could not parse input. Use JSON format: {{\"key\": \"value\"}}"
            
            if tool_name == "translate_document":
                doc = args.get("document", args.get("text", ""))
                lang = args.get("target_language", args.get("language", "English"))
                if not doc:
                    return "Error: Missing 'document' field in input"
                return str(TOOLS[tool_name]["func"](doc, lang))
            elif tool_name == "generate_document":
                template = args.get("template", "briefing")
                content = args.get("content_dict", args.get("content", {}))
                if isinstance(content, str):
                    parsed = parse_tool_input(content)
                    content = parsed if parsed else {"info": content}
                return str(TOOLS[tool_name]["func"](template, content))
        else:
            # Single argument tools - clean up the input
            clean_input = tool_input.strip().strip('"').strip("'")
            return str(TOOLS[tool_name]["func"](clean_input))
            
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"


def agentic_workflow(instruction):
    """
    ReAct-style agent loop: plans steps, calls tools dynamically, composes final document.
    """
    tools_desc = get_tools_description()
    
    react_prompt = f"""You are a research assistant agent. Complete tasks efficiently with minimal steps.

AVAILABLE TOOLS:
{tools_desc}

FORMAT (use exactly):
Thought: [brief reasoning]
Action: [tool_name]
Action Input: [input - use JSON for multi-param tools: {{"key": "value"}}]

For final response:
Thought: I have all the information needed.
Final Answer: [complete answer]

EFFICIENCY RULES:
- Use ONLY 1 action per response, then STOP
- Aim to complete in 2-4 steps total
- For company briefings: 1) get_company_info 2) generate_document or translate_document 3) Final Answer
- For translations: Pass full document content to translate_document
- When you have enough info, immediately give Final Answer

EXAMPLE - "Generate a briefing on Tesla":
Thought: I need company info first.
Action: get_company_info
Action Input: Tesla

[After receiving observation]
Thought: I have the info. Now I'll create the briefing document.
Action: generate_document
Action Input: {{"template": "briefing", "content_dict": {{"company_name": "Tesla", "industry": "EVs"}}}}

[After receiving observation]
Thought: I have all the information needed.
Final Answer: [the generated briefing]

Question: {instruction}
Thought:"""

    max_iterations = 10
    scratchpad = ""
    
    print("\n" + "="*50)
    print("AGENT STARTING")
    print("="*50)
    
    for i in range(max_iterations):
        current_prompt = react_prompt + scratchpad
        response = hf_llm_generate(current_prompt)
        
        print(f"\n--- Iteration {i+1} ---")
        print(f"LLM Response:\n{response}")
        
        parsed = parse_agent_response(response)
        
        if parsed["type"] == "final":
            print("\n" + "="*50)
            print("AGENT FINISHED")
            print("="*50)
            return parsed["answer"]
        
        elif parsed["type"] == "action":
            action = parsed["action"]
            action_input = parsed["input"]
            print(f"\nExecuting: {action}({action_input})")
            
            observation = execute_tool(action, action_input)
            obs_preview = observation[:200] + "..." if len(str(observation)) > 200 else observation
            print(f"Observation: {obs_preview}")
            
            # Add to scratchpad with clear separator
            scratchpad += f" {response}\nObservation: {observation}\n\nThought:"
        
        else:
            # Unknown response - nudge toward action or final answer
            scratchpad += f" {response}\n\nYou must either use a tool (Action + Action Input) or give a Final Answer.\nThought:"
    
    return "Agent reached maximum iterations. Please try a more specific instruction."
