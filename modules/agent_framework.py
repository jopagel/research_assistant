"""
Agent Framework for the Research Assistant Chatbot.

Implements a ReAct-style (Reasoning + Acting) agent loop that:
1. Receives natural language instructions
2. Plans steps using LLM reasoning
3. Executes tools to gather information
4. Composes final responses

The agent supports tools for company lookup, web search, document
generation, translation, and security filtering.
"""
import json
import re
from typing import Dict, Any, Optional, Callable

from dotenv import load_dotenv

from modules.agent_tools import (
    get_company_info, mock_web_search, translate_document,
    generate_document, security_filter
)
from modules.llm_utils import hf_llm_generate
from modules.config import AGENT_CONFIG

load_dotenv()


# Type alias for tool definitions
ToolDef = Dict[str, Any]


# Available tools registry
TOOLS: Dict[str, ToolDef] = {
    "get_company_info": {
        "func": get_company_info,
        "description": "Get company info from internal DB. Input: company_name (string). Example: Tesla",
        "requires_json": False
    },
    "mock_web_search": {
        "func": mock_web_search,
        "description": "Search for public products and partnerships. Input: company_name (string). Example: Tesla",
        "requires_json": False
    },
    "translate_document": {
        "func": translate_document,
        "description": 'Translate document to target language. Input JSON: {"document": "text", "target_language": "German"}',
        "requires_json": True
    },
    "generate_document": {
        "func": generate_document,
        "description": 'Generate briefing document. Input JSON: {"template": "briefing", "content_dict": {"key": "value"}}',
        "requires_json": True
    },
    "security_filter": {
        "func": security_filter,
        "description": "Filter sensitive terms from document. Input: document (string)",
        "requires_json": False
    }
}


def get_tools_description() -> str:
    """Generate a formatted description of available tools for the LLM prompt."""
    return "\n".join(
        f"- {name}: {tool['description']}"
        for name, tool in TOOLS.items()
    )


def parse_agent_response(response: str) -> Dict[str, Any]:
    """
    Parse the agent's response to extract action and action input.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Dictionary with 'type' key and relevant data:
        - {"type": "final", "answer": str} for final answers
        - {"type": "action", "action": str, "input": str} for tool calls
        - {"type": "unknown"} if unparseable
    """
    # Truncate at first "Observation:" if model hallucinates
    if "Observation:" in response:
        response = response.split("Observation:")[0]
    
    # Check for Final Answer
    final_match = re.search(r"Final Answer:\s*(.+)", response, re.DOTALL)
    if final_match:
        return {"type": "final", "answer": final_match.group(1).strip()}
    
    # Check for Action + Action Input
    action_match = re.search(r"Action:\s*(\w+)", response)
    input_match = re.search(r"Action Input:\s*(.+?)(?=\n|$)", response, re.DOTALL)
    
    if action_match:
        return {
            "type": "action",
            "action": action_match.group(1).strip(),
            "input": input_match.group(1).strip() if input_match else ""
        }
    
    return {"type": "unknown"}


def parse_tool_input(tool_input: str) -> Optional[Dict[str, Any]]:
    """
    Robustly parse tool input that should be JSON.
    
    Handles common LLM output issues:
    - Missing quotes around keys
    - Single quotes instead of double quotes
    - Extra text before/after JSON
    
    Args:
        tool_input: Raw input string from LLM
        
    Returns:
        Parsed dictionary or None if parsing fails
    """
    tool_input = tool_input.strip()
    
    # Try direct JSON parse
    try:
        return json.loads(tool_input)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON object from text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', tool_input, re.DOTALL)
    if json_match:
        json_str = json_match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try fixing single quotes
            try:
                return json.loads(json_str.replace("'", '"'))
            except json.JSONDecodeError:
                pass
    
    # Try manual key-value extraction
    kv_pattern = r'["\']?(\w+)["\']?\s*:\s*["\']?([^,}\n]+)["\']?'
    matches = re.findall(kv_pattern, tool_input)
    if matches:
        return {key: value.strip().strip('"\'') for key, value in matches}
    
    return None


