#!/usr/bin/env python3
"""
Research Assistant Chatbot - Gradio Web Interface

A simple web UI for interacting with the Research Assistant agent.
Run with: python app.py
"""
import gradio as gr
from io import StringIO
import sys

from modules.agent_framework import agentic_workflow
from modules.agent_tools import get_company_info, mock_web_search, security_filter


def run_agent(instruction: str, show_logs: bool = True) -> tuple[str, str]:
    """
    Run the agent and capture both result and logs.
    
    Args:
        instruction: Natural language instruction
        show_logs: Whether to capture and return logs
        
    Returns:
        Tuple of (final_result, execution_logs)
    """
    if not instruction.strip():
        return "Please enter an instruction.", ""
    
    # Capture stdout for logs
    old_stdout = sys.stdout
    sys.stdout = captured = StringIO()
    
    try:
        result = agentic_workflow(instruction)
    except Exception as e:
        result = f"Error: {e}"
    finally:
        sys.stdout = old_stdout
    
    logs = captured.getvalue() if show_logs else ""
    return result, logs


def get_company_preview(company_name: str) -> str:
    """Preview company info without running full agent."""
    if not company_name.strip():
        return "Enter a company name to preview."
    
    info = get_company_info(company_name)
    lines = [f"**{k.replace('_', ' ').title()}:** {v}" for k, v in info.items()]
    return "\n".join(lines)


def search_preview(company_name: str) -> str:
    """Preview web search results."""
    if not company_name.strip():
        return "Enter a company name to search."
    
    results = mock_web_search(company_name)
    return "\n".join(f"• {r}" for r in results)


def filter_text(text: str) -> str:
    """Run security filter on text."""
    if not text.strip():
        return "Enter text to filter."
    return security_filter(text)


# Example instructions
EXAMPLES = [
    ["Generate a company briefing on Tesla"],
    ["Generate a company briefing on Tesla in German"],
    ["Get information about Apple and search for recent news"],
    ["Create a briefing about Apple and translate to French"],
]


# Build Gradio interface
with gr.Blocks(title="Research Assistant Chatbot") as app:
    
    gr.Markdown("""
    # 🤖 Research Assistant Chatbot
    
    An agentic AI assistant that uses **ReAct workflow** to autonomously execute research tasks.
    
    The agent can:
    - 🏢 Look up company information
    - 🔍 Search for public news and partnerships  
    - 📄 Generate formatted briefing documents
    - 🌍 Translate documents to different languages
    - 🔒 Filter sensitive information
    """)
    
    with gr.Tab("💬 Chat with Agent"):
        with gr.Row():
            with gr.Column(scale=2):
                instruction_input = gr.Textbox(
                    label="Your Instruction",
                    placeholder="e.g., Generate a company briefing on Tesla in German",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("🚀 Run Agent", variant="primary")
                    clear_btn = gr.Button("🗑️ Clear")
                
                gr.Examples(
                    examples=EXAMPLES,
                    inputs=instruction_input,
                    label="Example Instructions"
                )
            
            with gr.Column(scale=1):
                show_logs = gr.Checkbox(label="Show execution logs", value=True)
        
        with gr.Row():
            with gr.Column():
                result_output = gr.Textbox(
                    label="📋 Agent Output",
                    lines=12
                )
            
            with gr.Column():
                logs_output = gr.Textbox(
                    label="📜 Execution Logs",
                    lines=12
                )
        
        submit_btn.click(
            fn=run_agent,
            inputs=[instruction_input, show_logs],
            outputs=[result_output, logs_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", ""),
            outputs=[instruction_input, result_output, logs_output]
        )
    
    with gr.Tab("🔧 Tool Playground"):
        gr.Markdown("### Test individual tools directly")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 🏢 Company Lookup")
                company_input = gr.Textbox(
                    label="Company Name",
                    placeholder="Tesla, Apple, etc."
                )
                company_btn = gr.Button("Look Up")
                company_output = gr.Markdown(label="Company Info")
                
                company_btn.click(
                    fn=get_company_preview,
                    inputs=company_input,
                    outputs=company_output
                )
            
            with gr.Column():
                gr.Markdown("#### 🔍 Web Search")
                search_input = gr.Textbox(
                    label="Company Name",
                    placeholder="Tesla, Apple, etc."
                )
                search_btn = gr.Button("Search")
                search_output = gr.Markdown(label="Search Results")
                
                search_btn.click(
                    fn=search_preview,
                    inputs=search_input,
                    outputs=search_output
                )
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("#### 🔒 Security Filter")
                filter_input = gr.Textbox(
                    label="Text to Filter",
                    placeholder="Enter text with sensitive terms like 'Project Falcon' or 'Confidential'",
                    lines=3
                )
                filter_btn = gr.Button("Apply Filter")
                filter_output = gr.Textbox(label="Filtered Output", lines=3)
                
                filter_btn.click(
                    fn=filter_text,
                    inputs=filter_input,
                    outputs=filter_output
                )
    
    with gr.Tab("ℹ️ About"):
        gr.Markdown("""
        ## About This Project
        
        This Research Assistant Chatbot demonstrates an **agentic AI workflow** using the 
        ReAct (Reasoning + Acting) pattern.
        
        ### Architecture
        
        ```
        User Instruction → ReAct Agent → LLM Planning → Tool Execution → Final Output
        ```
        
        ### Available Tools
        
        | Tool | Description |
        |------|-------------|
        | `get_company_info` | Retrieve company data from mock database |
        | `mock_web_search` | Simulate web search for news |
        | `translate_document` | Translate text using LLM |
        | `generate_document` | Create formatted briefings |
        | `security_filter` | Redact sensitive information |
        
        ### Technology Stack
        
        - **LLM**: Llama-3.2-3B-Instruct via Hugging Face Inference API
        - **Agent Framework**: Custom ReAct implementation
        - **UI**: Gradio
        
        ### Source Code
        
        [GitHub Repository](https://github.com/jopagel/research_assistant)
        """)


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
