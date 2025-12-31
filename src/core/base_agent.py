"""
Base agent class for the multi-agent system.

This module defines the abstract BaseAgent class that all agents must inherit from.
It establishes the contract that every agent must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.tools import BaseTool


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.

    Each agent must implement the required methods and provide metadata
    about its capabilities. This design enables the supervisor to make
    intelligent routing decisions.

    Attributes:
        name: Unique identifier for the agent
        description: Human-readable description of what the agent does
        capabilities: List of tasks/domains this agent can handle
    """

    def __init__(self):
        """Initialize the agent with metadata."""
        self._validate_metadata()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of the agent.

        Returns:
            str: Agent name (e.g., "file_operations", "research")
        """
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """
        Return a detailed description of the agent's purpose.

        This description is used by the supervisor to make routing decisions.

        Returns:
            str: Detailed description of agent capabilities
        """
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        Return a list of capabilities/domains this agent handles.

        Returns:
            List[str]: List of capability keywords (e.g., ["file reading", "file writing"])
        """
        pass

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """
        Return the list of tools this agent can use.

        Returns:
            List[BaseTool]: LangChain tools available to this agent
        """
        pass

    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's task based on the current state.

        This is the main entry point where the agent performs its work.
        The agent receives the current state and returns updates.

        Args:
            state: Current AgentState dictionary

        Returns:
            Dict[str, Any]: Updates to apply to the state
        """
        pass

    def can_handle(self, request: str) -> float:
        """
        Calculate confidence score for handling a request.

        This method can be overridden by agents that want custom
        routing logic. Default implementation returns 0.5.

        Args:
            request: The user's input string

        Returns:
            float: Confidence score between 0 and 1
        """
        return 0.5

    def _validate_metadata(self):
        """Validate that required metadata is properly defined."""
        try:
            name = self.name
            description = self.description
            capabilities = self.capabilities

            if not name or not isinstance(name, str):
                raise ValueError(f"{self.__class__.__name__}: 'name' must be a non-empty string")

            if not description or not isinstance(description, str):
                raise ValueError(f"{self.__class__.__name__}: 'description' must be a non-empty string")

            if not capabilities or not isinstance(capabilities, list):
                raise ValueError(f"{self.__class__.__name__}: 'capabilities' must be a non-empty list")

        except NotImplementedError:
            raise ValueError(
                f"{self.__class__.__name__} must implement 'name', 'description', and 'capabilities' properties"
            )

    def __repr__(self) -> str:
        """Return string representation of the agent."""
        return f"<{self.__class__.__name__} name='{self.name}'>"
