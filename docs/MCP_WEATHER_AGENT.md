# MCP Weather Agent

## Overview

The Weather Agent demonstrates how to integrate **Model Context Protocol (MCP)** servers with the multi-agent system. Unlike other agents that use LangChain tools, this agent connects to an external MCP server to access weather data.

## What is MCP?

**Model Context Protocol (MCP)** is a standard protocol for connecting LLMs to external data sources and tools. It allows:
- Standardized tool definitions
- Communication with external servers
- Language-agnostic tool implementations
- Easy integration of third-party services

## Architecture

```
┌─────────────────┐
│  Weather Agent  │
└────────┬────────┘
         │
         │ Uses LLM for reasoning
         ▼
┌─────────────────┐
│   MCP Client    │  ← Custom wrapper in src/core/mcp_client.py
└────────┬────────┘
         │
         │ MCP Protocol
         ▼
┌─────────────────┐
│   MCP Server    │  ← External weather server
│  (Node.js/NPM)  │
└─────────────────┘
```

## How It Works

### 1. **Tool Discovery**
```python
# Agent loads available tools from MCP server
mcp_tools = self._load_mcp_tools()
# Returns: [
#   {
#     "name": "get_weather",
#     "description": "Get current weather",
#     "input_schema": {...}
#   },
#   ...
# ]
```

### 2. **LLM Reasoning**
```python
# LLM decides which tool to use
reasoning_prompt = f"""
Available MCP tools:
{tools_text}

User Request: {user_input}

Decide which tool to call and with what arguments.
Respond in JSON format.
"""

response = self.llm.invoke(reasoning_prompt)
```

### 3. **Tool Execution**
```python
# Execute tool through MCP client
result = self.mcp_manager.run_sync(
    self.mcp_manager.execute_tool_call(
        tool_name="get_weather",
        arguments={"city": "London"}
    )
)
```

### 4. **Response Formatting**
```python
# LLM formats the result naturally
final_prompt = f"""
User Request: {user_input}
Tool Results: {results}

Provide a natural language response.
"""
```

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install MCP Weather Server (Node.js)
```bash
# Install Node.js if you don't have it
# Then install the weather MCP server globally
npm install -g @modelcontextprotocol/server-weather
```

### 3. Verify Installation
```bash
# Test the MCP server directly
npx -y @modelcontextprotocol/server-weather

# Should start the MCP server
```

## Usage

### Basic Weather Query
```
You: What's the weather in London?

Agent: Currently in London, it's 15°C with partly cloudy skies...
```

### Multi-step Reasoning
```
You: Is it going to rain in Paris tomorrow?

Agent:
1. Reasoning: Need to get forecast for Paris
2. Calls: get_forecast tool with {"city": "Paris"}
3. Response: Yes, there's a 70% chance of rain tomorrow in Paris...
```

### With Conversation Context
```
You: What's the weather in Tokyo?
Agent: Tokyo is currently 22°C and sunny...

You: What about tomorrow?
Agent: [Understands "tomorrow" refers to Tokyo from context]
       Tomorrow in Tokyo will be 24°C with scattered clouds...
```

## MCP Client API

### MCPClientManager

```python
from core.mcp_client import MCPClientManager

# Initialize
manager = MCPClientManager({
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-weather"]
})

# List available tools
tools = manager.run_sync(manager.list_tools())

# Execute a tool
result = manager.run_sync(
    manager.execute_tool_call(
        "get_weather",
        {"city": "London"}
    )
)
```

### Async Usage

```python
async with manager.get_client() as client:
    # Get tools
    tools = client.get_available_tools()

    # Call tool
    result = await client.call_tool(
        "get_weather",
        {"city": "London"}
    )
```

## Available MCP Weather Tools

The weather MCP server typically provides:

1. **get_weather**
   - Get current weather for a location
   - Parameters: `city`, `country` (optional)

2. **get_forecast**
   - Get weather forecast
   - Parameters: `city`, `days` (optional)

3. **get_alerts**
   - Get weather alerts
   - Parameters: `city`, `country` (optional)

## Agent Capabilities

