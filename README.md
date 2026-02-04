# Research Assistant Chatbot

An agentic AI chatbot that uses a ReAct (Reasoning + Acting) workflow to autonomously execute research tasks. Given natural language instructions like *"Generate a company briefing on Tesla in German"*, it plans steps, calls tools, and composes final documents.

## Features

- 🧠 **Agentic Workflow**: ReAct-style planning with dynamic tool selection
- 🔧 **Tool Integration**: Company lookup, web search, document generation, translation, security filtering
- 🌍 **Multi-language Support**: Translate outputs to German, French, Spanish, etc.
- 🔒 **Security Filter**: Redacts sensitive terms before output
- 📊 **Evaluation Suite**: Notebooks for testing and performance analysis

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  User Request   │────▶│  ReAct Agent │────▶│  LLM (HF)   │
└─────────────────┘     └──────┬───────┘     └─────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
             ┌────────────┐        ┌────────────┐
             │   Tools    │        │  Security  │
             │ - company  │        │   Filter   │
             │ - search   │        └────────────┘
             │ - translate│
             │ - generate │
             └────────────┘
```

## Project Structure

```
research_assistant/
├── main.py                     # Entry point
├── modules/
│   ├── agent_framework.py      # ReAct agent loop & tool execution
│   ├── agent_tools.py          # Tool implementations
│   └── llm_utils.py            # Hugging Face API wrapper
├── evaluation_notebook.ipynb   # Performance evaluation (3 test cases)
├── synthetic_test_data.ipynb   # Generate 10 company profiles
├── test_plan.md                # Comprehensive test strategy
└── requirements.txt
```

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/jopagel/research_assistant.git
cd research_assistant

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

> Get your API key from [Hugging Face Settings](https://huggingface.co/settings/tokens)

### 3. Run the Agent

```bash
python main.py
```

Example output:
```
==================================================
AGENT STARTING
==================================================

--- Iteration 1 ---
Thought: I need to get company information first.
Action: get_company_info
Action Input: Tesla

Observation: {'name': 'Tesla', 'industry': 'Electric Vehicles'...}

--- Iteration 2 ---
Thought: Now I'll generate the briefing document...
...

==================================================
AGENT FINISHED
==================================================
```

## Available Tools

| Tool | Description | Input |
|------|-------------|-------|
| `get_company_info` | Retrieve company data from internal DB | Company name |
| `mock_web_search` | Search for public news/partnerships | Company name |
| `generate_document` | Create formatted briefing document | Template + content |
| `translate_document` | Translate text to target language | Document + language |
| `security_filter` | Redact sensitive terms | Text |

## Evaluation

Run the evaluation notebook to test the agent on 3 scenarios:

1. **Basic Briefing**: Generate Tesla briefing in German
2. **Security Test**: Handle sensitive defense company data
3. **Multi-step**: Apple briefing with news search + French translation

```bash
jupyter notebook evaluation_notebook.ipynb
```

## Model

Uses **meta-llama/Llama-3.2-3B-Instruct** via Hugging Face Inference API.

## License

MIT
