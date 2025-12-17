# Multi-Agent System Documentation

## Overview

MetaPersona's multi-agent system allows you to create, manage, and coordinate multiple specialized AI agents. Each agent has unique capabilities, skills, and can handle specific types of tasks. The system automatically routes tasks to the most suitable agent.

## Key Concepts

### 1. **BaseAgent**
The foundation class for all agents in the system. Every agent inherits from `BaseAgent` and must implement:
- **Capabilities**: What the agent is good at
- **Task Handler**: How to execute tasks
- **Task Evaluator**: Confidence scoring for task suitability

### 2. **Agent Registry**
Central hub for managing all agents:
- Register and deregister agents
- Discover agents by ID or role
- Track agent status and performance
- Persist agent metadata

### 3. **Task Router**
Intelligent routing engine with **LLM-enhanced decision making** that:
- Analyzes tasks using keyword matching AND LLM intent analysis
- Understands context, verb tense, and actual user intent
- Scores all agents for task suitability (0.0-1.0 confidence)
- Selects the best agent automatically
- Tracks routing decisions and analytics
- Supports manual agent selection

> 🧠 **New in v2.0**: LLM-powered routing goes beyond keyword matching to understand what you actually want. See [INTELLIGENT_ROUTING.md](./INTELLIGENT_ROUTING.md) for details.

## Built-in Specialized Agents

### ResearchAgent
**Role:** `researcher`  
**Specialization:** Information gathering, analysis, and research

**Capabilities:**
- Web research and information retrieval
- Data analysis and summarization
- Fact-checking and verification

**Best for:**
- "Research the history of AI"
- "Find information about quantum computing"
- "Analyze trends in machine learning"

### CodeAgent
**Role:** `coder`  
**Specialization:** Programming, debugging, and technical tasks

**Capabilities:**
- Code writing in multiple languages
- Code review and optimization
- Technical explanations
- Debugging assistance

**Best for:**
- "Write a Python function to sort a list"
- "Debug this code snippet"
- "Explain how binary search works"

### WriterAgent
**Role:** `writer`  
**Specialization:** Content creation and communication

**Capabilities:**
- Creative writing (stories, content)
- Professional writing (emails, reports)
- Editing and proofreading

**Best for:**
- "Write a professional email"
- "Draft a blog post about AI"
- "Edit this paragraph for clarity"

### GeneralistAgent
**Role:** `generalist`  
**Specialization:** General tasks and conversations

**Capabilities:**
- General assistance
- Natural conversation
- Fallback for unmatched tasks

**Best for:**
- General questions
- Casual conversation
- Tasks that don't fit other categories

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Input                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Task Router                            │
│  • Analyzes task requirements                               │
│  • Scores all agents (confidence 0.0-1.0)                   │
│  • Selects best match                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Registry                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ Researcher  │  │    Coder    │  │   Writer    │  ...   │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Selected Agent                           │
│  • Uses skills (web_search, file_ops, etc.)                 │
│  • Calls LLM provider                                       │
│  • Updates memory                                           │
│  • Returns TaskResult                                       │
└─────────────────────────────────────────────────────────────┘
```

## Usage

### CLI Commands

#### List All Agents
```bash
python metapersona.py agents-list --data-dir ./data
```

Shows all registered agents with their roles, capabilities, and interaction counts.

#### View Agent Status
```bash
# View all agents
python metapersona.py agents-status

# View specific agent
python metapersona.py agents-status --agent-id researcher
```

Shows detailed information about agents including capabilities, skills, and statistics.

#### Route a Task
```bash
# Execute task with automatic routing
python metapersona.py route-task "Research quantum computing"

# Explain routing without executing
python metapersona.py route-task "Write a Python function" --explain
```

Routes the task to the best agent and optionally executes it.

#### Multi-Agent Chat
```bash
python metapersona.py multi-agent-chat
```

Interactive chat session with automatic agent routing. Commands:
- `agents` - List registered agents
- `stats` - Show routing statistics
- `exit` - Quit the chat

### Python API

#### Basic Usage

```python
from pathlib import Path
from src.agent_registry import AgentRegistry
from src.task_router import TaskRouter
from src.specialized_agents import ResearchAgent, CodeAgent
from src.llm_provider import get_llm_provider
from src.skills_system import SkillsManager

# Initialize components
registry = AgentRegistry(Path("./data"))
llm_provider = get_llm_provider()
skills_manager = SkillsManager()

