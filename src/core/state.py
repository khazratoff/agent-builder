"""
State management for the multi-agent system.

This module defines the state schema used across the LangGraph workflow.
The state tracks the conversation flow, agent execution, and routing decisions.
"""

from typing import TypedDict, List, Optional, Any


class AgentState(TypedDict):
    """
    State schema for the multi-agent system.

    This TypedDict defines all the data that flows through the LangGraph workflow.
    Each node can read from and update this state.

    Attributes:
        messages: Conversation history as a list of message dictionaries
        user_input: The original user request/query
        current_agent: Name of the agent currently handling the request
        agent_output: Result/output from the last agent execution
        next_action: Supervisor's decision on what to do next
        task_complete: Flag indicating if the user's request is fully handled
        metadata: Additional context or information for agents
    """
    messages: List[dict]
    user_input: str
    current_agent: Optional[str]
    agent_output: Optional[str]
    next_action: Optional[str]
    task_complete: bool
    metadata: Optional[dict]
