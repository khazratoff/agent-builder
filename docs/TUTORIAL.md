# Multi-Agent System Tutorial

A comprehensive guide to understanding and extending the multi-agent system.

## Table of Contents

1. [Understanding the Architecture](#understanding-the-architecture)
2. [How the Supervisor Works](#how-the-supervisor-works)
3. [Creating Your First Custom Agent](#creating-your-first-custom-agent)
4. [Implementing Custom Tools](#implementing-custom-tools)
5. [Testing Your Agent](#testing-your-agent)
6. [Advanced Patterns](#advanced-patterns)

---

## Understanding the Architecture

### The Big Picture

The system consists of three main layers:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: User Interface (main.py)                          │
│  • CLI interaction                                          │
│  • Command handling                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Orchestration (supervisor.py)                     │
│  • LangGraph StateGraph workflow                            │
│  • Request analysis                                         │
│  • Agent selection and routing                              │
└────────────────────────┬────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Agents (agents/)                                  │
│  • Specialized agent implementations                        │
│  • Tool execution                                           │
│  • Task completion                                          │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. BaseAgent (base_agent.py)

The abstract base class that all agents inherit from:

```python
class BaseAgent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for the agent"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """What the agent does (used for routing)"""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of tasks the agent can handle"""
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Tools available to the agent"""
        pass

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent's task"""
        pass
```

#### 2. AgentRegistry (agent_registry.py)

A singleton that manages agent registration:

```python
@AgentRegistry.register  # Decorator automatically registers the agent
class MyAgent(BaseAgent):
    ...
```

The registry provides:
- `get_agent(name)` - Retrieve an agent by name
- `get_all_agents()` - Get all registered agents
- `get_agent_info()` - Get metadata about all agents

#### 3. AgentState (state.py)

The state that flows through the LangGraph workflow:

```python
class AgentState(TypedDict):
    messages: List[dict]           # Conversation history
    user_input: str                # Original request
    current_agent: Optional[str]   # Active agent
    agent_output: Optional[str]    # Agent's result
    next_action: Optional[str]     # Supervisor's decision
    task_complete: bool            # Completion flag
    metadata: Optional[dict]       # Additional context
```

---

## How the Supervisor Works

### The LangGraph Workflow

The supervisor is a LangGraph StateGraph with three main nodes:

```
START → route_request → [agent_node] → finalize → END
```

#### Node 1: route_request

This node analyzes the user's request and selects the best agent:

1. **Get all registered agents** from the registry
2. **Build a prompt** with agent descriptions
3. **Ask the LLM** to select the most appropriate agent
4. **Validate** the selection
5. **Route** to the selected agent using `Command(goto=agent_name)`

```python
def _route_request(self, state: AgentState) -> Command:
    user_input = state["user_input"]
    agents = self.registry.get_all_agents()

    # Build prompt with agent information
    routing_prompt = f"""
    Available Agents:
    {agent_descriptions}

    User Request: "{user_input}"

    Which agent should handle this?
    """

    # Get LLM decision
    response = self.llm.invoke(routing_prompt)
    selected_agent = response.content.strip()

    # Route to agent
    return Command(
        update={"current_agent": selected_agent},
        goto=selected_agent
    )
```

#### Node 2: Agent Execution Nodes

Each registered agent gets its own node:

```python
def agent_node(state: AgentState) -> Command:
    agent = registry.get_agent(agent_name)
    result = agent.execute(state)

    return Command(
        update={**result, "task_complete": True},
        goto="finalize"
    )
```

#### Node 3: finalize

Formats and displays the final result.

### Dynamic Routing

The supervisor uses LangGraph's `Command` to dynamically route between agents:

```python
Command(
    update={"current_agent": "research"},  # Update state
    goto="research"  # Go to research agent node
)
```

This allows the workflow to adapt based on the user's request without hardcoded logic!

---

## Creating Your First Custom Agent

Let's build a **Weather Agent** that provides weather information.

### Step 1: Create the Tools

Create a new file `src/tools/weather_tools.py`:

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """
    Get weather information for a location.

    Args:
        location: City name or coordinates

    Returns:
        Weather information
    """
    # In production, you'd call a weather API
    # For this example, we'll return mock data
    return f"Weather in {location}: Sunny, 72°F (22°C)"

@tool
def get_forecast(location: str, days: int = 3) -> str:
    """
    Get weather forecast for multiple days.

    Args:
        location: City name
        days: Number of days (1-7)

    Returns:
        Multi-day forecast
    """
    forecast = f"{days}-day forecast for {location}:\n"
    forecast += "Day 1: Sunny, 72°F\n"
    forecast += "Day 2: Partly Cloudy, 68°F\n"
    forecast += "Day 3: Rainy, 61°F"
    return forecast
```

### Step 2: Create the Agent Class

Create `src/agents/weather_agent.py`:

```python
from typing import List, Dict, Any
from langchain.tools import BaseTool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.core.agent_registry import AgentRegistry
from src.tools.weather_tools import get_weather, get_forecast


@AgentRegistry.register  # Magic happens here!
class WeatherAgent(BaseAgent):
    """Agent specialized in weather information."""

    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.agent_executor = None
        super().__init__()

    @property
    def name(self) -> str:
        return "weather"

    @property
    def description(self) -> str:
        return (
            "Provides weather information and forecasts for any location. "
            "Can get current weather conditions and multi-day forecasts. "
            "Use this agent when the user asks about weather."
        )

    @property
    def capabilities(self) -> List[str]:
        return [
            "weather",
            "forecast",
            "temperature",
            "climate",
            "weather conditions",
            "weather report"
        ]

    def get_tools(self) -> List[BaseTool]:
        return [get_weather, get_forecast]

    def _create_agent_executor(self) -> AgentExecutor:
        tools = self.get_tools()

        template = """You are a Weather Agent.

Available tools:
{tools}

Tool Names: {tool_names}

Format:
Thought: What information is needed?
Action: tool to use
Action Input: input for the tool
Observation: tool result
...
Thought: I have the answer
Final Answer: formatted weather information

Task: {input}

{agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)
        agent = create_react_agent(self.llm, tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_input = state.get("user_input", "")

            if not user_input:
                return {
                    "agent_output": "Error: No input provided.",
                    "current_agent": self.name
                }

            if self.agent_executor is None:
                self.agent_executor = self._create_agent_executor()

            result = self.agent_executor.invoke({"input": user_input})

            return {
                "agent_output": result.get("output", "Weather check completed."),
                "current_agent": self.name,
                "metadata": {"agent": self.name}
            }

        except Exception as e:
            return {
                "agent_output": f"Error: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """Calculate confidence for weather requests."""
        keywords = ["weather", "forecast", "temperature", "rain", "sunny"]
        request_lower = request.lower()
        matches = sum(1 for kw in keywords if kw in request_lower)

        return 0.9 if matches >= 1 else 0.3
```

### Step 3: Register the Agent

Add your agent to `src/agents/__init__.py`:

```python
from src.agents.file_operations_agent import FileOperationsAgent
from src.agents.research_agent import ResearchAgent
from src.agents.weather_agent import WeatherAgent  # Add this

__all__ = ["FileOperationsAgent", "ResearchAgent", "WeatherAgent"]
```

### Step 4: Test It!

Run the system:

```bash
python src/main.py
```

Try it:
```
You: What's the weather in San Francisco?

🎯 Supervisor selected: weather
⚙️  Executing weather agent...
[Your weather agent responds!]
```

That's it! Your agent is now part of the system.

---

## Implementing Custom Tools

### Tool Basics

Tools are functions decorated with `@tool`:

```python
from langchain.tools import tool

@tool
def my_tool(param1: str, param2: int) -> str:
    """
    Tool description (shown to the LLM).

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        str: What the tool returns
    """
    # Your implementation
    result = f"Processed {param1} with {param2}"
    return result
```

### Best Practices

1. **Clear Descriptions**: The LLM uses the docstring to decide when to use the tool

2. **Type Hints**: Always include type hints for parameters

3. **Error Handling**: Return error messages as strings, don't raise exceptions

   ```python
   @tool
   def safe_divide(a: float, b: float) -> str:
       """Divide two numbers."""
       if b == 0:
           return "Error: Cannot divide by zero"
       return f"Result: {a / b}"
   ```

4. **Focused Tools**: Each tool should do one thing well

   ❌ Bad: `file_operations(action, file, content)`
   ✅ Good: `read_file(file)`, `write_file(file, content)`

### Tool Examples

#### API Call Tool

```python
@tool
def fetch_data(api_endpoint: str) -> str:
    """Fetch data from an API endpoint."""
    import requests

    try:
        response = requests.get(api_endpoint, timeout=5)
        response.raise_for_status()
        return f"Data: {response.json()}"
    except Exception as e:
        return f"Error fetching data: {str(e)}"
```

#### Database Query Tool

```python
@tool
def query_database(sql_query: str) -> str:
    """Execute a SQL query and return results."""
    import sqlite3

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        conn.close()

        return f"Results: {results}"
    except Exception as e:
        return f"Error: {str(e)}"
```

---

## Testing Your Agent

### Unit Testing

Test individual components:

```python
# test_weather_agent.py
from src.agents.weather_agent import WeatherAgent
from src.tools.weather_tools import get_weather

def test_weather_tool():
    result = get_weather("San Francisco")
    assert "San Francisco" in result
    assert "°F" in result or "°C" in result

def test_agent_creation():
    agent = WeatherAgent()
    assert agent.name == "weather"
    assert len(agent.get_tools()) > 0

def test_agent_execution():
    agent = WeatherAgent()
    state = {"user_input": "What's the weather in Tokyo?"}
    result = agent.execute(state)

    assert "agent_output" in result
    assert result["current_agent"] == "weather"
```

### Integration Testing

Test the full workflow:

```python
# test_integration.py
from src.core.supervisor import SupervisorWorkflow
import agents  # Register all agents

def test_weather_routing():
    supervisor = SupervisorWorkflow()
    supervisor.build()

    result = supervisor.invoke("What's the weather in London?")

    assert result["current_agent"] == "weather"
    assert result["task_complete"] == True
```

### Manual Testing

Create a test script:

```python
# test_my_agent.py
from dotenv import load_dotenv
from src.core.supervisor import SupervisorWorkflow
import agents

load_dotenv()

supervisor = SupervisorWorkflow()
supervisor.build()

test_cases = [
    "What's the weather in Paris?",
    "Give me a 5-day forecast for New York",
    "Is it raining in Seattle?"
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test}")
    print('='*60)
    result = supervisor.invoke(test)
    print()
```

---

## Advanced Patterns

### Pattern 1: Multi-Tool Agents

Agents can combine multiple tools:

```python
@AgentRegistry.register
class DataAgent(BaseAgent):
    def get_tools(self) -> List[BaseTool]:
        return [
            fetch_from_api,
            query_database,
            export_to_csv,
            visualize_data
        ]
```

### Pattern 2: Agent Collaboration

Agents can call other agents (advanced):

```python
def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # First, use research agent to gather data
    research_result = self.registry.get_agent("research").execute(state)

    # Then, process the data
    processed_data = self.process(research_result["agent_output"])

    return {"agent_output": processed_data}
```

### Pattern 3: Stateful Agents

Maintain state across invocations:

```python
class StatefulAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.session_data = {}

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        thread_id = state.get("metadata", {}).get("thread_id")

        # Access previous data
        previous = self.session_data.get(thread_id, {})

        # Store new data
        self.session_data[thread_id] = {
            "last_request": state["user_input"],
            "timestamp": datetime.now()
        }

        return {"agent_output": "Processed with memory"}
```

### Pattern 4: Conditional Tool Selection

Choose tools dynamically:

```python
def get_tools(self) -> List[BaseTool]:
    tools = [basic_tool]

    # Add optional tools based on environment
    if os.getenv("ENABLE_ADVANCED_FEATURES"):
        tools.append(advanced_tool)

    if has_database_connection():
        tools.append(database_tool)

    return tools
```

### Pattern 5: Custom Routing Logic

Override `can_handle` for smarter routing:

```python
def can_handle(self, request: str) -> float:
    """Custom confidence calculation."""
    request_lower = request.lower()

    # High confidence for explicit keywords
    if "weather" in request_lower or "forecast" in request_lower:
        return 0.95

    # Medium confidence for related terms
    if any(word in request_lower for word in ["temperature", "rain", "sunny"]):
        return 0.7

    # Check for location names
    if self._contains_location(request):
        return 0.6

    return 0.2

def _contains_location(self, text: str) -> bool:
    # Check if text contains city names
    cities = ["london", "paris", "tokyo", "new york"]
    return any(city in text.lower() for city in cities)
```

---

## Troubleshooting

### Agent Not Being Selected

1. **Check description**: Make sure your agent's description clearly states its purpose
2. **Test can_handle**: Verify your `can_handle` method returns appropriate scores
3. **Review capabilities**: Ensure capability keywords match common user requests

### Tools Not Working

1. **Check docstrings**: Tools need clear descriptions
2. **Verify imports**: Make sure tools are properly imported
3. **Test tools independently**: Call tools directly to verify they work

### LLM Errors

1. **Check API key**: Verify `OPENAI_API_KEY` is set
2. **Review prompts**: Ensure prompts are clear and well-formatted
3. **Check model access**: Verify you have access to the specified model

---

## Next Steps

1. **Build more agents**: Email, Calendar, Database, API clients
2. **Enhance tools**: Add real API integrations
3. **Improve routing**: Implement more sophisticated selection logic
4. **Add memory**: Implement conversation history
5. **Deploy**: Move from CLI to web interface

---

## Conclusion

You now understand:
- ✅ The architecture of the multi-agent system
- ✅ How the supervisor routes requests
- ✅ How to create custom agents
- ✅ How to implement tools
- ✅ How to test your agents
- ✅ Advanced patterns for complex scenarios

**Happy building! 🚀**

For more examples, check out [examples/add_custom_agent.py](../examples/add_custom_agent.py)
