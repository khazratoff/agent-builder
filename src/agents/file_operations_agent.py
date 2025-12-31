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
        """Create the agent executor with tools."""
        from langchain.agents import initialize_agent, AgentType

        tools = self.get_tools()

        # Create the agent executor using initialize_agent
        agent_executor = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            agent_kwargs={
                "system_message": """You are a File Operations Agent specialized in handling file system tasks.

Important Guidelines:
1. Always verify file paths before operations
2. Provide clear feedback about what was done
3. If an operation fails, explain why and suggest alternatives
4. Be careful with delete operations"""
            }
        )

        return agent_executor

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the file operations task.

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

            # Create agent executor if not already created
            if self.agent_executor is None:
                self.agent_executor = self._create_agent_executor()

            # Execute the task
            result = self.agent_executor.invoke({"input": user_input})

            output = result.get("output", "Task completed but no output generated.")

            return {
                "agent_output": output,
                "current_agent": self.name,
                "metadata": {
                    "agent": self.name,
                    "tools_used": [tool.name for tool in self.get_tools()]
                }
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
