"""
Research Agent

This agent handles research tasks including web search, content summarization,
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

    This agent can perform web searches, summarize content, extract specific
    information, and analyze topics. It's useful for research-related tasks.
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
            "Specializes in research and information gathering tasks. Can perform web searches, "
            "summarize long content, extract specific information from text, and analyze topics. "
            "Use this agent when the user needs to find information, research a topic, or analyze content."
        )

    @property
    def capabilities(self) -> List[str]:
        """Return the agent's capabilities."""
        return [
            "web search",
            "internet search",
            "find information",
            "research topics",
            "summarize content",
            "extract information",
            "analyze topics",
            "gather data",
            "information retrieval"
        ]

    def get_tools(self) -> List[BaseTool]:
        """Return the tools available to this agent."""
        return [web_search, summarize_content, extract_information, analyze_topic]

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
                "system_message": """You are a Research Agent specialized in information gathering and analysis.

Important Guidelines:
1. Use web_search to find current information online
2. Use summarize_content to condense long texts
3. Use extract_information to pull specific details from content
4. Use analyze_topic for comprehensive topic analysis
5. Provide well-structured, informative responses
6. Cite sources when available"""
            }
        )

        return agent_executor

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the research task.

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

            output = result.get("output", "Research completed but no output generated.")

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
                "agent_output": f"Error in Research Agent: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """
        Calculate confidence score for handling a research request.

        Args:
            request: User's input string

        Returns:
            Confidence score between 0 and 1
        """
        research_keywords = [
            "search", "find", "research", "look up", "information about",
            "tell me about", "what is", "who is", "analyze", "summarize",
            "explain", "learn about", "gather", "investigate"
        ]

        request_lower = request.lower()
        matches = sum(1 for keyword in research_keywords if keyword in request_lower)

        # Calculate confidence based on keyword matches
        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.75
        else:
            return 0.3
