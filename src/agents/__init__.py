"""
Agents module for the multi-agent system.

This module automatically registers all agents when imported.
Add new agent files here and they will be automatically discovered.
"""

# Import all agents to trigger their registration
from .file_operations_agent import FileOperationsAgent
from .research_agent import ResearchAgent

__all__ = ["FileOperationsAgent", "ResearchAgent",]
