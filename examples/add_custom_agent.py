"""
Example: Adding a Custom Agent to the Multi-Agent System

This example demonstrates how easy it is to add a new agent to the system.
We'll create a simple Math Agent that can perform calculations.

Steps:
1. Create a new agent class that inherits from BaseAgent
2. Implement required properties and methods
3. Decorate with @AgentRegistry.register
4. Create tools for the agent
5. Run the system - the new agent is automatically available!
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from typing import List, Dict, Any
from langchain.tools import tool, BaseTool
from langchain_openai import ChatOpenAI

from core.base_agent import BaseAgent
from core.agent_registry import AgentRegistry
from core.supervisor import SupervisorWorkflow


# Step 1: Define tools for the agent
@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Safely evaluates basic math expressions like "2 + 2", "10 * 5", etc.

    Args:
        expression: The mathematical expression to evaluate

    Returns:
        str: The result of the calculation

    Example:
        calculate("(5 + 3) * 2")
    """
    try:
        # Use eval safely with limited scope
        allowed_names = {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "pow": pow
        }

        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, allowed_names)

        return f"Result: {expression} = {result}"

    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


@tool
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """
    Convert between common units.

    Supports: meters/feet, kg/pounds, celsius/fahrenheit

    Args:
        value: The numeric value to convert
        from_unit: The source unit
        to_unit: The target unit

    Returns:
        str: The converted value

    Example:
        convert_units(100, "celsius", "fahrenheit")
    """
    try:
        conversions = {
            ("meters", "feet"): lambda x: x * 3.28084,
            ("feet", "meters"): lambda x: x / 3.28084,
            ("kg", "pounds"): lambda x: x * 2.20462,
            ("pounds", "kg"): lambda x: x / 2.20462,
            ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
        }

        key = (from_unit.lower(), to_unit.lower())

        if key not in conversions:
            return f"Conversion from {from_unit} to {to_unit} is not supported."

        result = conversions[key](value)

        return f"{value} {from_unit} = {result:.2f} {to_unit}"

    except Exception as e:
        return f"Error converting units: {str(e)}"


# Step 2: Create the agent class
@AgentRegistry.register  # This decorator registers the agent automatically!
class MathAgent(BaseAgent):
    """
    Agent specialized in mathematical calculations and conversions.

    This agent can perform calculations and unit conversions.
    It demonstrates how easy it is to add a new agent to the system.
    """

    def __init__(self):
        """Initialize the Math Agent."""
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.agent_executor = None
        super().__init__()

    @property
    def name(self) -> str:
        """Return the agent's unique name."""
        return "math"

    @property
    def description(self) -> str:
        """Return the agent's description."""
        return (
            "Specializes in mathematical calculations and unit conversions. "
            "Can evaluate mathematical expressions and convert between common units "
            "(meters/feet, kg/pounds, celsius/fahrenheit). "
            "Use this agent when the user needs to perform calculations or convert units."
        )

    @property
    def capabilities(self) -> List[str]:
        """Return the agent's capabilities."""
        return [
            "calculate",
            "math",
            "arithmetic",
            "convert units",
            "unit conversion",
            "evaluate expression",
            "solve math"
        ]

    def get_tools(self) -> List[BaseTool]:
        """Return the tools available to this agent."""
        return [calculate, convert_units]

    def _create_agent_executor(self):
        """Create the agent executor with tools."""
        from langchain.agents import AgentExecutor, create_openai_functions_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

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
                "system_message": "You are a Math Agent specialized in calculations and unit conversions."
            }
        )

        return agent_executor

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the math task."""
        try:
            user_input = state.get("user_input", "")

            if not user_input:
                return {
                    "agent_output": "Error: No user input provided.",
                    "current_agent": self.name
                }

            if self.agent_executor is None:
                self.agent_executor = self._create_agent_executor()

            result = self.agent_executor.invoke({"input": user_input})

            output = result.get("output", "Calculation completed.")

            return {
                "agent_output": output,
                "current_agent": self.name,
                "metadata": {"agent": self.name}
            }

        except Exception as e:
            return {
                "agent_output": f"Error in Math Agent: {str(e)}",
                "current_agent": self.name
            }

    def can_handle(self, request: str) -> float:
        """Calculate confidence score for handling a math request."""
        math_keywords = [
            "calculate", "compute", "math", "convert", "units",
            "add", "subtract", "multiply", "divide", "plus", "minus"
        ]

        request_lower = request.lower()
        matches = sum(1 for keyword in math_keywords if keyword in request_lower)

        if matches >= 2:
            return 0.9
        elif matches == 1:
            return 0.75
        else:
            return 0.3


# Step 3: Test the new agent!
if __name__ == "__main__":
    from dotenv import load_dotenv
    import agents  # Import existing agents

    load_dotenv()

    print("\n" + "="*60)
    print("  Custom Agent Example: Math Agent")
    print("="*60 + "\n")

    print("✓ Math Agent created and registered!")
    print("\nLet's test the multi-agent system with the new agent...\n")

    # Build the supervisor
    supervisor = SupervisorWorkflow(model="gpt-4o")
    app = supervisor.build()

    # Test requests
    test_requests = [
        "What is 15 * 23 + 47?",
        "Convert 100 celsius to fahrenheit",
        "Calculate (2 + 3) * (4 + 5)"
    ]

    for request in test_requests:
        print(f"\n{'='*60}")
        print(f"Request: {request}")
        print('='*60)

        result = supervisor.invoke(request)

        print()

    print("\n" + "="*60)
    print("  That's it! Adding a new agent is that easy!")
    print("="*60)
    print("\nKey Points:")
    print("  1. Create a class inheriting from BaseAgent")
    print("  2. Implement required properties and methods")
    print("  3. Use @AgentRegistry.register decorator")
    print("  4. The agent is automatically available in the system!")
    print()
