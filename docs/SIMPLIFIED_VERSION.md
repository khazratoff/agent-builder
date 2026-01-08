# Simplified Multi-Agent System

This is the simplified version of the multi-agent system, focused on core learning concepts without advanced production features.

## What's Included

### Core Components

1. **BaseAgent** (`src/core/base_agent.py`)
   - Abstract base class for all agents
   - Defines interface: name, description, capabilities, execute()

2. **AgentRegistry** (`src/core/agent_registry.py`)
   - Simple singleton registry for agent discovery
   - `@AgentRegistry.register` decorator for registration

3. **AgentState** (`src/core/state.py`)
   - TypedDict defining the state flow

4. **Supervisor** (`src/core/supervisor.py`)
   - LangGraph StateGraph for routing requests to agents

### Example Agents

1. **FileOperationsAgent** (`src/agents/file_operations_agent.py`)
   - Read, write, list, delete, append files

2. **ResearchAgent** (`src/agents/research_agent.py`)
   - Web search, content summarization, information extraction

### Tools

- **File Tools** (`src/tools/file_tools.py`)
- **Research Tools** (`src/tools/research_tools.py`)

## What Was Removed

To keep the system simple and focused on learning, we removed:

- ❌ Advanced configuration management (pydantic settings)
- ❌ Structured logging system
- ❌ Retry and circuit breaker logic
- ❌ Thread safety locks (simple singleton now)
- ❌ Testing infrastructure (pytest)
- ❌ Production-ready error handling

## Project Structure

```
agent-builder/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── base_agent.py        # Abstract base class
│   │   ├── agent_registry.py    # Simple registry
│   │   ├── state.py             # State definition
│   │   └── supervisor.py        # LangGraph supervisor
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── file_operations_agent.py
│   │   └── research_agent.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── file_tools.py
│   │   └── research_tools.py
│   └── main.py                  # CLI application
├── examples/
│   └── add_custom_agent.py
├── docs/                        # Learning documentation
├── requirements.txt             # Minimal dependencies
├── .env.example
└── README.md

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### 3. Run the System

```bash
cd src && python main.py
```

## Adding a New Agent

It's simple - just 3 steps:

### 1. Create Your Agent File

Create `src/agents/my_agent.py`:

```python
from typing import List, Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry

@AgentRegistry.register
class MyAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.agent_executor = None
        super().__init__()

    @property
    def name(self) -> str:
        return "my_agent"

    @property
    def description(self) -> str:
        return "Description of what my agent does"

    @property
    def capabilities(self) -> List[str]:
        return ["capability1", "capability2"]

    def get_tools(self) -> List[BaseTool]:
        return []  # Add your tools here

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_input = state.get("user_input", "")

            # Your agent logic here
            result = self.llm.invoke(user_input)

            return {
                "agent_output": result.content,
                "current_agent": self.name
            }
        except Exception as e:
            return {
                "agent_output": f"Error: {str(e)}",
                "current_agent": self.name
            }
```

### 2. Register in `src/agents/__init__.py`

```python
from .my_agent import MyAgent

__all__ = ["FileOperationsAgent", "ResearchAgent", "MyAgent"]
```

### 3. Done!

Your agent is automatically available. The supervisor will route requests to it based on the description and capabilities.

## Key Learning Concepts

### 1. Registry Pattern
Agents self-register using a decorator, no manual configuration needed.

### 2. Strategy Pattern
Each agent implements the same interface but with different strategies.

### 3. State Management
LangGraph StateGraph manages state flow through the workflow.

### 4. Dynamic Routing
Supervisor uses LLM to intelligently select the right agent.

## Dependencies

Minimal set of dependencies:
- `langchain` - Agent framework
- `langchain-openai` - OpenAI integration
- `langgraph` - Workflow orchestration
- `openai` - API client
- `python-dotenv` - Environment variables
- `duckduckgo-search` - Web search for research agent

## Documentation

- [README.md](README.md) - Main overview
- [QUICKSTART.md](QUICKSTART.md) - Quick 5-minute guide
- [INSTALL.md](INSTALL.md) - Detailed installation
- [docs/TUTORIAL.md](docs/TUTORIAL.md) - Step-by-step tutorial
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Architecture details

## Philosophy

This version focuses on:
- **Simplicity** - Easy to understand core concepts
- **Learning** - Clear patterns and practices
- **Extensibility** - Simple to add new agents
- **Clarity** - Minimal abstractions

Perfect for:
- Learning AI agent programming
- Understanding LangGraph workflows
- Experimenting with agent design
- Building prototypes

## Need Production Features?

If you need advanced features like configuration management, logging, testing, and error recovery, those are available in a separate branch with comprehensive documentation.

For learning purposes, this simplified version is recommended!
