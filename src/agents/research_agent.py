"""
Research Agent

This agent handles research tasks including web searches, content summarization,
information extraction, and topic analysis.
"""

from typing import List, Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from tools.research_tools import web_search, summarize_content, extract_information, analyze_topic


@AgentRegistry.register
class ResearchAgent(BaseAgent):
    """
    Agent specialized in research and information gathering.

    This agent can perform web searches, summarize content, extract information,
    and analyze topics. It's useful for research-related tasks.
    """

    def __init__(self):
        """Initialize the Research Agent."""
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.agent_executor = None
        super().__init__()

    @property
    def name(self) -> str:
        """Return the agent's unique name."""
        return "research"

    @property
    def description(self) -> str:
        """Return the agent's description."""
        return (
            "Handles research tasks including web searches, content summarization, "
            "information extraction, and topic analysis. Use this agent when the user "
            "wants to research topics, find information, or analyze content."
        )

    @property
    def capabilities(self) -> List[str]:
        """Return the agent's capabilities."""
        return [
            "web search",
            "content summarization",
            "information extraction",
            "topic analysis",
            "research tasks",
            "information gathering"
        ]

    def get_tools(self) -> List[BaseTool]:
        """Return the tools available to this agent."""
        return [web_search, summarize_content, extract_information, analyze_topic]

    def _create_agent_executor(self):
        """Create the agent executor with tools - simplified version."""
        tools = self.get_tools()

        # Bind tools directly to LLM
        llm_with_tools = self.llm.bind_tools(tools)

        return llm_with_tools

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the research task with actual tool execution.

        Args:
            state: Current agent state containing user input

        Returns:
            Dict with updated state including agent output
        """
        try:
            user_input = state.get("user_input", "")

            if not user_input:
                return {
                    "agent_output": "Error: No user input provided.",
                    "current_agent": self.name
                }

            # Create LLM with tools if not already created
            if self.agent_executor is None:
                self.agent_executor = self._create_agent_executor()

            # Get tools as a dict for lookup
            tools = {tool.name: tool for tool in self.get_tools()}

            # System message
            system_msg = (
                "You are a Research Agent. Use the available tools to research and answer the user's question. "
                "You can use web search, content summarization, information extraction, and topic analysis."
            )

            # Create messages
            messages = [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_input}
            ]

            # Tool execution loop
            max_iterations = 5
            for iteration in range(max_iterations):
                # Get LLM response with tool calls
                response = self.agent_executor.invoke(messages)

                # Check if there are tool calls
                if not hasattr(response, 'tool_calls') or not response.tool_calls:
                    # No more tool calls, return the final response
                    output = response.content if response.content else "Research completed."
                    return {
                        "agent_output": output,
                        "current_agent": self.name,
                        "metadata": {
                            "agent": self.name,
                            "iterations": iteration + 1
                        }
                    }

                # Execute each tool call
                messages.append(response)  # Add AI response to messages

                for tool_call in response.tool_calls:
                    tool_name = tool_call.get("name")
                    tool_args = tool_call.get("args", {})

                    if tool_name in tools:
                        # Execute the tool
                        tool_result = tools[tool_name].invoke(tool_args)

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": str(tool_result),
                            "tool_call_id": tool_call.get("id"),
                            "name": tool_name
                        })
                    else:
                        messages.append({
                            "role": "tool",
                            "content": f"Error: Tool '{tool_name}' not found",
                            "tool_call_id": tool_call.get("id"),
                            "name": tool_name
                        })

            # Max iterations reached
            return {
                "agent_output": "Research execution reached maximum iterations. Please try breaking down your question.",
                "current_agent": self.name
            }

        except Exception as e:
            return {
                "agent_output": f"Error in Research Agent: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """
        Calculate confidence score for handling a research-related request.

        Args:
            request: User's input string

        Returns:
            Confidence score between 0 and 1
        """
        research_keywords = [
            "search", "research", "find", "information", "analyze", "summarize",
            "topic", "web", "look up", "investigate", "study"
        ]

        request_lower = request.lower()
        matches = sum(1 for keyword in research_keywords if keyword in request_lower)

        # Calculate confidence based on keyword matches
        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.7
        else:
            return 0.3
