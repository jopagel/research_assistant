"""
Research Assistant Chatbot - Modules Package

This package contains the core components:
- agent_framework: ReAct-style agent loop
- agent_tools: Tool implementations (company lookup, search, translate, etc.)
- llm_utils: LLM API wrapper for Hugging Face
- config: Configuration settings
"""

from modules.agent_framework import agentic_workflow
from modules.agent_tools import (
    get_company_info,
    mock_web_search,
    translate_document,
    generate_document,
    security_filter
)
from modules.llm_utils import hf_llm_generate

__all__ = [
    "agentic_workflow",
    "get_company_info",
    "mock_web_search", 
    "translate_document",
    "generate_document",
    "security_filter",
    "hf_llm_generate"
]
