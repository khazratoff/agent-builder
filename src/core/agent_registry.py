"""
Agent registry for managing agent discovery and registration.

This module implements the Registry pattern, allowing agents to be
automatically discovered without modifying core code.
"""

from typing import Dict, List, Type, Optional
from .base_agent import BaseAgent


class AgentRegistry:
    """
    Singleton registry for managing all agents in the system.

    The registry maintains a catalog of all registered agents and provides
    methods for agent discovery and retrieval. Agents are registered using
    the @AgentRegistry.register decorator.

    Example:
        @AgentRegistry.register
        class MyAgent(BaseAgent):
            ...
    """

    _instance = None
    _agents: Dict[str, BaseAgent] = {}

    def __new__(cls):
        """Ensure only one instance of the registry exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(AgentRegistry, cls).__new__(cls)
            cls._agents = {}
        return cls._instance

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]) -> Type[BaseAgent]:
        """
        Decorator to register an agent class.

        This decorator instantiates the agent and adds it to the registry.
        It should be used on any agent class that inherits from BaseAgent.

        Args:
            agent_class: The agent class to register

        Returns:
            The same agent class (allows chaining)

        Raises:
            ValueError: If the agent name is already registered

        Example:
            @AgentRegistry.register
            class FileOperationsAgent(BaseAgent):
                @property
                def name(self) -> str:
                    return "file_operations"
                ...
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class.__name__} must inherit from BaseAgent")

        # Instantiate the agent
        agent_instance = agent_class()

        # Check for duplicate names
        if agent_instance.name in cls._agents:
            raise ValueError(
                f"Agent with name '{agent_instance.name}' is already registered. "
                f"Each agent must have a unique name."
            )

        # Register the agent
        cls._agents[agent_instance.name] = agent_instance
        print(f"✓ Registered agent: {agent_instance.name}")

        return agent_class

    @classmethod
    def get_agent(cls, name: str) -> Optional[BaseAgent]:
        """
        Retrieve an agent by name.

        Args:
            name: The unique name of the agent

        Returns:
            BaseAgent instance or None if not found
        """
        return cls._agents.get(name)

    @classmethod
    def get_all_agents(cls) -> List[BaseAgent]:
        """
        Get a list of all registered agents.

        Returns:
            List of all BaseAgent instances
        """
        return list(cls._agents.values())

    @classmethod
    def get_agent_names(cls) -> List[str]:
        """
        Get a list of all registered agent names.

        Returns:
            List of agent names
        """
        return list(cls._agents.keys())

    @classmethod
    def get_agent_info(cls) -> List[Dict[str, any]]:
        """
        Get detailed information about all registered agents.

        Returns:
            List of dictionaries containing agent metadata
        """
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
            }
            for agent in cls._agents.values()
        ]

    @classmethod
    def clear(cls):
        """
        Clear all registered agents.

        Useful for testing or reloading the agent system.
        """
        cls._agents.clear()

    @classmethod
    def agent_exists(cls, name: str) -> bool:
        """
        Check if an agent with the given name is registered.

        Args:
            name: Agent name to check

        Returns:
            True if agent exists, False otherwise
        """
        return name in cls._agents

    def __repr__(self) -> str:
        """Return string representation of the registry."""
        agent_count = len(self._agents)
        agent_names = ", ".join(self._agents.keys()) if self._agents else "none"
        return f"<AgentRegistry agents={agent_count} [{agent_names}]>"
