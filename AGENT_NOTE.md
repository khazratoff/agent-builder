# Agent Implementation Note

## Current Simplified Approach

The agents in this simplified version use **LLM responses without actual tool execution**. This was done intentionally to keep the codebase simple and focused on learning core concepts.

### What the Agents Do

**FileOperationsAgent:**
- Routes correctly based on file-related keywords
- Describes what file operations it would perform
- Returns informative responses about file handling

**ResearchAgent:**
- Routes correctly based on research keywords
- Provides information and answers questions
- Returns helpful research-oriented responses

### Why No Tool Execution?

Implementing proper tool calling requires:
1. Tool invocation loop
2. Parsing tool calls from LLM responses
3. Executing tools and feeding results back
4. Handling tool errors and retries

This adds significant complexity that can obscure the core learning concepts of:
- Agent registry pattern
- Dynamic routing with supervisor
- State management with LangGraph
- Agent interface design

### The Output Issue (FIXED)

**Problem:** Agents were returning blank outputs

**Root Cause:** We were using `llm.bind_tools()` which returns an AIMessage with tool_calls, but we weren't:
1. Extracting the tool calls from the message
2. Actually invoking the tools
3. Getting results from tool execution

**Solution:** Simplified to direct LLM invocation:
```python
# Before (blank output):
result = self.agent_executor.invoke(...)  # Returns AIMessage with tool_calls
output = result.content  # Empty because content is blank when tools are called

# After (working):
result = self.llm.invoke(prompt)  # Direct LLM call
output = result.content  # Has actual response text
```

### For Real Tool Execution

If you want agents to actually execute tools, you need to:

1. **Option 1: Use LangChain's AgentExecutor** (but it's been deprecated)

2. **Option 2: Implement Manual Tool Loop**
   ```python
   messages = [{"role": "user", "content": user_input}]

   while True:
       result = llm_with_tools.invoke(messages)

       if not result.tool_calls:
           return result.content  # Done

       # Execute each tool
       for tool_call in result.tool_calls:
           tool = get_tool(tool_call["name"])
           tool_result = tool.invoke(tool_call["args"])
           messages.append({
               "role": "tool",
               "content": tool_result,
               "tool_call_id": tool_call["id"]
           })

       messages.append(result)  # Add AI response
   ```

3. **Option 3: Use LangGraph ReAct Agent** (more advanced)

### Learning Value

This simplified approach lets you focus on:
- ✓ How agents self-register
- ✓ How the supervisor routes requests
- ✓ How state flows through LangGraph
- ✓ How to add new agents easily

Without getting distracted by:
- ✗ Tool calling protocols
- ✗ Message formatting for tools
- ✗ Tool error handling
- ✗ Complex execution loops

### Testing the System

You can test that routing works correctly:

```bash
cd src && python main.py
```

Try these inputs:
- "List files in the current directory" → Routes to file_operations
- "What is LangGraph?" → Routes to research
- "Create a file called test.txt" → Routes to file_operations
- "Research artificial intelligence" → Routes to research

The agents will provide informative responses, and you'll see the routing is working correctly!

### Next Steps for Real Tool Execution

When you're ready to implement real tool execution:
1. Study the tool calling protocol in LangChain docs
2. Implement a simple tool loop (Option 2 above)
3. Test with one tool first
4. Gradually add more complex tool chains

The architecture is already set up correctly - you just need to enhance the `execute()` method in each agent!