def execute_tool(tool_name: str, tool_input: str) -> str:
    """
    Execute a tool by name with the given input.
    
    Args:
        tool_name: Name of the tool to execute
        tool_input: Input string (may be JSON for some tools)
        
    Returns:
        Tool output as string, or error message
    """
    if tool_name not in TOOLS:
        available = ', '.join(TOOLS.keys())
        return f"Error: Tool '{tool_name}' not found. Available: {available}"
    
    tool = TOOLS[tool_name]
    tool_input = tool_input.strip()
    
    try:
        if tool.get("requires_json"):
            args = parse_tool_input(tool_input)
            if args is None:
                return 'Error: Could not parse input. Use JSON: {"key": "value"}'
            
            if tool_name == "translate_document":
                doc = args.get("document", args.get("text", ""))
                lang = args.get("target_language", args.get("language", "English"))
                if not doc:
                    return "Error: Missing 'document' field"
                return str(tool["func"](doc, lang))
            
            elif tool_name == "generate_document":
                template = args.get("template", "briefing")
                content = args.get("content_dict", args.get("content", {}))
                if isinstance(content, str):
                    content = parse_tool_input(content) or {"info": content}
                return str(tool["func"](template, content))
        else:
            # Single argument - clean quotes
            clean_input = tool_input.strip('"\'')
            return str(tool["func"](clean_input))
            
    except Exception as e:
        return f"Error executing {tool_name}: {e}"


def _build_prompt(instruction: str, tools_desc: str) -> str:
    """Build the ReAct prompt for the agent."""
    return f"""You are a research assistant agent. Complete tasks efficiently with minimal steps.

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


def agentic_workflow(
    instruction: str,
    max_iterations: Optional[int] = None,
    verbose: Optional[bool] = None
) -> str:
    """
    Execute the ReAct-style agent loop.
    
    Given a natural language instruction, the agent will:
    1. Plan the required steps
    2. Call tools as needed
    3. Compose and return a final response
    
    Args:
        instruction: Natural language task description
        max_iterations: Maximum loop iterations (defaults to config)
        verbose: Whether to print progress (defaults to config)
        
    Returns:
        Final answer string from the agent
    """
    max_iterations = max_iterations or AGENT_CONFIG.max_iterations
    verbose = verbose if verbose is not None else AGENT_CONFIG.verbose
    
    tools_desc = get_tools_description()
    react_prompt = _build_prompt(instruction, tools_desc)
    scratchpad = ""
    
    if verbose:
        print("\n" + "="*50)
        print("AGENT STARTING")
        print("="*50)
    
    for i in range(max_iterations):
        current_prompt = react_prompt + scratchpad
        response = hf_llm_generate(current_prompt)
        
        if verbose:
            print(f"\n--- Iteration {i+1} ---")
            print(f"LLM Response:\n{response}")
        
        parsed = parse_agent_response(response)
        
        if parsed["type"] == "final":
            if verbose:
                print("\n" + "="*50)
                print("AGENT FINISHED")
                print("="*50)
            return parsed["answer"]
        
        elif parsed["type"] == "action":
            action = parsed["action"]
            action_input = parsed["input"]
            
            if verbose:
                print(f"\nExecuting: {action}({action_input})")
            
            observation = execute_tool(action, action_input)
            
            if verbose:
                preview = observation[:200] + "..." if len(observation) > 200 else observation
                print(f"Observation: {preview}")
            
            scratchpad += f" {response}\nObservation: {observation}\n\nThought:"
        
        else:
            scratchpad += f" {response}\n\nYou must use a tool or give Final Answer.\nThought:"
    
    return "Agent reached maximum iterations. Please try a more specific instruction."
