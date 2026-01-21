"""
Main application entry point for the multi-agent system.

This module provides an interactive CLI interface for users to interact
with the multi-agent system.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Suppress INFO logs from MCP and related libraries
logging.getLogger("mcp").setLevel(logging.WARNING)
logging.getLogger("mcp-weather").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("mcp.server.lowlevel.server").setLevel(logging.WARNING)

# Add src to Python path for imports
sys.path.insert(0, os.path.dirname(__file__))

from core.supervisor import SupervisorWorkflow
from core.agent_registry import AgentRegistry

# Import agents to trigger registration
try:
    import agents
except ImportError:
    # Fallback: import agents directly
    from agents.file_operations_agent import FileOperationsAgent
    from agents.research_agent import ResearchAgent


def print_banner():
    """Print welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🤖 Multi-Agent System with LangGraph 🤖             ║
║                                                              ║
║          A Flexible, OOP-Based Agent Architecture           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """Print help information."""
    help_text = """
Available Commands:
  /help     - Show this help message
  /agents   - List all registered agents
  /clear    - Clear the screen
  /exit     - Exit the application

Usage:
  Simply type your request and press Enter. The supervisor will
  automatically route your request to the appropriate agent.

Examples:
  - "Search for information about LangGraph"
  - "Create a file called notes.txt with hello world"
  - "List all files in the current directory"
  - "Analyze the topic of artificial intelligence"
    """
    print(help_text)


def list_agents():
    """List all registered agents."""
    registry = AgentRegistry()
    agents = registry.get_all_agents()

    print(f"\n📋 Registered Agents ({len(agents)}):\n")

    for agent in agents:
        print(f"  🤖 {agent.name}")
        print(f"     Description: {agent.description}")
        print(f"     Capabilities: {', '.join(agent.capabilities[:5])}")
        if len(agent.capabilities) > 5:
            print(f"                   ... and {len(agent.capabilities) - 5} more")
        print()


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Main application loop."""
    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in a .env file or export it in your shell.\n")
        return

    # Print banner
    print_banner()

    # Initialize the supervisor workflow
    print("\n🔧 Initializing multi-agent system...")

    try:
        supervisor = SupervisorWorkflow(model="gpt-4o")
        app = supervisor.build()
    except Exception as e:
        print(f"\n❌ Error initializing system: {e}")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return

    print("\n✅ System ready! Type /help for commands or enter your request.\n")

    # Main interaction loop
    thread_id = "main_session"

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower()

                if command == "/exit" or command == "/quit":
                    print("\n👋 Goodbye!\n")
                    break

                elif command == "/help":
                    print_help()
                    continue

                elif command == "/agents":
                    list_agents()
                    continue

                elif command == "/clear":
                    clear_screen()
                    print_banner()
                    continue

                else:
                    print(f"Unknown command: {user_input}")
                    print("Type /help for available commands.")
                    continue

            # Execute the request through the supervisor
            print("\n" + "="*60)

            try:
                result = supervisor.invoke(user_input, thread_id=thread_id)

                # The output is already printed by the supervisor
                # Just add spacing for readability

            except Exception as e:
                print(f"\n❌ Error executing request: {e}")
                print("Please try again or type /help for assistance.\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            print("Please try again or type /help for assistance.\n")


if __name__ == "__main__":
    main()
