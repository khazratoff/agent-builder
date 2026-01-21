# Quick Setup: Python MCP Weather Agent

## Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
pip install mcp-weather-server
```

### 2. Verify MCP Server
```bash
python -m mcp_weather_server
# Should show: Registered tools: ['get_current_weather', 'get_weather_byDateTimeRange', ...]
# Press Ctrl+C to stop
```

## Usage

```bash
cd src && python main.py
```

### Try These Queries:
```
You: What's the weather in London?
You: Check air quality in Beijing
You: What timezone is Tokyo in?
You: What's the weather in Paris and what about tomorrow?
```

## How It Works

1. **User asks about weather** → Supervisor routes to weather agent
2. **Weather agent** → Loads MCP tools from python server
3. **LLM reasoning** → Decides which tool to call (get_current_weather, etc.)
4. **MCP client** → Executes tool on external server
5. **LLM formats** → Returns natural language response

## Available MCP Tools
- get_current_weather
- get_weather_byDateTimeRange
- get_air_quality
- get_timezone_info
- get_current_datetime
- And 3 more...

## Troubleshooting

**"Weather service unavailable"**
```bash
pip install mcp-weather-server
```

**Connection hangs**
```bash
pkill -f "mcp_weather_server"
cd src && python main.py
```

Enjoy! 🌤️
