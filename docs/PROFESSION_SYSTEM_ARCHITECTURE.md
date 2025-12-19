# Universal Profession Understanding System (UPUS)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Input Layer                          │
│  (Natural language onboarding / Questions / Tasks)              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Onboarding Interpreter                          │
│  • NLP extraction                                                │
│  • Schema mapping                                                │
│  • Profession detection                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Profession Schema Store                       │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ • Role Definition      • Tools & Equipment           │      │
│  │ • Daily Tasks          • Environment Context         │      │
│  │ • Decision Patterns    • Safety Rules                │      │
│  │ • Terminology          • Skill Hierarchy             │      │
│  │ • Constraints          • Edge Cases                  │      │
│  └──────────────────────────────────────────────────────┘      │
└────────┬────────────────────────────────┬────────────────────────┘
         │                                │
         │ Knowledge Gap?                 │ Query Context
         ▼                                │
┌─────────────────────────────┐          │
│  Knowledge Expansion Layer  │          │
│  ┌───────────────────────┐  │          │
│  │  Query Generator      │  │          │
│  │  ↓                    │  │          │
│  │  Web Agent            │  │          │
│  │  (Google Custom API)  │  │          │
│  │  ↓                    │  │          │
│  │  Result Cleaner       │  │          │
│  │  ↓                    │  │          │
│  │  Schema Merger        │  │          │
│  └───────────────────────┘  │          │
└────────┬────────────────────┘          │
         │                                │
         └────────────┬───────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Reasoning Layer                             │
│  • Schema Context Injection                                      │
│  • User Persona Blending                                         │
│  • Professional Decision Logic                                   │
│  • Risk Assessment (profession-specific)                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Parallel-Self Alignment                         │
│  • Merge profession schema with user cognitive profile          │
│  • Style transfer (professional + personal)                     │
│  • Decision pattern harmonization                               │
│  • Output as "parallel you" in your profession                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Response Output                            │
│  (Contextually accurate, professionally sound, personally       │
│   aligned responses)                                            │
└─────────────────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Profession Schema (Universal Template)

**Purpose**: Represent any profession in a structured, queryable format.

**Schema Structure**:
```python
{
    "profession_id": "unique_id",
    "profession_name": "Software Engineer",
    "last_updated": "timestamp",
    
    "role_definition": {
        "primary_responsibilities": [...],
        "secondary_responsibilities": [...],
        "success_metrics": [...],
        "common_challenges": [...]
    },
    
    "daily_tasks": {
        "routine": [...],  # Regular daily activities
        "periodic": {...},  # Weekly/monthly tasks
        "situational": [...]  # Event-triggered tasks
    },
    
    "tools_equipment": {
        "software": [...],
        "hardware": [...],
        "platforms": [...],
        "methodologies": [...]
    },
    
    "environment": {
        "work_setting": "office/remote/hybrid/field",
        "team_structure": "solo/small team/large team",
        "pace": "fast/moderate/methodical",
        "autonomy_level": "high/medium/low"
    },
    
    "constraints": {
        "regulatory": [...],
        "time_sensitive": [...],
        "resource_limitations": [...],
        "ethical_considerations": [...]
    },
    
    "terminology": {
        "jargon": {...},  # Term: definition
        "acronyms": {...},
        "concepts": {...}
    },
    
    "decision_patterns": {
        "common_decisions": [...],
        "decision_frameworks": [...],
        "risk_tolerance": "...",
        "information_sources": [...]
    },
    
    "safety_rules": {
        "critical": [...],  # Must never violate
        "important": [...],  # Should avoid
        "best_practices": [...]
    },
    
    "skill_hierarchy": {
        "foundational": [...],
        "intermediate": [...],
        "advanced": [...],
        "mastery": [...]
    },
    
    "edge_cases": {
        "scenarios": [...],
        "exceptions": [...],
        "escalation_triggers": [...]
    },
    
    "knowledge_confidence": {
        "high_confidence_areas": [...],
        "medium_confidence_areas": [...],
        "needs_expansion": [...]  # Triggers web agent
    }
}
```

### 2. Onboarding Interpreter

**Purpose**: Extract profession schema from natural language user input.

**Input**: User's profession description, responsibilities, tools
**Output**: Structured Profession Schema

**Process**:
1. **Profession Detection**: Identify primary profession from description
2. **Entity Extraction**: Pull out tools, tasks, terminology
3. **Pattern Recognition**: Identify decision patterns, constraints
4. **Schema Mapping**: Map extracted entities to schema fields
5. **Confidence Scoring**: Mark areas needing expansion

**Implementation Strategy**:
- Use LLM with structured output prompting
- JSON schema validation
- Iterative refinement with user confirmation

### 3. Knowledge Expansion Layer

**Purpose**: Fill knowledge gaps using web search when needed.