# Register agents
researcher = ResearchAgent(
    agent_id="researcher",
    role="researcher",
    description="Research specialist",
    llm_provider=llm_provider,
    skills_manager=skills_manager
)
registry.register(researcher)

coder = CodeAgent(
    agent_id="coder",
    role="coder",
    description="Coding specialist",
    llm_provider=llm_provider,
    skills_manager=skills_manager
)
registry.register(coder)

# Create router
router = TaskRouter(registry, default_agent_id="researcher")

# Route and execute task
import asyncio
result = asyncio.run(router.execute_task("Research AI trends"))

if result.success:
    print(result.result)
else:
    print(f"Error: {result.error}")
```

#### Explain Routing Decision

```python
# Analyze routing without executing
explanation = router.explain_routing("Write a Python function")

print(f"Recommended: {explanation['recommended_agent']}")
print(f"Confidence: {explanation['recommended_confidence']}")

for candidate in explanation['all_candidates']:
    print(f"  {candidate['agent_id']}: {candidate['confidence']}")
```

#### Manual Agent Selection

```python
# Route to specific agent
result = await router.execute_task(
    "Some task",
    agent_id="coder"  # Force specific agent
)

# Or by role
result = await router.execute_task(
    "Some task",
    preferred_role="writer"  # Prefer specific role
)
```

#### Access Routing Statistics

```python
stats = router.get_routing_stats()

print(f"Total routes: {stats['total_routes']}")
print(f"Average confidence: {stats['average_confidence']}")
print(f"Most used: {stats['most_used_agent']}")
print(f"Agent usage: {stats['agent_usage']}")
```

## Creating Custom Agents

### Step 1: Define Your Agent Class

```python
from typing import Dict, List, Any, Optional
from src.agent_base import BaseAgent, AgentCapability, TaskResult

class MyCustomAgent(BaseAgent):
    """Custom agent for specific tasks."""
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """Define what this agent can do."""
        return [
            AgentCapability(
                name="my_capability",
                description="Description of what I can do",
                confidence=0.9,
                examples=["example task", "another example"]
            )
        ]
    
    def can_handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Return confidence score (0.0-1.0) for handling this task.
        Higher score = better match.
        """
        task_lower = task.lower()
        
        # Check for keywords
        if "my keyword" in task_lower:
            return 0.9  # High confidence
        elif "related keyword" in task_lower:
            return 0.6  # Medium confidence
        
        return 0.2  # Low confidence
    
    async def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute the task."""
        try:
            # Get LLM response
            system_prompt = self.get_system_prompt()
            response = await self.llm_provider.generate(
                prompt=task,
                system_prompt=system_prompt
            )
            
            # Record interaction
            self.update_memory({
                "task": task,
                "response": response[:200]
            })
            
            return TaskResult(
                success=True,
                result=response,
                metadata={
                    "agent_id": self.agent_id,
                    "role": self.role
                }
            )
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=str(e)
            )
```

### Step 2: Register Your Agent

```python
from src.agent_registry import AgentRegistry
from src.llm_provider import get_llm_provider
from src.skills_system import SkillsManager

registry = AgentRegistry()
llm_provider = get_llm_provider()
skills_manager = SkillsManager()

my_agent = MyCustomAgent(
    agent_id="my_agent",
    role="specialist",
    description="My custom specialized agent",
    llm_provider=llm_provider,
    skills_manager=skills_manager
)

registry.register(my_agent)
```

### Step 3: Use Your Agent

```python
from src.task_router import TaskRouter

router = TaskRouter(registry)

# Your agent will now be considered for all tasks
result = await router.execute_task("Task for my agent")
```

## Advanced Features

### Agent Memory

Every agent maintains memory of interactions:

```python
# Access agent memory
agent = registry.get("researcher")
print(f"Total interactions: {len(agent.memory.interactions)}")
print(f"Learnings: {agent.memory.learnings}")

# Get recent context
recent = agent.get_recent_context(limit=5)
for interaction in recent:
    print(interaction)

# Add learning
agent.update_memory(
    interaction={"task": "Some task", "result": "Success"},
    learning="Learned something new"
)
```

### Skills Integration

Agents can use skills for enhanced capabilities:

```python
from src.skills_system import SkillsManager

skills_manager = SkillsManager()
skills_manager.discover_skills()  # Load all skills