The Weather Agent can:
- ✅ Get current weather for any city
- ✅ Provide weather forecasts
- ✅ Check weather alerts
- ✅ Compare weather across cities
- ✅ Answer temperature questions
- ✅ Use conversation context for follow-ups

## Comparison: LangChain Tools vs MCP Tools

| Feature | LangChain Tools | MCP Tools |
|---------|----------------|-----------|
| **Implementation** | Python functions | External servers |
| **Language** | Python only | Any language |
| **Deployment** | Embedded in app | Separate service |
| **Examples** | FileTools, ResearchTools | WeatherAgent |
| **Updates** | Requires code changes | Server updates independently |
| **Scalability** | Limited to Python process | Can run distributed |
| **Sharing** | Code sharing | Protocol sharing |

## Error Handling

The agent handles common errors:

### MCP Server Not Available
```python
if not mcp_tools:
    return {
        "agent_output": (
            "Weather service is currently unavailable. "
            "Please install: npm install -g @modelcontextprotocol/server-weather"
        )
    }
```

### Tool Execution Failure
```python
try:
    result = await client.call_tool(tool_name, arguments)
except Exception as e:
    return f"Error calling tool {tool_name}: {str(e)}"
```

### JSON Parsing Error
```python
try:
    reasoning_data = json.loads(reasoning_text)
except json.JSONDecodeError:
    # Try to extract JSON with regex
    json_match = re.search(r'\{.*\}', reasoning_text, re.DOTALL)
```

## Creating Custom MCP Agents

Follow this pattern to create agents with other MCP servers:

```python
from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from core.mcp_client import MCPClientManager

@AgentRegistry.register
class MyMCPAgent(BaseAgent):
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Configure your MCP server
        self.mcp_config = {
            "command": "npx",  # or "python", etc.
            "args": ["-y", "@your/mcp-server"],
            "env": None
        }

        self.mcp_manager = MCPClientManager(self.mcp_config)
        super().__init__()

    @property
    def name(self) -> str:
        return "my_mcp_agent"

    # ... rest of implementation similar to WeatherAgent
```

## Example MCP Servers

You can create agents for various MCP servers:

### File System MCP Server
```python
mcp_config = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
}
```

### Database MCP Server
```python
mcp_config = {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://..."]
}
```

### Custom Python MCP Server
```python
mcp_config = {
    "command": "python",
    "args": ["my_mcp_server.py"]
}
```

## Debugging

### Enable Debug Output
```python
# In weather_agent.py, add print statements
print(f"Available tools: {mcp_tools}")
print(f"LLM reasoning: {reasoning_text}")
print(f"Tool results: {results}")
```

### Test MCP Server Directly
```bash
# Run the server and test it
npx -y @modelcontextprotocol/server-weather

# In another terminal, test with curl or similar
```

### Check Connection
```python
# Add to execute method
if not self.mcp_manager.client.connected:
    print("⚠️ MCP client not connected")
```

## Limitations

1. **Requires Node.js**: Weather MCP server needs Node.js/NPM
2. **Async/Sync Bridge**: Uses `run_sync` to bridge async MCP to sync agent
3. **Single Server**: Each agent connects to one MCP server
4. **Startup Time**: Connecting to MCP server adds latency

## Future Enhancements

Possible improvements:
- Connection pooling for MCP clients
- Caching of tool results
- Multiple MCP servers per agent
- Streaming MCP responses
- MCP server health checks
- Automatic reconnection on failure

## Troubleshooting

### "Weather service is currently unavailable"
```bash
# Install the MCP weather server
npm install -g @modelcontextprotocol/server-weather

# Verify it works
npx -y @modelcontextprotocol/server-weather
```

### "ModuleNotFoundError: No module named 'mcp'"
```bash
# Install MCP SDK
pip install mcp
```

### "Command 'npx' not found"
```bash
# Install Node.js from nodejs.org
# Or use your package manager:
# macOS: brew install node
# Ubuntu: sudo apt install nodejs npm
```

## Summary

The Weather Agent demonstrates:
- ✅ Integration with external MCP servers
- ✅ LLM-based tool selection and reasoning
- ✅ Async/sync communication handling
- ✅ Protocol-based tool access (not code-based)
- ✅ Easy integration of third-party services

This architecture allows you to connect to any MCP server and use its tools within your agent system!
