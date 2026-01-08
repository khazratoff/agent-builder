# Quick Start Guide

Get up and running with the multi-agent system in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Step-by-Step Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- LangChain (agent framework)
- LangGraph (workflow engine)
- OpenAI (LLM provider)
- DuckDuckGo Search (web search)
- Python-dotenv (environment management)

### 2. Set Up Environment

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

**Note**: Keep this file secure and never commit it to version control!

### 3. Run the System

```bash
python src/main.py
```

You should see:

```
╔══════════════════════════════════════════════════════════════╗
║          🤖 Multi-Agent System with LangGraph 🤖             ║
║          A Flexible, OOP-Based Agent Architecture           ║
╚══════════════════════════════════════════════════════════════╝

🔧 Initializing multi-agent system...
✓ Registered agent: file_operations
✓ Registered agent: research
✓ Supervisor workflow built with 2 agents

✅ System ready! Type /help for commands or enter your request.
```

### 4. Try These Examples

Once the system is running, try these requests:

#### Research Example
```
You: What is LangGraph and how does it work?
```

The supervisor will route this to the Research Agent, which will search for information and provide a comprehensive answer.

#### File Operations Example
```
You: Create a file called hello.txt with the content "Hello, World!"
```

The supervisor will route this to the File Operations Agent, which will create the file.

#### Combined Example
```
You: Search for information about multi-agent systems and save it to agents_info.txt
```

The supervisor will coordinate both agents to complete the task!

### 5. Explore Commands

Try these built-in commands:

```bash
/help      # Show available commands
/agents    # List all registered agents
/clear     # Clear the screen
/exit      # Exit the application
```

## What's Next?

### Learn the Architecture

Read the [Tutorial](docs/TUTORIAL.md) to understand:
- How the supervisor routes requests
- How agents are structured
- How the registry pattern works
- State management with LangGraph

### Build Your First Agent

Follow [examples/add_custom_agent.py](examples/add_custom_agent.py) to:
1. Create a new Math Agent
2. Implement calculation tools
3. Register it with the system
4. Test it with the supervisor

Run the example:
```bash
python examples/add_custom_agent.py
```

### Explore the Code

Check out these key files:

1. **[src/core/base_agent.py](src/core/base_agent.py)** - Abstract base class for all agents
2. **[src/core/agent_registry.py](src/core/agent_registry.py)** - Registry pattern implementation
3. **[src/core/supervisor.py](src/core/supervisor.py)** - LangGraph supervisor workflow
4. **[src/agents/research_agent.py](src/agents/research_agent.py)** - Example agent implementation

### Read the Docs

- **[README.md](README.md)** - Project overview and quick reference
- **[docs/TUTORIAL.md](docs/TUTORIAL.md)** - Step-by-step guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Deep dive into design
- **[docs/README.md](docs/README.md)** - Comprehensive documentation

## Troubleshooting

### "OPENAI_API_KEY not found"

Make sure you:
1. Created the `.env` file
2. Added your actual API key
3. Saved the file

### "Module not found" errors

Run the installation again:
```bash
pip install -r requirements.txt
```

Make sure you're in the project root directory.

### "No agents are registered"

This usually means an import error. Check:
1. All files in `src/agents/` are valid Python
2. Agents are imported in `src/agents/__init__.py`
3. No syntax errors in your agent code

### Agent not being selected

The supervisor uses the agent's `description` and `capabilities` to make routing decisions. Make sure:
1. Your agent's description clearly states what it does
2. Capabilities include relevant keywords
3. Test with explicit requests matching the agent's purpose

## Common Tasks

### Adding a New Tool

1. Create the tool function:
```python
from langchain.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description."""
    return "result"
```

2. Add to an agent's `get_tools()` method:
```python
def get_tools(self) -> List[BaseTool]:
    return [existing_tool, my_tool]
```

### Adding a New Agent

1. Create agent file in `src/agents/`
2. Use `@AgentRegistry.register` decorator
3. Import in `src/agents/__init__.py`
4. Restart the application

See [docs/TUTORIAL.md](docs/TUTORIAL.md) for detailed instructions.

### Changing the LLM Model

Edit the model name in:
- `src/core/supervisor.py` (line ~20) - for routing
- Individual agent files - for agent execution

Available models:
- `gpt-4o` (default, most capable)
- `gpt-4o-mini` (faster, cheaper)
- `gpt-4-turbo` (previous generation)

## Tips for Success

1. **Start Simple**: Try the built-in agents first
2. **Read the Code**: The codebase is well-commented and educational
3. **Experiment**: Modify existing agents to learn how they work
4. **Ask Questions**: The architecture is designed to be understandable
5. **Build Incrementally**: Start with simple agents, add complexity gradually

## Project Structure

```
agent-builder/
├── src/
│   ├── core/                  # Framework
│   │   ├── base_agent.py      # Base class
│   │   ├── agent_registry.py  # Registry
│   │   ├── state.py           # State schema
│   │   └── supervisor.py      # Workflow
│   ├── agents/                # Agents
│   │   ├── research_agent.py
│   │   └── file_operations_agent.py
│   ├── tools/                 # Tools
│   │   ├── research_tools.py
│   │   └── file_tools.py
│   └── main.py               # Entry point
├── docs/                      # Documentation
├── examples/                  # Examples
└── requirements.txt          # Dependencies
```

## Need Help?

1. Check the [Tutorial](docs/TUTORIAL.md)
2. Review [examples/](examples/)
3. Read [ARCHITECTURE.md](docs/ARCHITECTURE.md)
4. Look at existing agent implementations

## Ready to Learn More?

Head over to the [Tutorial](docs/TUTORIAL.md) to dive deeper into:
- LangGraph StateGraph workflows
- Design patterns used in the system
- Advanced agent patterns
- Testing strategies
- Best practices

---

**Happy agent building! 🤖**
