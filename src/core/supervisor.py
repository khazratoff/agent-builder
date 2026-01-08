"""
Supervisor module for the multi-agent system.

This module implements the LangGraph StateGraph that orchestrates
agent selection and execution based on user requests.
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .agent_registry import AgentRegistry


class SupervisorWorkflow:
    """
    Supervisor workflow that routes requests to appropriate agents.

    This class builds and manages the LangGraph StateGraph that:
    1. Analyzes user requests
    2. Selects the best agent to handle the request
    3. Executes the agent
    4. Returns the result
    """

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize the supervisor workflow.

        Args:
            model: The LLM model to use for routing decisions
        """
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.workflow = None
        self.app = None

    def _route_request(self, state: AgentState) -> Command:
        """
        Analyze the user request and route to the appropriate agent.

        This node uses the LLM to decide which agent should handle the request
        based on agent descriptions and capabilities.

        Args:
            state: Current agent state

        Returns:
            Command with routing decision
        """
        user_input = state["user_input"]

        # Get all registered agents
        agents = AgentRegistry.get_all_agents()

        if not agents:
            return Command(
                update={
                    "agent_output": "Error: No agents are registered in the system.",
                    "task_complete": True
                },
                goto="finalize"
            )

        # Build agent information for the LLM
        agent_info = []
        for agent in agents:
            info = f"- {agent.name}: {agent.description}"
            agent_info.append(info)

        agent_descriptions = "\n".join(agent_info)
        agent_names = [agent.name for agent in agents]

        # Create prompt for agent selection
        routing_prompt = f"""You are a supervisor that routes user requests to the most appropriate specialized agent.

Available Agents:
{agent_descriptions}

User Request: "{user_input}"

Based on the user's request, which agent should handle this task?
Respond with ONLY the agent name, nothing else.

Available agent names: {", ".join(agent_names)}

Selected Agent:"""

        # Get LLM decision
        response = self.llm.invoke(routing_prompt)
        selected_agent_name = response.content.strip().lower()

        # Validate the selection
        if selected_agent_name not in agent_names:
            # If LLM gives invalid response, use confidence scores
            best_agent = None
            best_score = 0.0

            for agent in agents:
                score = agent.can_handle(user_input)
                if score > best_score:
                    best_score = score
                    best_agent = agent

            selected_agent_name = best_agent.name if best_agent else agent_names[0]

        print(f"\n🎯 Supervisor selected: {selected_agent_name}")

        return Command(
            update={
                "current_agent": selected_agent_name,
                "next_action": f"execute_{selected_agent_name}"
            },
            goto=selected_agent_name
        )

    def _create_agent_node(self, agent_name: str):
        """
        Create a node function for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Node function that executes the agent
        """
        def agent_node(state: AgentState) -> Command:
            """Execute the specified agent."""
            agent = AgentRegistry.get_agent(agent_name)

            if not agent:
                return Command(
                    update={
                        "agent_output": f"Error: Agent '{agent_name}' not found.",
                        "task_complete": True
                    },
                    goto="finalize"
                )

            print(f"\n⚙️  Executing {agent.name} agent...")

            # Execute the agent
            result = agent.execute(state)

            # Update state with result
            return Command(
                update={
                    **result,
                    "task_complete": True
                },
                goto="finalize"
            )

        return agent_node

    def _finalize(self, state: AgentState) -> dict:
        """
        Finalize and format the response.

        Args:
            state: Current agent state

        Returns:
            Empty dict (state is already updated)
        """
        agent_output = state.get("agent_output", "No output generated.")
        current_agent = state.get("current_agent", "unknown")

        print(f"\n✅ Task completed by {current_agent} agent")
        print(f"\n{'='*60}")
        print(f"Result:\n{agent_output}")
        print(f"{'='*60}\n")

        return {}

    def build(self) -> StateGraph:
        """
        Build the LangGraph StateGraph workflow.

        Returns:
            Compiled StateGraph application
        """
        # Create the workflow
        workflow = StateGraph(AgentState)

        # Add the supervisor/routing node
        workflow.add_node("route_request", self._route_request)

        # Add a node for each registered agent
        agents = AgentRegistry.get_all_agents()
        for agent in agents:
            agent_node = self._create_agent_node(agent.name)
            workflow.add_node(agent.name, agent_node)

        # Add finalize node
        workflow.add_node("finalize", self._finalize)

        # Add edges
        workflow.add_edge(START, "route_request")
        workflow.add_edge("finalize", END)

        # Store the workflow
        self.workflow = workflow

        # Compile with memory
        memory = MemorySaver()
        self.app = workflow.compile(checkpointer=memory)

        print(f"\n✓ Supervisor workflow built with {len(agents)} agents")

        return self.app

    def visualize(self, output_path: str = "workflow_graph.png"):
        """
        Generate a visual representation of the workflow.

        Args:
            output_path: Path to save the visualization
        """
        if self.app is None:
            raise ValueError("Workflow not built yet. Call build() first.")

        try:
            from langchain_core.runnables.graph import MermaidDrawMethod

            # Generate mermaid diagram
            mermaid_png = self.app.get_graph().draw_mermaid_png(
                draw_method=MermaidDrawMethod.API
            )

            with open(output_path, "wb") as f:
                f.write(mermaid_png)

            print(f"✓ Workflow visualization saved to {output_path}")

        except Exception as e:
            print(f"Could not generate visualization: {e}")
            print("Tip: Visualization requires additional dependencies")

    def invoke(self, user_input: str, thread_id: str = "default") -> dict:
        """
        Execute the workflow for a user request.

        Args:
            user_input: The user's request/query
            thread_id: Thread ID for conversation persistence

        Returns:
            Final state after execution
        """
        if self.app is None:
            raise ValueError("Workflow not built yet. Call build() first.")

        # Create initial state
        initial_state = {
            "messages": [],
            "user_input": user_input,
            "current_agent": None,
            "agent_output": None,
            "next_action": None,
            "task_complete": False,
            "metadata": {}
        }

        # Configure thread for persistence
        config = {"configurable": {"thread_id": thread_id}}

        # Execute the workflow
        result = self.app.invoke(initial_state, config)

        return result

    def stream(self, user_input: str, thread_id: str = "default"):
        """
        Stream the workflow execution for a user request.

        Args:
            user_input: The user's request/query
            thread_id: Thread ID for conversation persistence

        Yields:
            State updates as they occur
        """
        if self.app is None:
            raise ValueError("Workflow not built yet. Call build() first.")

        # Create initial state
        initial_state = {
            "messages": [],
            "user_input": user_input,
            "current_agent": None,
            "agent_output": None,
            "next_action": None,
            "task_complete": False,
            "metadata": {}
        }

        # Configure thread for persistence
        config = {"configurable": {"thread_id": thread_id}}

        # Stream the workflow
        for step in self.app.stream(initial_state, config):
            yield step
