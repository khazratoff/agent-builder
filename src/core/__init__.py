"""
Core module for the multi-agent system.

This module exports the main components needed to build and register agents.
"""

from .base_agent import BaseAgent
from .agent_registry import AgentRegistry
from .state import AgentState

__all__ = ["BaseAgent", "AgentRegistry", "AgentState"]
