# Multi-Agent System Builder

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-latest-green.svg)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-latest-orange.svg)](https://langchain-ai.github.io/langgraph/)

A flexible, OOP-based multi-agent system built with **LangChain** and **LangGraph** for learning and building AI agent applications. Features intelligent supervisor routing, easy agent extensibility, and a clean modular architecture.

## ✨ What You'll Learn

This project demonstrates:
- 🎯 **LangGraph StateGraph workflows** for agent orchestration
- 🏗️ **Design patterns** (Registry, Strategy, Command, Factory)
- 🔌 **Plug-and-play architecture** for adding agents
- 🤖 **Multi-agent coordination** with supervisor pattern
- 📚 **Production-ready code structure** and best practices

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Add your OpenAI API key to .env
OPENAI_API_KEY=your_key_here
```

### 3. Run the System

```bash
python src/main.py
```

### 4. Try It Out

```
You: Search for information about LangGraph
🎯 Supervisor selected: research
⚙️  Executing research agent...
[Results appear...]

You: Save that to a file called langgraph_notes.txt
🎯 Supervisor selected: file_operations
⚙️  Executing file_operations agent...
✅ File saved successfully!
```

## 🏛️ Architecture

The system has a clean three-layer architecture:

```
User Interface (CLI)
        ↓
Supervisor (LangGraph StateGraph)
        ↓
Agents (File Operations, Research, Custom...)
        ↓
Tools (Web search, File I/O, etc.)
```

### Key Components

- **BaseAgent**: Abstract base class all agents inherit from
- **AgentRegistry**: Singleton managing agent discovery
- **Supervisor**: LangGraph workflow that routes requests
- **Tools**: Reusable @tool decorated functions

## 🤖 Built-in Agents

### Research Agent
- Web search using DuckDuckGo
- Content summarization
- Information extraction
- Topic analysis

### File Operations Agent
- Read and write files
- List directory contents
- Delete files
- Append to files

## ➕ Adding Your Own Agent

It's incredibly easy! Just 3 steps:

### 1. Create Your Agent

```python
from src.core.base_agent import BaseAgent
from src.core.agent_registry import AgentRegistry

@AgentRegistry.register  # This decorator does the magic!
class WeatherAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return "Provides weather information and forecasts"

    @property
    def capabilities(self) -> List[str]:
        return ["weather", "forecast", "temperature"]

    def get_tools(self) -> List[BaseTool]:
        return [get_weather, get_forecast]

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Your implementation
        return {"agent_output": "Weather result"}
```

### 2. Register It

Add to `src/agents/__init__.py`:

```python
from src.agents.weather_agent import WeatherAgent
```

### 3. Done!

Your agent is now automatically available. The supervisor will route weather-related requests to it!

## 📚 Documentation

- **[docs/README.md](docs/README.md)** - Comprehensive guide with architecture overview
- **[docs/TUTORIAL.md](docs/TUTORIAL.md)** - Step-by-step tutorial for building custom agents
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Deep dive into system design
- **[examples/](examples/)** - Working code examples

## 📁 Project Structure

```
agent-builder/
├── src/
│   ├── core/              # Framework (base classes, registry, supervisor)
│   ├── agents/            # Agent implementations
│   ├── tools/             # Reusable tools
│   └── main.py            # CLI application
├── docs/                  # Documentation
├── examples/              # Example code
├── requirements.txt       # Dependencies
└── .env.example          # Environment template
```

## 🎓 Learning Path

1. **Start Here**: Run the system and try different requests
2. **Understand**: Read [docs/TUTORIAL.md](docs/TUTORIAL.md) to understand the architecture
3. **Explore**: Look at the built-in agents in `src/agents/`
4. **Build**: Follow [examples/add_custom_agent.py](examples/add_custom_agent.py) to create your own agent
5. **Master**: Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for advanced patterns

## 🛠️ Tech Stack

- **[LangChain](https://langchain.com/)** - Agent framework and tools
- **[LangGraph](https://langchain-ai.github.io/langgraph/)** - State graph workflows
- **[OpenAI GPT-4](https://openai.com/)** - LLM for reasoning and routing
- **Python 3.8+** - Implementation language

## 🎯 Use Cases

This architecture is perfect for:
- ✅ Learning agent programming concepts
- ✅ Building multi-agent applications
- ✅ Prototyping AI agent systems
- ✅ Understanding LangGraph workflows
- ✅ Experimenting with agent coordination

## 🔧 Advanced Features

- **Dynamic Routing**: Supervisor intelligently selects agents based on request
- **State Management**: LangGraph state flows through the workflow
- **Memory**: MemorySaver checkpointer for conversation persistence
- **Extensibility**: Multiple extension points (agents, tools, routing)
- **Type Safety**: TypedDict state and abstract base classes

## 🤝 Contributing Ideas

Want to extend the system? Try adding:
- 📧 Email agent (send, read, manage emails)
- 🗄️ Database agent (query, insert, update data)
- 🌐 API agent (call external APIs)
- 📊 Data analysis agent (pandas, visualization)
- 📅 Calendar agent (schedule, reminders)

## 📖 Example Output

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

You: What is LangGraph?

============================================================
🎯 Supervisor selected: research
⚙️  Executing research agent...

✅ Task completed by research agent

============================================================
Result:
LangGraph is a library for building stateful, multi-actor
applications with LLMs. It extends LangChain with the ability
to create cyclical graphs for complex agent workflows...
============================================================
```

## 🐛 Troubleshooting

**Agent not being selected?**
- Check the agent's `description` property
- Verify `capabilities` include relevant keywords
- Test the `can_handle()` method

**Import errors?**
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're running from the project root

**OpenAI API errors?**
- Verify your API key is set in `.env`
- Check you have credits in your OpenAI account

## 📄 License

MIT License - Feel free to use for learning and building!

## 🙏 Acknowledgments

This project is built for educational purposes to demonstrate modern AI agent architecture patterns using LangChain and LangGraph.

---

**Ready to build your own agents? Start with the [Tutorial](docs/TUTORIAL.md)! 🚀**
