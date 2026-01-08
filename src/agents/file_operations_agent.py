"""
File Operations Agent

This agent handles all file system operations including reading, writing,
listing, and deleting files.
"""

from typing import List, Dict, Any
from langchain.tools import BaseTool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from tools.file_tools import read_file, write_file, list_files, delete_file, append_to_file


@AgentRegistry.register
class FileOperationsAgent(BaseAgent):
    """
    Agent specialized in file system operations.

    This agent can read, write, list, delete, and append to files.
    It's useful for tasks involving file management and manipulation.
    """

    def __init__(self):
        """Initialize the File Operations Agent."""
        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.agent_executor = None
        super().__init__()

    @property
    def name(self) -> str:
        """Return the agent's unique name."""
        return "file_operations"

    @property
    def description(self) -> str:
        """Return the agent's description."""
        return (
            "Handles all file system operations including reading files, writing to files, "
            "listing directory contents, deleting files, and appending to existing files. "
            "Use this agent when the user wants to interact with the file system."
        )

    @property
    def capabilities(self) -> List[str]:
        """Return the agent's capabilities."""
        return [
            "read files",
            "write files",
            "create files",
            "delete files",
            "list directories",
            "append to files",
            "file management",
            "file system operations"
        ]

    def get_tools(self) -> List[BaseTool]:
        """Return the tools available to this agent."""
        return [read_file, write_file, list_files, delete_file, append_to_file]

    def _create_agent_executor(self):
        """Create the agent executor with tools - simplified version."""
        tools = self.get_tools()

        # Bind tools directly to LLM
        llm_with_tools = self.llm.bind_tools(tools)

        return llm_with_tools

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the file operations task with actual tool execution.

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
                "You are a File Operations Agent. Use the available tools to complete the user's request. "
                "Call the appropriate tool(s) to perform the actual file operations."
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
                    output = response.content if response.content else "Task completed successfully."
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
                "agent_output": "Task execution reached maximum iterations. Please try breaking down your request.",
                "current_agent": self.name
            }

        except Exception as e:
            return {
                "agent_output": f"Error in File Operations Agent: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """
        Calculate confidence score for handling a file-related request.

        Args:
            request: User's input string

        Returns:
            Confidence score between 0 and 1
        """
        file_keywords = [
            "file", "read", "write", "save", "delete", "list", "directory",
            "folder", "create", "append", "open", "load"
        ]

        request_lower = request.lower()
        matches = sum(1 for keyword in file_keywords if keyword in request_lower)

        # Calculate confidence based on keyword matches
        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.7
        else:
            return 0.3
