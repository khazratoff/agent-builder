"""
Weather Agent using Python MCP weather server.

This agent connects to a Python-based MCP weather server (mcp_weather_server)
to get weather information using external tools.
"""

from typing import List, Dict, Any
import json
import re
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from core.mcp_client import MCPClientManager


@AgentRegistry.register
class WeatherAgent(BaseAgent):
    """
    Agent specialized in weather information using Python MCP server.

    This agent demonstrates how to use external MCP servers. It connects
    to the mcp_weather_server (installed via pip) and uses LLM reasoning
    to decide which tools to call.

    Tools are dynamically loaded from the MCP server on initialization,
    so capabilities automatically reflect what the server provides.
    """

    def __init__(self):
        """Initialize the Weather Agent with MCP client."""
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Configure Python MCP weather server
        # Server is started with: python -m mcp_weather_server
        self.mcp_config = {
            "command": "python",
            "args": ["-m", "mcp_weather_server"],
            "env": None
        }

        self.mcp_manager = MCPClientManager(self.mcp_config)
        self.available_tools = []
        self._capabilities_cache = None

        # Load tools and capabilities from MCP server
        self._load_mcp_tools()

        super().__init__()

    @property
    def name(self) -> str:
        """Return the agent's unique name."""
        return "weather"

    @property
    def description(self) -> str:
        """Return the agent's description."""
        return (
            "Handles weather-related queries using an external MCP weather server. "
            "Can get current weather, forecasts, weather details, air quality, "
            "timezone information, and date/time conversions for any location. "
            "Use this agent when the user asks about weather, temperature, forecasts, "
            "air quality, or time zones."
        )

    @property
    def capabilities(self) -> List[str]:
        """Return the agent's capabilities dynamically from MCP tools."""
        if self._capabilities_cache:
            return self._capabilities_cache

        # Generate capabilities from available MCP tools
        capabilities = []
        for tool in self.available_tools:
            tool_name = tool.get("name", "")
            # Convert snake_case tool names to readable capabilities
            readable = tool_name.replace("_", " ")
            capabilities.append(readable)

        # Cache the capabilities
        self._capabilities_cache = capabilities if capabilities else ["weather information"]
        return self._capabilities_cache

    def get_tools(self) -> List[Any]:
        """
        Return available MCP tools (for display purposes).

        Note: These are MCP tools, not LangChain tools.
        """
        return self.available_tools

    def _load_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Load available tools from MCP server.

        Returns:
            List of tool definitions
        """
        try:
            tools = self.mcp_manager.list_tools()
            self.available_tools = tools
            # Clear capabilities cache to force regeneration
            self._capabilities_cache = None
            print(f"✓ Loaded {len(tools)} tools from MCP weather server")
            return tools
        except Exception as e:
            print(f"Warning: Could not load MCP tools: {e}")
            self.available_tools = []
            return []

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute weather queries using MCP server with LLM reasoning.

        Args:
            state: Current agent state containing user input

        Returns:
            Dict with updated state including agent output
        """
        try:
            user_input = state.get("user_input", "")
            conversation_history = state.get("messages", [])

            if not user_input:
                return {
                    "agent_output": "Error: No user input provided.",
                    "current_agent": self.name
                }

            # Load available MCP tools
            mcp_tools = self._load_mcp_tools()

            if not mcp_tools:
                return {
                    "agent_output": (
                        "Weather service is currently unavailable. "
                        "Please ensure mcp_weather_server is installed: "
                        "pip install mcp-weather-server"
                    ),
                    "current_agent": self.name
                }

            # Build tool descriptions for LLM
            tool_descriptions = []
            for tool in mcp_tools:
                tool_desc = f"- {tool['name']}: {tool.get('description', 'No description')}"
                if tool.get('input_schema', {}).get('properties'):
                    params = list(tool['input_schema']['properties'].keys())
                    tool_desc += f" (parameters: {', '.join(params)})"
                tool_descriptions.append(tool_desc)

            tools_text = "\n".join(tool_descriptions)

            # Build conversation context
            context = ""
            if len(conversation_history) > 1:
                recent_history = conversation_history[-7:-1] if len(conversation_history) > 7 else conversation_history[:-1]
                context = "Previous conversation:\n"
                for msg in recent_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")[:100]  # Limit context length
                    if role in ["user", "assistant"]:
                        context += f"{role}: {content}\n"
                context += "\n"

            # Ask LLM to reason about which tool to use
            reasoning_prompt = f"""You are a Weather Agent with access to these MCP tools:

{tools_text}

{context}Current User Request: {user_input}

Analyze the request and determine:
1. Which tool(s) should be called
2. What arguments to pass to each tool

Common tool usage:
- get_current_weather: needs "city" and optionally "country"
- get_weather_byDateTimeRange: needs "city", "start_datetime", "end_datetime"
- get_air_quality: needs "city" and optionally "country"
- get_timezone_info: needs "city"

Respond ONLY with valid JSON in this format:
{{
    "reasoning": "brief explanation",
    "tool_calls": [
        {{
            "tool": "tool_name",
            "arguments": {{"param": "value"}}
        }}
    ]
}}

If you need clarification, set tool_calls to [] and explain in reasoning."""

            # Get LLM's reasoning
            reasoning_response = self.llm.invoke(reasoning_prompt)
            reasoning_text = reasoning_response.content

            # Parse LLM response
            try:
                # Try to parse as JSON
                reasoning_data = json.loads(reasoning_text)
            except json.JSONDecodeError:
                # Extract JSON from markdown code blocks or text
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', reasoning_text, re.DOTALL)
                if not json_match:
                    json_match = re.search(r'\{.*\}', reasoning_text, re.DOTALL)

                if json_match:
                    try:
                        reasoning_data = json.loads(json_match.group(1) if json_match.lastindex else json_match.group(0))
                    except:
                        return {
                            "agent_output": f"I need more specific information about what weather data you're looking for. Please specify a city or location.",
                            "current_agent": self.name
                        }
                else:
                    return {
                        "agent_output": reasoning_text,
                        "current_agent": self.name
                    }

            tool_calls = reasoning_data.get("tool_calls", [])
            reasoning = reasoning_data.get("reasoning", "")

            # If no tool calls, return reasoning
            if not tool_calls:
                return {
                    "agent_output": reasoning,
                    "current_agent": self.name
                }

            # Execute tool calls through MCP
            results = []
            for tool_call in tool_calls:
                tool_name = tool_call.get("tool")
                arguments = tool_call.get("arguments", {})

                print(f"  → Calling MCP tool: {tool_name} with {arguments}")

                # Execute the tool via MCP
                result = self.mcp_manager.execute_tool_call(tool_name, arguments)

                results.append({
                    "tool": tool_name,
                    "result": result
                })

            # Format results with LLM
            results_text = "\n\n".join([
                f"Tool: {r['tool']}\nResult: {r['result']}"
                for r in results
            ])

            final_prompt = f"""Based on the tool results, provide a helpful, natural language response to the user.

User Request: {user_input}

Tool Results:
{results_text}

Provide a clear, conversational response. Format the information in an easy-to-read way."""

            final_response = self.llm.invoke(final_prompt)
            output = final_response.content

            return {
                "agent_output": output,
                "current_agent": self.name,
                "metadata": {
                    "agent": self.name,
                    "mcp_tools_used": [r["tool"] for r in results],
                    "reasoning": reasoning
                }
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error details: {error_details}")
            return {
                "agent_output": f"Error in Weather Agent: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """
        Calculate confidence score for handling weather-related requests.

        Args:
            request: User's input string

        Returns:
            Confidence score between 0 and 1
        """
        weather_keywords = [
            "weather", "temperature", "forecast", "rain", "snow", "sunny",
            "cloudy", "storm", "wind", "climate", "hot", "cold", "warm",
            "degrees", "celsius", "fahrenheit", "humidity", "precipitation",
            "air quality", "aqi", "pollution", "timezone", "time zone"
        ]

        request_lower = request.lower()
        matches = sum(1 for keyword in weather_keywords if keyword in request_lower)

        # Calculate confidence based on keyword matches
        if matches >= 2:
            return 0.95
        elif matches == 1:
            return 0.85
        else:
            return 0.1
