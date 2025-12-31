# Multi-Agent System with LangGraph

A flexible, OOP-based multi-agent system built with LangChain and LangGraph. This system features a supervisor that intelligently routes user requests to specialized agents, with an architecture designed for easy extensibility.

## 🌟 Features

- **Intelligent Routing**: Supervisor automatically selects the best agent for each task
- **Plug-and-Play Architecture**: Add new agents without modifying core code
- **OOP Design**: Clean, modular design with base classes and interfaces
- **LangGraph StateGraph**: Explicit workflow control with state management
- **Agent Registry**: Automatic agent discovery and registration
- **Interactive CLI**: User-friendly command-line interface
- **Comprehensive Examples**: Learn by example with working code

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          User Input                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor (LangGraph)                   │
│  • Analyzes request                                         │
│  • Queries agent registry                                   │
│  • Routes to appropriate agent                              │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Research   │  │    File      │  │  Your Custom │
│    Agent     │  │  Operations  │  │    Agent     │
│              │  │    Agent     │  │              │
│ • Web search │  │ • Read files │  │ • Custom     │
│ • Summarize  │  │ • Write files│  │   tools      │
│ • Analyze    │  │ • List files │  │ • Custom     │
│              │  │              │  │   logic      │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Installation

1. **Clone or navigate to the repository**:
   ```bash
   cd agent-builder
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the system**:
   ```bash
   python src/main.py
   ```

## 📖 Usage

### Interactive Mode

Once the system starts, you can interact with it naturally:

```
You: Search for information about LangGraph

🎯 Supervisor selected: research
⚙️  Executing research agent...
[Agent performs web search and returns results]

You: Save the summary to a file called langgraph_info.txt

🎯 Supervisor selected: file_operations
⚙️  Executing file_operations agent...
[Agent saves the file]
```

### Available Commands

- `/help` - Show help information
- `/agents` - List all registered agents
- `/clear` - Clear the screen
- `/exit` - Exit the application

## 🤖 Built-in Agents

### 1. Research Agent
**Capabilities**: Web search, content summarization, information extraction, topic analysis

**Example requests**:
- "Search for the latest LangChain documentation"
- "Summarize this article: [paste content]"
- "What is the definition of multi-agent systems?"

### 2. File Operations Agent
**Capabilities**: Read, write, list, delete, and append to files

**Example requests**:
- "Create a file called notes.txt with 'Hello World'"
- "Read the contents of data/config.json"
- "List all files in the current directory"

## ➕ Adding Custom Agents

Adding a new agent is simple! Follow these steps:

### Step 1: Create Your Agent Class

```python
from typing import List, Dict, Any
from langchain.tools import tool, BaseTool
from src.core.base_agent import BaseAgent
from src.core.agent_registry import AgentRegistry

# Define your tools
@tool
def my_custom_tool(input_data: str) -> str:
    """Your tool description."""
    # Tool implementation
    return "result"

# Create your agent
@AgentRegistry.register  # This registers the agent automatically!
class MyCustomAgent(BaseAgent):

    @property
    def name(self) -> str:
        return "my_custom_agent"

    @property
    def description(self) -> str:
        return "Description of what your agent does"

    @property
    def capabilities(self) -> List[str]:
        return ["capability1", "capability2"]

    def get_tools(self) -> List[BaseTool]:
        return [my_custom_tool]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Your execution logic here
        user_input = state.get("user_input", "")
        # Process and return result
        return {
            "agent_output": "Your result",
            "current_agent": self.name
        }
```

### Step 2: Import Your Agent

Add your agent file to `src/agents/` and import it in `src/agents/__init__.py`:

```python
from src.agents.my_custom_agent import MyCustomAgent
```

### Step 3: Run the System

That's it! Your agent is now automatically available in the system. The supervisor will route appropriate requests to it.

See `examples/add_custom_agent.py` for a complete working example.

## 📁 Project Structure

```
agent-builder/
├── src/
│   ├── core/                      # Core framework
│   │   ├── base_agent.py          # BaseAgent abstract class
│   │   ├── agent_registry.py      # Agent registration system
│   │   ├── state.py               # State schema
│   │   └── supervisor.py          # LangGraph supervisor
│   ├── agents/                    # Agent implementations
│   │   ├── file_operations_agent.py
│   │   └── research_agent.py
│   ├── tools/                     # Reusable tools
│   │   ├── file_tools.py
│   │   └── research_tools.py
│   └── main.py                    # Application entry point
├── docs/                          # Documentation
│   ├── README.md                  # This file
│   ├── TUTORIAL.md                # Step-by-step tutorial
│   └── ARCHITECTURE.md            # Architecture details
├── examples/                      # Examples
│   └── add_custom_agent.py        # Custom agent example
├── requirements.txt               # Dependencies
├── .env.example                   # Environment template
└── .gitignore                     # Git ignore rules
```

## 🎓 Learning Resources

- **[TUTORIAL.md](TUTORIAL.md)** - Detailed step-by-step guide for building custom agents
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Deep dive into the system architecture
- **[examples/](../examples/)** - Working code examples

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for LLM operations
- `TAVILY_API_KEY` - Optional, for enhanced web search

### Model Selection

By default, the system uses `gpt-4o`. You can change this in:
- `src/core/supervisor.py` - For supervisor routing
- Individual agent files - For agent execution

## 🛠️ Development

### Running Tests

```bash
# Test individual agents
python -m src.agents.research_agent

# Test the custom agent example
python examples/add_custom_agent.py
```

### Debugging

Set `verbose=True` in agent executors to see detailed execution logs.

## 🤝 Contributing

Contributions are welcome! Some ideas:

- Add new agents (Email, Database, API, etc.)
- Enhance existing tools
- Improve routing logic
- Add tests
- Improve documentation

## 📝 License

This project is for educational purposes. Feel free to use and modify as needed.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://langchain.com/) - Framework for LLM applications
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Graph-based workflows
- [OpenAI](https://openai.com/) - LLM provider

## 📧 Support

For questions or issues:
1. Check the [TUTORIAL.md](TUTORIAL.md) for detailed guidance
2. Review [examples/](../examples/) for working code
3. Consult [ARCHITECTURE.md](ARCHITECTURE.md) for design details

---

**Happy agent building! 🤖**
