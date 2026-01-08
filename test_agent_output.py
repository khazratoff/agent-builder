import os
import sys
sys.path.insert(0, 'src')

from dotenv import load_dotenv
load_dotenv()

from agents.file_operations_agent import FileOperationsAgent

# Create agent
agent = FileOperationsAgent()

# Test state
test_state = {
    "user_input": "list files in current directory",
    "messages": [],
    "current_agent": None,
    "agent_output": None
}

print("Testing agent execution...")
print(f"Input: {test_state['user_input']}")

result = agent.execute(test_state)

print(f"\nResult keys: {result.keys()}")
print(f"Agent output type: {type(result.get('agent_output'))}")
print(f"Agent output content: {result.get('agent_output')}")
print(f"Agent output length: {len(str(result.get('agent_output')))}")