agent = ResearchAgent(
    agent_id="researcher",
    role="researcher",
    description="Research specialist",
    llm_provider=llm_provider,
    skills_manager=skills_manager  # Agent now has skills
)

# Agent can use web_search, file_operations, etc.
result = await agent.handle_task(
    "Search for Python tutorials",
    use_skills=True  # Enable skill usage
)
```

### Routing Configuration

```python
# Custom confidence threshold
router = TaskRouter(
    registry,
    min_confidence=0.7  # Only route if confidence >= 0.7
)

# Default fallback agent
router = TaskRouter(
    registry,
    default_agent_id="generalist"  # Use this if no match
)
```

### Monitoring & Analytics

```python
# Recent routing decisions
recent_routes = router.get_recent_routes(limit=10)
for route in recent_routes:
    print(f"{route['task']} -> {route['selected_agent_id']}")

# Agent status
status = agent.get_status()
print(f"Agent: {status['agent_id']}")
print(f"Interactions: {status['interactions_count']}")
print(f"Skills: {status['skills_count']}")
```

## Best Practices

### 1. **Specific Capabilities**
Define clear, specific capabilities for your agents:
```python
# Good
AgentCapability(
    name="python_coding",
    description="Write Python code for data processing",
    confidence=0.9
)

# Too vague
AgentCapability(
    name="coding",
    description="Write code",
    confidence=0.5
)
```

### 2. **Accurate Confidence Scoring**
Return honest confidence scores in `can_handle_task()`:
- 0.9-1.0: Perfect match, agent is ideal
- 0.7-0.8: Good match, agent can handle well
- 0.5-0.6: Moderate match, agent can try
- <0.5: Poor match, agent should not handle

### 3. **Use System Prompts**
Leverage `get_system_prompt()` for consistent agent behavior:
```python
system_prompt = self.get_system_prompt()
system_prompt += "\n\nAdditional instructions for this task type."
```

### 4. **Record Interactions**
Always update memory after handling tasks:
```python
self.update_memory(
    interaction={
        "task": task,
        "result": result,
        "success": True
    },
    learning="Optional learning from this interaction"
)
```

### 5. **Error Handling**
Always wrap task execution in try-except:
```python
try:
    result = await self.llm_provider.generate(...)
    return TaskResult(success=True, result=result)
except Exception as e:
    return TaskResult(success=False, error=str(e))
```

## Troubleshooting

### No Agent Found
**Problem:** Router can't find suitable agent  
**Solution:** 
- Lower `min_confidence` threshold
- Add a `default_agent_id` fallback
- Register more specialized agents

### Wrong Agent Selected
**Problem:** Tasks routed to incorrect agent  
**Solution:**
- Improve `can_handle_task()` logic
- Add more specific keywords
- Adjust confidence scores

### Agent Not Registered
**Problem:** `Agent not found` error  
**Solution:**
```python
# Check if registered
if "my_agent" in registry:
    print("Agent is registered")
else:
    print("Need to register agent")
```

## Examples

See `examples/multi_agent_demo.py` for comprehensive demonstrations:
- Basic task routing
- Routing explanations
- Agent collaboration
- Statistics and analytics
- Agent status monitoring

Run the demo:
```bash
python examples/multi_agent_demo.py
```

## API Reference

### BaseAgent
- `can_handle_task(task, context) -> float`
- `handle_task(task, context, use_skills) -> TaskResult`
- `get_system_prompt() -> str`
- `update_memory(interaction, learning)`
- `get_status() -> Dict`

### AgentRegistry
- `register(agent) -> bool`
- `deregister(agent_id) -> bool`
- `get(agent_id) -> Agent`
- `get_by_role(role) -> List[Agent]`
- `list_all() -> List[Agent]`
- `get_status() -> Dict`

### TaskRouter
- `route_task(task, context, preferred_role, agent_id) -> Agent`
- `execute_task(task, ...) -> TaskResult`
- `explain_routing(task, context) -> Dict`
- `get_routing_stats() -> Dict`
- `get_recent_routes(limit) -> List[Dict]`

## Next Steps

1. **Create Custom Agents**: Build agents for your specific use cases
2. **Integrate Skills**: Give agents tools to enhance capabilities
3. **Monitor Performance**: Use analytics to optimize routing
4. **Scale Up**: Add more agents as needs grow

For more information, see:
- `SKILLS.md` - Skills system documentation
- `README.md` - Main documentation
- `examples/` - Example code
