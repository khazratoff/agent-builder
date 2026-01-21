# Conversation Memory Implementation

## Overview

The multi-agent system now maintains conversation history throughout the chat session, allowing agents to understand context from previous interactions.

## What Changed

### 1. Supervisor (`src/core/supervisor.py`)

#### `invoke()` method:
- **Before**: Always started with empty messages `[]`
- **After**: Retrieves existing conversation history from memory
- Appends new user input to the history
- Maintains context across multiple interactions

```python
# Get existing state from memory
existing_state = self.app.get_state(config)
if existing_state and existing_state.values:
    messages = existing_state.values.get("messages", [])
else:
    messages = []

# Add new user message
messages.append({
    "role": "user",
    "content": user_input
})
```

#### `_route_request()` method:
- Now includes conversation history in routing decisions
- Supervisor can see last 5 messages for context
- Routes agents based on current request AND conversation context

```python
# Build conversation history context
if len(messages) > 1:
    conversation_context = "\n\nConversation History:\n"
    recent_messages = messages[-6:-1]
    for msg in recent_messages:
        # Format and include in routing prompt
```

#### `_finalize()` method:
- Saves agent's response to conversation history
- Appends assistant message after each response

```python
# Add assistant's response to history
messages.append({
    "role": "assistant",
    "content": agent_output
})
```

### 2. Agents (`src/agents/*.py`)

Both `FileOperationsAgent` and `ResearchAgent` now:
- Retrieve conversation history from state
- Include last 3 exchanges (6 messages) for context
- Pass history to LLM when processing requests

```python
# Get conversation history
conversation_history = state.get("messages", [])

# Build messages with history
messages = [{"role": "system", "content": system_msg}]

if len(conversation_history) > 1:
    recent_history = conversation_history[-7:-1]
    messages.extend(recent_history)

messages.append({"role": "user", "content": user_input})
```

## How It Works

### Flow:

1. **User sends first message**
   ```
   User: "list files"
   → State: [{"role": "user", "content": "list files"}]
   → Agent executes and responds
   → State: [
       {"role": "user", "content": "list files"},
       {"role": "assistant", "content": "Here are the files: ..."}
     ]
   ```

2. **User sends follow-up**
   ```
   User: "read the first one"
   → System retrieves existing messages from memory
   → State: [
       {"role": "user", "content": "list files"},
       {"role": "assistant", "content": "Here are the files: ..."},
       {"role": "user", "content": "read the first one"}
     ]
   → Agent sees "the first one" refers to first file from previous list
   → Agent executes with full context
   ```

3. **Conversation continues**
   - Each exchange is saved
   - History is maintained within thread
   - Agents always have context

## Benefits

### 1. Follow-up Questions
```
User: "What files are here?"
Agent: "You have README.md, main.py, and config.py"

User: "Read the first one"
Agent: ✓ Knows "first one" = README.md (from context)
```

### 2. Clarification Flow
```
User: "Create a file"
Agent: "What should I name the file and what content should it have?"

User: "Call it notes.txt with hello world"
Agent: ✓ Understands this clarifies the previous request
```

### 3. Multi-step Tasks
```
User: "Research Python web frameworks"
Agent: "Here's info on Django, Flask, FastAPI..."

User: "Which one is best for beginners?"
Agent: ✓ Knows context is about the frameworks just discussed
```

## Memory Persistence

- **Thread-based**: Each `thread_id` maintains separate conversation
- **In-memory**: Uses LangGraph's `MemorySaver` (memory persists during runtime)
- **Session-scoped**: Memory cleared when app restarts

### Thread IDs

```python
# In main.py
thread_id = "main_session"  # Single session for CLI

# Could be extended for multi-user:
thread_id = f"user_{user_id}"  # Separate history per user
```

## Context Window Management

To prevent token overflow, only recent history is included:

- **Routing**: Last 5 messages (2-3 exchanges)
- **Agents**: Last 6 messages (3 exchanges)
- **Total**: Typically 6-7 messages max in any single request

This balances:
- ✓ Sufficient context for understanding
- ✓ Reasonable token usage
- ✓ Fast response times

## Example Scenarios

### Scenario 1: File Operations with Context
```
User: "list files in the current directory"
Agent: [Lists files including README.md, main.py, config.py]

User: "read README.md"
Agent: [Reads and returns README.md content]

User: "now read main.py"
Agent: ✓ Continues from context, reads main.py

User: "create a backup of the first file"
Agent: ✓ Knows "first file" = README.md from earlier context
```

### Scenario 2: Research with Follow-ups
```
User: "what is LangGraph?"
Agent: [Explains LangGraph]

User: "how does it compare to LangChain?"
Agent: ✓ Understands comparison is about LangGraph from context

User: "give me code examples"
Agent: ✓ Provides LangGraph examples, not generic code
```

### Scenario 3: Elaboration After Questions
```
User: "help me with files"
Agent: "What would you like to do with files? Read, write, list, delete?"

User: "list them"
Agent: ✓ Understands this elaborates on "files" request
       ✓ Lists files in directory
```

## Testing the Feature

Try these test cases:

### Test 1: Reference Previous Output
```bash
You: list files
You: read the first file
# Should work - agent remembers the file list
```

### Test 2: Clarification
```bash
You: create a file
# Agent asks for details
You: name it test.txt with content "hello"
# Should work - agent understands this is clarification
```

### Test 3: Multi-turn Research
```bash
You: tell me about Python
# Agent explains Python
You: what are its main frameworks?
# Should work - knows "its" = Python from context
```

## Configuration

### Adjust Context Window

In agents (`execute` method):

```python
# Currently: Last 6 messages (3 exchanges)
recent_history = conversation_history[-7:-1]

# For more context:
recent_history = conversation_history[-13:-1]  # 6 exchanges

# For less context:
recent_history = conversation_history[-3:-1]  # 1 exchange
```

### Adjust Supervisor Context

In supervisor (`_route_request` method):

```python
# Currently: Last 5 messages
recent_messages = messages[-6:-1]

# Adjust as needed
```

## Limitations

1. **In-memory only**: Doesn't persist after restart
2. **Single thread**: CLI uses one shared thread
3. **Fixed window**: Context window is hardcoded
4. **No pruning**: Very long conversations will grow indefinitely

## Future Enhancements

Possible improvements:
- Persistent storage (SQLite, Redis)
- Dynamic context window based on token count
- Conversation summarization for long histories
- Multi-user thread management
- Explicit conversation reset command

## Technical Details

### State Structure

```python
{
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."},
        {"role": "user", "content": "..."},
        ...
    ],
    "user_input": "current input",
    "current_agent": "agent_name",
    "agent_output": "last output",
    ...
}
```

### Memory Backend

Uses LangGraph's `MemorySaver`:
```python
memory = MemorySaver()
self.app = workflow.compile(checkpointer=memory)
```

### State Retrieval

```python
config = {"configurable": {"thread_id": thread_id}}
existing_state = self.app.get_state(config)
messages = existing_state.values.get("messages", [])
```

## Summary

✅ **Conversation memory is now fully functional**

The system:
- Maintains conversation history across interactions
- Provides context to agents for better understanding
- Handles follow-up questions and clarifications
- Manages context window to prevent overflow
- Uses thread-based isolation for future multi-user support

Try it out with follow-up questions and references to previous exchanges!
