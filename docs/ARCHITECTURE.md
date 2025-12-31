# Architecture Documentation

A deep dive into the design and implementation of the multi-agent system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Design Patterns](#design-patterns)
3. [Component Diagrams](#component-diagrams)
4. [Data Flow](#data-flow)
5. [State Management](#state-management)
6. [Extensibility Points](#extensibility-points)
7. [Performance Considerations](#performance-considerations)

---

## System Overview

### Architecture Principles

The system is built on four core principles:

1. **Modularity**: Each component has a single, well-defined responsibility
2. **Extensibility**: New agents can be added without modifying existing code
3. **Discoverability**: Agents are automatically registered and discoverable
4. **Clarity**: Explicit state flow through LangGraph for easy debugging

### Technology Stack

```
┌─────────────────────────────────────────┐
│  Application Layer                      │
│  • CLI Interface (main.py)              │
│  • User interaction handling            │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│  Orchestration Layer                    │
│  • LangGraph StateGraph                 │
│  • Supervisor workflow                  │
│  • Dynamic routing                      │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│  Agent Layer                            │
│  • BaseAgent abstract class             │
│  • Concrete agent implementations       │
│  • AgentRegistry singleton              │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│  Tool Layer                             │
│  • LangChain @tool decorators           │
│  • Reusable tool functions              │
└──────────────┬──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│  Foundation Layer                       │
│  • LangChain (agent framework)          │
│  • LangGraph (workflow engine)          │
│  • OpenAI (LLM provider)                │
└─────────────────────────────────────────┘
```

---

## Design Patterns

### 1. Registry Pattern

**Purpose**: Decouple agent registration from supervisor logic

**Implementation**:
```python
class AgentRegistry:
    _instance = None
    _agents: Dict[str, BaseAgent] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, agent_class: Type[BaseAgent]):
        agent_instance = agent_class()
        cls._agents[agent_instance.name] = agent_instance
        return agent_class
```

**Benefits**:
- Agents self-register at import time
- No manual registration required
- Supervisor automatically discovers all agents
- Easy to add/remove agents

**Usage**:
```python
@AgentRegistry.register  # Automatic registration
class MyAgent(BaseAgent):
    pass
```

### 2. Strategy Pattern

**Purpose**: Define a family of interchangeable agent algorithms

**Implementation**:
```python
class BaseAgent(ABC):
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Strategy execution method"""
        pass
```

**Benefits**:
- Agents can be swapped at runtime
- Common interface for all agents
- Supervisor doesn't need to know agent internals
- Easy to test individual strategies

### 3. Command Pattern

**Purpose**: Encapsulate routing decisions as commands

**Implementation**:
```python
return Command(
    update={"current_agent": "research"},  # State update
    goto="research"  # Routing decision
)
```

**Benefits**:
- Declarative routing
- State updates and navigation in one call
- LangGraph handles execution flow
- Clear separation of routing logic

### 4. Factory Pattern

**Purpose**: Create agent instances through the registry

**Implementation**:
```python
def get_agent(cls, name: str) -> Optional[BaseAgent]:
    return cls._agents.get(name)
```

**Benefits**:
- Centralized agent creation
- No direct instantiation needed
- Registry acts as factory
- Easy to mock for testing

### 5. Template Method Pattern

**Purpose**: Define skeleton of agent execution

**Implementation**:
```python
class BaseAgent(ABC):
    def execute(self, state):
        # Template method that subclasses implement
        pass

    def can_handle(self, request):
        # Hook with default implementation
        return 0.5
```

**Benefits**:
- Common structure for all agents
- Subclasses customize specific steps
- Default implementations for optional methods

---

## Component Diagrams

### 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  CLI Loop                                            │  │
│  │  • Read user input                                   │  │
│  │  • Handle commands (/help, /exit, /agents)          │  │
│  │  • Call supervisor.invoke()                          │  │
│  │  • Display results                                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    supervisor.py                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  SupervisorWorkflow                                  │  │
│  │                                                      │  │
│  │  build() → Create StateGraph:                       │  │
│  │    START → route_request → [agents] → finalize      │  │
│  │                                                      │  │
│  │  invoke(input) → Execute workflow                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               agent_registry.py                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AgentRegistry (Singleton)                           │  │
│  │                                                      │  │
│  │  _agents = {                                         │  │
│  │    "research": ResearchAgent(),                      │  │
│  │    "file_operations": FileOperationsAgent(),         │  │
│  │    ...                                               │  │
│  │  }                                                   │  │
│  │                                                      │  │
│  │  Methods:                                            │  │
│  │  • register(agent_class) → decorator                │  │
│  │  • get_agent(name) → agent instance                 │  │
│  │  • get_all_agents() → list of agents                │  │
│  └──────────────────┬───────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  base_agent.py                              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  BaseAgent (ABC)                                     │  │
│  │                                                      │  │
│  │  Abstract:                                           │  │
│  │  • name: str                                         │  │
│  │  • description: str                                  │  │
│  │  • capabilities: List[str]                           │  │
│  │  • get_tools() → List[BaseTool]                      │  │
│  │  • execute(state) → Dict                             │  │
│  │                                                      │  │
│  │  Concrete:                                           │  │
│  │  • can_handle(request) → float                       │  │
│  └──────────────────┬───────────────────────────────────┘  │
└─────────────────────┼───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            agents/*.py (Implementations)                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Research     │  │ File Ops     │  │ Your Custom      │ │
│  │ Agent        │  │ Agent        │  │ Agent            │ │
│  │              │  │              │  │                  │ │
│  │ • web_search │  │ • read_file  │  │ • custom_tools   │ │
│  │ • summarize  │  │ • write_file │  │                  │ │
│  │ • analyze    │  │ • list_files │  │                  │ │
│  └──────────────┘  └──────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. Agent Registration Flow

```
┌───────────────────────────────────────────────────────────┐
│  Step 1: Agent Class Definition                          │
│                                                           │
│  @AgentRegistry.register  ← Decorator applied             │
│  class MyAgent(BaseAgent):                                │
│      ...                                                  │
└────────────────────────┬──────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────┐
│  Step 2: Decorator Execution                              │
│                                                           │
│  1. agent_class passed to register()                      │
│  2. agent_instance = agent_class()                        │
│  3. _agents[name] = agent_instance                        │
│  4. return agent_class (for chaining)                     │
└────────────────────────┬──────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────┐
│  Step 3: Registry State                                   │
│                                                           │
│  AgentRegistry._agents = {                                │
│      "my_agent": MyAgent instance                         │
│  }                                                        │
└────────────────────────┬──────────────────────────────────┘
                         │
                         ▼
┌───────────────────────────────────────────────────────────┐
│  Step 4: Agent Discovery                                  │
│                                                           │
│  supervisor.build():                                      │
│    agents = registry.get_all_agents()                     │
│    for agent in agents:                                   │
│        workflow.add_node(agent.name, create_node(agent))  │
└───────────────────────────────────────────────────────────┘
```

### 3. Request Flow Sequence

```
User Input: "Search for LangGraph docs"
        │
        ▼
┌───────────────────────┐
│   main.py             │
│   supervisor.invoke() │
└───────┬───────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   supervisor.py                       │
│   START → route_request node          │
│                                       │
│   1. Get all agents from registry     │
│   2. Build routing prompt:            │
│      "Available: research, file_ops"  │
│      "User wants: search for docs"    │
│   3. LLM selects: "research"          │
│   4. Command(goto="research")         │
└───────┬───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   research agent node                 │
│                                       │
│   1. agent = registry.get("research") │
│   2. result = agent.execute(state)    │
│   3. Command(goto="finalize")         │
└───────┬───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   research_agent.py                   │
│   ResearchAgent.execute()             │
│                                       │
│   1. Create agent executor            │
│   2. agent_executor.invoke(input)     │
│   3. Agent uses web_search tool       │
│   4. Return {agent_output: result}    │
└───────┬───────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│   finalize node                       │
│                                       │
│   1. Format output                    │
│   2. Print result                     │
│   3. END                              │
└───────┬───────────────────────────────┘
        │
        ▼
    User sees result
```

---

## Data Flow

### State Transitions

```
Initial State:
{
    "messages": [],
    "user_input": "Search for LangGraph",
    "current_agent": None,
    "agent_output": None,
    "next_action": None,
    "task_complete": False,
    "metadata": {}
}
        │
        ▼ [route_request node]
{
    "messages": [],
    "user_input": "Search for LangGraph",
    "current_agent": "research",  ← Updated
    "agent_output": None,
    "next_action": "execute_research",  ← Updated
    "task_complete": False,
    "metadata": {}
}
        │
        ▼ [research agent node]
{
    "messages": [],
    "user_input": "Search for LangGraph",
    "current_agent": "research",
    "agent_output": "LangGraph is...",  ← Updated
    "next_action": "execute_research",
    "task_complete": True,  ← Updated
    "metadata": {"agent": "research"}  ← Updated
}
        │
        ▼ [finalize node]
Final State (printed to user)
```

### State Update Methods

1. **Command.update**: Merge updates into state
   ```python
   Command(update={"field": "value"})
   ```

2. **Return dict**: Update state from node
   ```python
   def node(state):
       return {"field": "new_value"}
   ```

---

## State Management

### LangGraph State Features

1. **TypedDict Schema**: Type-safe state definition
2. **Automatic Merging**: Updates merge with existing state
3. **Persistence**: MemorySaver checkpointer for conversation history
4. **Thread Isolation**: Each conversation has separate state

### State Best Practices

1. **Minimal State**: Only store what's needed
2. **Immutable Updates**: Don't modify state directly, return updates
3. **Clear Naming**: Use descriptive field names
4. **Optional Fields**: Use Optional[T] for nullable fields

---

## Extensibility Points

### 1. Adding New Agents

**Minimal Required Changes**:
- Create agent class file
- Import in `agents/__init__.py`

**No Changes Needed In**:
- Supervisor logic
- Registry implementation
- Main application
- Other agents

### 2. Adding New Tools

**Steps**:
1. Create tool function with `@tool`
2. Add to agent's `get_tools()`

**Automatic Benefits**:
- LLM can use the tool
- Tool shows in agent description
- Error handling included

### 3. Custom Routing Logic

**Override Methods**:
```python
def can_handle(self, request: str) -> float:
    # Custom confidence calculation
    return confidence_score
```

### 4. State Extensions

**Add New Fields**:
```python
class ExtendedState(AgentState):
    custom_field: Optional[str]
    another_field: List[int]
```

---

## Performance Considerations

### 1. Agent Initialization

**Lazy Loading**: Agents initialize LLM only when first executed
```python
if self.agent_executor is None:
    self.agent_executor = self._create_agent_executor()
```

**Benefits**:
- Faster startup
- Lower memory usage
- Only active agents consume resources

### 2. LLM Calls

**Optimization Strategies**:
- Use `gpt-4o-mini` for simple tasks
- Set `temperature=0` for deterministic results
- Limit `max_iterations` in agent executors

### 3. Caching

**Opportunities**:
- Cache agent executor instances
- Cache LLM responses for repeated queries
- Cache tool results when appropriate

### 4. Parallel Execution

**Future Enhancement**:
- Execute independent agents in parallel
- Batch tool calls when possible
- Use async/await for I/O operations

---

## Security Considerations

### 1. Input Validation

**Implemented**:
- File path validation in file tools
- Expression safety in calculation tools

**Best Practices**:
- Validate all user inputs
- Sanitize file paths
- Limit tool capabilities

### 2. API Key Management

**Current Approach**:
- Environment variables via `.env`
- Keys not committed to repository

**Recommendations**:
- Use secret management systems in production
- Rotate keys regularly
- Limit key permissions

### 3. Tool Permissions

**Design Principle**:
- Tools have minimal required permissions
- No destructive operations without confirmation
- Clear error messages for failures

---

## Testing Strategy

### 1. Unit Tests

**Coverage**:
- Individual tools
- Agent initialization
- Registry operations
- State management

### 2. Integration Tests

**Coverage**:
- Full workflow execution
- Agent routing
- Multi-step operations

### 3. Manual Testing

**Approach**:
- Interactive CLI testing
- Example scripts
- Edge case scenarios

---

## Future Enhancements

### Potential Improvements

1. **Conversation Memory**: Multi-turn conversations with context
2. **Agent Collaboration**: Agents calling other agents
3. **Streaming Responses**: Real-time output as agents work
4. **Web Interface**: GUI instead of CLI
5. **Agent Metrics**: Track performance and usage
6. **Config-Based Agents**: Define simple agents in YAML/JSON
7. **Plugin System**: Load agents from external packages
8. **Error Recovery**: Retry logic and fallback strategies

---

## Conclusion

This architecture provides:

✅ **Clean Separation**: Each component has a clear responsibility
✅ **Easy Extension**: Add agents without modifying core code
✅ **Type Safety**: TypedDict and abstract base classes
✅ **Testability**: Each component can be tested independently
✅ **Visibility**: Explicit state flow through LangGraph
✅ **Flexibility**: Multiple extension points for customization

The system demonstrates enterprise-grade patterns while remaining accessible for learning and experimentation.
