# Examples

This directory contains working examples to help you learn and extend the multi-agent system.

## Available Examples

### 1. add_custom_agent.py

A complete, runnable example showing how to add a new agent to the system.

**What it demonstrates:**
- Creating custom tools with `@tool`
- Building a new agent class (MathAgent)
- Using the `@AgentRegistry.register` decorator
- Testing the new agent with the supervisor

**Run it:**
```bash
python examples/add_custom_agent.py
```

**What you'll see:**
- Math Agent being registered
- Supervisor building with all agents
- Test requests being routed to the Math Agent
- Calculations and unit conversions being performed

## Creating Your Own Examples

Feel free to create your own example files in this directory! Here's a template:

```python
"""
Example: [Your Example Name]

Description of what this example demonstrates.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from core.supervisor import SupervisorWorkflow
import agents

load_dotenv()

# Your example code here

if __name__ == "__main__":
    print("Running example...")
    # Your test code
```

## Ideas for More Examples

Here are some ideas for additional examples you could create:

### Email Agent Example
```python
# examples/email_agent_example.py
# - Create an agent that handles email operations
# - Tools: send_email, read_email, search_inbox
# - Show how to integrate with email APIs
```

### Database Agent Example
```python
# examples/database_agent_example.py
# - Create an agent for database operations
# - Tools: query_db, insert_record, update_record
# - Demonstrate SQL generation and execution
```

### API Integration Example
```python
# examples/api_agent_example.py
# - Create an agent that calls external APIs
# - Tools: fetch_data, post_data, parse_response
# - Show authentication and error handling
```

### Multi-Agent Workflow Example
```python
# examples/multi_agent_workflow.py
# - Demonstrate agents working together
# - Research Agent → finds information
# - File Operations Agent → saves results
# - Show state passing between agents
```

### Custom Routing Logic Example
```python
# examples/custom_routing.py
# - Implement sophisticated can_handle() logic
# - Use regex, NLP, or other techniques
# - Show confidence score calculation
```

## Learning Path

1. **Start Here**: Read through `add_custom_agent.py`
2. **Understand**: Follow the code comments and structure
3. **Experiment**: Modify the Math Agent to add new capabilities
4. **Build**: Create your own agent from scratch
5. **Share**: Add your examples to help others learn!

## Tips

- **Keep it focused**: Each example should demonstrate one concept clearly
- **Add comments**: Explain what each part does and why
- **Include tests**: Show how to verify the agent works
- **Error handling**: Demonstrate proper error management
- **Documentation**: Add a docstring explaining the example

## Need Help?

- Check the [Tutorial](../docs/TUTORIAL.md) for detailed guidance
- Review the [Architecture docs](../docs/ARCHITECTURE.md) for design patterns
- Look at existing agents in `src/agents/` for inspiration

Happy learning! 🚀
