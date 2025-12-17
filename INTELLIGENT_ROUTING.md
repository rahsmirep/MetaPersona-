# Intelligent Task Routing

MetaPersona v2.0 features an advanced **LLM-based routing system** that goes beyond simple keyword matching to understand task intent and select the most appropriate agent.

## 🧠 How It Works

### Traditional Keyword Routing (Baseline)
Each agent defines keywords and patterns:
- **ResearchAgent**: "research", "search for", "find information"
- **CodeAgent**: "write code", "function", "python", "javascript"
- **WriterAgent**: "write email", "draft letter", "article"
- **GeneralistAgent**: Fallback with lower confidence

**Problem**: Simple keyword matching can be confused:
- "I researched Python yesterday" → Should NOT route to ResearchAgent (past tense)
- "Write an email about my research" → Should route to WriterAgent, not ResearchAgent
- "Can you help me write code?" → "write" + "code" = CodeAgent, but basic matching might confuse with WriterAgent

### Enhanced LLM Routing (Intelligent)
The system now uses a two-stage approach:

1. **Initial Scoring**: Agents evaluate the task using their `can_handle_task()` method with keyword/pattern matching
2. **LLM Analysis**: If enabled, the LLM analyzes:
   - **Task Intent**: What does the user actually want?
   - **Expected Output**: Code, documentation, research, or conversation?
   - **Verb Tense**: Is it asking to DO something or just mentioning it?
   - **Context Clues**: Complexity, domain, and specific requirements

The LLM provides:
- Analysis of task intent
- Recommended agent with reasoning
- Confidence adjustment (-0.3 to +0.3) to refine scores

## 🎯 Examples

### Example 1: Research vs Past Mention
```bash
Task: "I researched Python yesterday and want to share findings"
```

**Keyword Routing**: Sees "researched" → High confidence for ResearchAgent
**LLM Routing**: 
- Detects past tense → User already did research
- Detects "share findings" → User wants to write/communicate
- **Adjusts**: Reduces research confidence, maintains writer confidence
- **Result**: Routes to appropriate agent based on actual intent

### Example 2: Writing About Research
```bash
Task: "Write an email to my professor about my research findings"
```

**Keyword Routing**: Sees "research" → Might route to ResearchAgent
**LLM Routing**:
- Primary verb: "Write an email" → WriterAgent territory
- "research findings" is just the topic, not the task
- **Result**: Routes to WriterAgent (0.95 confidence)

### Example 3: Code Writing
```bash
Task: "Can you write a Python function to calculate fibonacci?"
```

**Keyword Routing**: Sees "write" + "Python" + "function" → High confidence
**LLM Routing**:
- Confirms intent: Create code
- Validates domain: Programming task
- **Result**: Routes to CodeAgent (0.95+ confidence)

## 🔧 Configuration

### Enable/Disable LLM Routing
```python
from src.task_router import TaskRouter
from src.llm_provider import LLMProvider

llm_provider = LLMProvider(model="llama3.2:latest")

# Enable intelligent routing (default)
router = TaskRouter(
    registry,
    llm_provider=llm_provider,
    use_llm_routing=True  # <-- LLM-enhanced routing
)

# Disable for keyword-only routing
router = TaskRouter(
    registry,
    llm_provider=llm_provider,
    use_llm_routing=False  # <-- Keyword matching only
)
```

### Confidence Threshold
```python
router = TaskRouter(
    registry,
    min_confidence=0.5,  # Only route if confidence >= 0.5
    llm_provider=llm_provider
)
```

## 📊 Routing Process

```
┌─────────────────┐
│   User Task     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Keyword Scoring │  ← Each agent scores 0.0-1.0
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LLM Analysis   │  ← Analyzes intent & context
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Adjust Scores   │  ← Refines confidence scores
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Select Best    │  ← Highest confidence wins
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Execute Task   │
└─────────────────┘
```

## 🎨 CLI Usage

### Explain Routing Decision
```bash
python metapersona.py route-task "your task here" --explain
```

Shows:
- Recommended agent with confidence
- All candidate agents with scores
- Whether each meets the confidence threshold

### Execute with Routing
```bash
python metapersona.py route-task "your task here"
```

Routes and executes immediately.

### Multi-Agent Chat
```bash
python metapersona.py multi-agent-chat
```

Interactive chat with automatic routing:
- Type your message → System routes to best agent
- Type `stats` → View routing analytics
- Type `agents` → List available agents

## 🧪 Testing Scenarios

### Ambiguous Tasks
```python
# Test cases that benefit from LLM routing:
tasks = [
    "I need to research quantum computing",  # ResearchAgent
    "I researched quantum computing yesterday",  # GeneralistAgent (past tense)
    "Write a report on quantum computing research",  # WriterAgent
    "Write code to simulate quantum gates",  # CodeAgent
    "Explain how quantum computing works",  # GeneralistAgent (explanation)
]

for task in tasks:
    explanation = router.explain_routing(task)
    print(f"Task: {task}")
    print(f"Routed to: {explanation['recommended_agent']}")
    print(f"Confidence: {explanation['recommended_confidence']}\n")
```

## 📈 Benefits

### Traditional Keyword Matching
✅ Fast and lightweight
✅ Predictable behavior
❌ Can be confused by similar keywords
❌ Doesn't understand context or intent
❌ Limited to pattern matching

### LLM-Enhanced Routing
✅ **Understands task intent** beyond keywords
✅ **Contextual awareness** of what user wants
✅ **Handles ambiguous tasks** intelligently
✅ **Verb tense detection** (do vs did)
✅ **Graceful fallback** if LLM fails
❌ Slightly slower (adds LLM call)
❌ Requires LLM provider

## 🎯 Best Practices

1. **Enable for Production**: LLM routing significantly improves accuracy
2. **Set Appropriate Thresholds**: `min_confidence=0.5` works well
3. **Monitor Analytics**: Use `stats` command to track routing patterns
4. **Use Explain Mode**: Test routing decisions with `--explain` flag
5. **Fallback Agent**: Always configure a generalist as default

## 🔍 Debugging

### View Routing Decision
```bash
python metapersona.py route-task "task" --explain
```

### Check Routing Stats
```python
stats = router.get_routing_stats()
print(f"Total routes: {stats['total_routes']}")
print(f"Average confidence: {stats['average_confidence']}")
print(f"Most used agent: {stats['most_used_agent']}")
```

### Test Without LLM
```python
# Disable LLM routing to see baseline keyword scoring
router = TaskRouter(registry, use_llm_routing=False)
```

## 🚀 Future Enhancements

Planned improvements:
- **Multi-agent collaboration**: Route to multiple agents for complex tasks
- **Learning from history**: Adapt routing based on user feedback
- **Custom routing rules**: User-defined routing logic
- **Confidence calibration**: Auto-tune confidence thresholds
- **A/B testing**: Compare routing strategies

## 📚 Related Documentation

- [MULTI_AGENT.md](./MULTI_AGENT.md) - Complete multi-agent system guide
- [README.md](./README.md) - Project overview
- [examples/multi_agent_demo.py](./examples/multi_agent_demo.py) - Routing examples

---

**MetaPersona v2.0** - Intelligent Multi-Agent System with Context-Aware Routing