**Components**:

**a) Gap Detector**:
- Monitors questions/tasks
- Identifies missing schema information
- Prioritizes expansion needs

**b) Query Generator**:
```python
def generate_queries(profession, gap_area, context):
    """
    Examples:
    - "software engineer best practices for code review"
    - "financial analyst risk assessment frameworks"
    - "nurse medication administration safety protocols"
    """
    return optimized_search_queries
```

**c) Web Agent**:
- Uses Google Custom Search API
- Filters for authoritative sources
- Rate limiting and caching

**d) Result Cleaner**:
- Extract relevant facts
- Remove ads/noise
- Validate accuracy
- Cite sources

**e) Schema Merger**:
- Integrate new knowledge into schema
- Update confidence scores
- Maintain version history

### 4. Reasoning Layer

**Purpose**: Generate profession-aware responses using schema + persona.

**Process**:
1. **Context Injection**: Load relevant schema sections
2. **Persona Blending**: Merge with user's cognitive profile
3. **Professional Logic**: Apply profession-specific reasoning
4. **Decision Modeling**: Use profession's decision patterns
5. **Safety Checks**: Validate against safety rules

**Example Prompt Enhancement**:
```
Original: "How should I handle this bug report?"

Enhanced: "How should I handle this bug report?

Context from your profession (Software Engineer):
- You typically prioritize bugs by: severity, user impact, business value
- Your tools for bug tracking: Jira, GitHub Issues
- Your decision framework: triage → assign → fix → test → deploy
- Safety rules: Never deploy without code review, always write tests
- Your personal style: analytical, cautious, prefers thorough documentation
```

### 5. Parallel-Self Alignment

**Purpose**: Make AI behave as a parallel version of the user in their profession.

**Alignment Process**:

**a) Style Transfer**:
- Professional communication style + User's personal writing style
- Professional decision patterns + User's risk tolerance
- Professional terminology + User's vocabulary preferences

**b) Pattern Harmonization**:
```python
professional_pattern = schema["decision_patterns"]
personal_pattern = cognitive_profile["decision_pattern"]
aligned_pattern = merge_patterns(professional_pattern, personal_pattern)
```

**c) Contextual Switching**:
- Work mode: Profession-heavy alignment
- Personal mode: User-heavy alignment
- Advisory mode: Balanced blending

**d) Consistency Checks**:
- Ensure professional safety rules are never violated
- Maintain user's ethical boundaries
- Preserve user's preferences

## Data Flow Example

**User Query**: "Should I refactor this legacy code or add a feature first?"

**Flow**:
1. **Schema Lookup**: Load software engineer schema
2. **Gap Check**: Schema has "refactoring best practices" ✓
3. **Context Build**: 
   - Professional context: "Code quality vs feature velocity tradeoff"
   - User pattern: "Prefers long-term quality over short-term wins"
   - Schema rules: "Tech debt should be addressed before major features"
4. **Reasoning**: Apply decision framework from schema
5. **Alignment**: Phrase response in user's communication style
6. **Output**: "Given your tendency to prioritize code quality and the engineering principle that technical debt compounds, I'd recommend refactoring first. Here's why..."

## Implementation Priorities

### Phase 1: Foundation (Week 1-2)
1. ✅ Design Profession Schema structure
2. ✅ Implement schema storage (JSON/SQLite)
3. ✅ Create basic onboarding interpreter
4. ✅ Build schema validator

### Phase 2: Core Intelligence (Week 3-4)
1. ✅ Implement Knowledge Expansion Layer
2. ✅ Integrate Google Custom Search API
3. ✅ Build query generator and result cleaner
4. ✅ Create schema merger logic

### Phase 3: Reasoning & Alignment (Week 5-6)
1. ✅ Build Reasoning Layer
2. ✅ Implement Parallel-Self Alignment
3. ✅ Create context injection system
4. ✅ Test with multiple professions

### Phase 4: Polish & Scale (Week 7-8)
1. ✅ Add profession library (common professions pre-loaded)
2. ✅ Optimize performance
3. ✅ Add analytics and learning
4. ✅ Build UI for schema viewing/editing

## Scalability Considerations

1. **Modular Design**: Each component is independent
2. **Schema Versioning**: Track changes to profession schemas
3. **Caching**: Cache web search results and expanded knowledge
4. **Lazy Loading**: Load schema sections only when needed
5. **Multi-Profession**: Support users with multiple professions
6. **Continuous Learning**: Schema improves with usage

## Success Metrics

1. **Accuracy**: Profession-specific responses are correct
2. **Relevance**: Responses match professional context
3. **Alignment**: Output matches user's style and patterns
4. **Coverage**: Percentage of queries handled without expansion
5. **User Satisfaction**: Feedback scores on responses
