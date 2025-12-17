# User Profiling & Adaptive System

MetaPersona v2.1 introduces an **intelligent user profiling system** that learns about you through onboarding and adapts the entire assistant to your profession, technical level, and preferences.

## 🎯 Overview

The system conducts a simple onboarding questionnaire to understand:
- **Professional Background**: Profession, industry, experience level
- **Technical Proficiency**: Coding skills, tools used, technical level
- **Daily Work Context**: Common tasks, tools, programming languages
- **Personal Preferences**: Communication style, help frequency
- **Skill Needs**: Areas where you want assistance

Based on your responses, the system automatically:
1. **Loads appropriate skill packs** for your profession
2. **Adjusts agent routing weights** to prioritize relevant agents
3. **Customizes communication style** to match your preferences
4. **Adapts system prompts** with domain-specific knowledge

## 🚀 Quick Start

### 1. Complete Onboarding
```bash
python metapersona.py onboard
```

Answer the interactive questions about your background, work, and preferences.

### 2. View Your Profile
```bash
python metapersona.py profile --user-id YOUR_NAME
```

### 3. Chat with Adaptive Agents
```bash
python metapersona.py adaptive-chat --user-id YOUR_NAME
```

## 📋 Onboarding Questions

### Professional Information
- **Profession**: Your job title or primary role
- **Industry**: Technology, Healthcare, Finance, Education, Retail, etc.
- **Experience Level**: Entry, Mid-Level, Senior, Executive
- **Technical Proficiency**: Beginner, Intermediate, Advanced, Expert

### Work Context
- **Daily Tasks**: Your top 3-5 regular tasks
- **Tools Used**: Software/tools you use regularly
- **Programming Languages**: Languages you code in (if applicable)

### Personal
- **Hobbies/Interests**: Your interests outside work
- **Communication Style**: Casual, Professional, or Technical
- **Help Frequency**: How often you'll use the assistant

### Skills Needed
Select from:
- Research & Information Gathering
- Writing & Documentation
- Coding & Development
- Data Analysis
- Project Management
- Creative Content
- Problem Solving
- Learning New Topics
- Task Automation
- Communication

## 🎨 Skill Packs

The system includes pre-built skill packs for different professions:

### 1. Software Developer Pack
**For**: Developers, Programmers, Engineers  
**Includes**: Code generation, debugging, API docs, git ops, testing  
**Agent Weights**: Coder (1.2x), Researcher (1.1x)  
**Style**: Technical accuracy, best practices focus

### 2. Healthcare Professional Pack
**For**: Doctors, Nurses, Medical Staff  
**Includes**: Medical research, documentation, data analysis, terminology  
**Agent Weights**: Researcher (1.3x), Writer (1.1x)  
**Style**: Precise medical terminology, evidence-based

### 3. Business Professional Pack
**For**: Managers, Analysts, Consultants  
**Includes**: Data analysis, reporting, presentations, email drafting  
**Agent Weights**: Writer (1.2x), Researcher (1.1x)  
**Style**: Business outcomes, ROI focus

### 4. Creative Professional Pack
**For**: Writers, Designers, Content Creators  
**Includes**: Content creation, brainstorming, editing, research  
**Agent Weights**: Writer (1.3x)  
**Style**: Creativity encouraged, engaging content

### 5. Educator Pack
**For**: Teachers, Professors, Instructors  
**Includes**: Research, content creation, explanation, assessment  
**Agent Weights**: Researcher (1.2x), Writer (1.2x)  
**Style**: Clear explanations, pedagogical focus

### 6. Retail & Sales Pack
**For**: Retail Workers, Sales Staff, Customer Service  
**Includes**: Communication, problem-solving, documentation  
**Agent Weights**: Generalist (1.2x), Writer (1.1x)  
**Style**: Customer satisfaction focus

### 7. Research Professional Pack
**For**: Researchers, Scientists, Analysts  
**Includes**: Research, data analysis, documentation, citations  
**Agent Weights**: Researcher (1.3x), Writer (1.1x)  
**Style**: Accuracy, evidence, proper citations

### 8. General Purpose Pack
**For**: All users (always loaded)  
**Includes**: Web search, calculator, file operations  
**Agent Weights**: Balanced (1.0x)

## 🔄 Adaptive Routing

The system adjusts agent routing based on your profile:

### Example: Software Developer
```python
# Base routing confidence
researcher: 0.70
coder: 0.90
writer: 0.60
generalist: 0.50

# After applying Developer Pack weights (1.2x for coder, 1.1x for researcher)
researcher: 0.77  # 0.70 * 1.1
coder: 1.00  # 0.90 * 1.2 (capped at 1.0)
writer: 0.60  # no adjustment
generalist: 0.50  # no adjustment

# Result: Coding tasks route to coder with even higher priority
```

### Example: Healthcare Professional
```python
# Research task: "Find latest studies on diabetes treatment"

# Base confidence
researcher: 0.90
coder: 0.30
writer: 0.70
generalist: 0.50

# After applying Healthcare Pack weights (1.3x for researcher)
researcher: 1.00  # 0.90 * 1.3 (capped)
coder: 0.30  # no adjustment
writer: 0.77  # 0.70 * 1.1
generalist: 0.50  # no adjustment

# Result: Research routes to researcher with maximum confidence
# System uses medical terminology and evidence-based focus
```

## 💬 Adaptive Communication Styles

### Casual & Friendly
- Uses conversational tone
- Avoids unnecessary jargon
- Friendly and approachable
- Best for: General users, creative professionals

### Professional & Formal
- Clear, professional language
- Balanced technical detail
- Business-appropriate
- Best for: Business professionals, educators

### Technical & Precise
- Uses technical terminology
- Detailed technical explanations
- Assumes domain knowledge
- Best for: Developers, researchers, advanced users

## 🛠️ Usage Examples

### Complete Onboarding
```bash
$ python metapersona.py onboard

🎭 Welcome to MetaPersona!
Let's personalize your experience with a few questions...

What is your profession or primary role?
  > Software Developer

Which industry do you work in?
Options:
  1. Technology/Software
  2. Healthcare/Medical
  3. Finance/Banking
  ...
  Select: 1

What is your experience level?
Options:
  1. Entry Level
  2. Mid-Level
  3. Senior
  4. Executive/Leadership
  Select: 3

...

✓ Onboarding Complete
Loaded skill packs: general, developer
Agent routing weights: coder (1.2x), researcher (1.1x)
```

### View Profile
```bash
$ python metapersona.py profile --user-id john_doe

╭──────────────────────────────────────────╮
│ User Profile: john_doe                   │
│                                          │
│ Professional Background:                 │
│   Profession: software developer         │
│   Industry: Technology/Software          │
│   Level: senior                          │
│   Technical Level: advanced              │
│                                          │
│ Loaded Skill Packs:                      │
│   • general                              │
│   • developer                            │
│                                          │
│ Agent Routing Weights:                   │
│   • coder: 1.27x                         │
│   • researcher: 1.21x                    │
│   • writer: 1.00x                        │
│   • generalist: 1.00x                    │
╰──────────────────────────────────────────╯
```

### Adaptive Chat
```bash
$ python metapersona.py adaptive-chat --user-id john_doe

🎭 Adaptive Multi-Agent Chat
Personalized for: john_doe (software developer)

Initializing adaptive agents...
  ✓ Research Agent (adapted for your needs)
  ✓ Code Agent (adapted for your technical level)
  ✓ Writer Agent (adapted for your communication style)
  ✓ Generalist Agent (your default helper)

System Ready!
Skill Packs: general, developer
Routing optimized for: software developer

Commands: 'exit', 'agents', 'stats', 'profile'

[john_doe] > Write a Python function to parse JSON

→ Routing to coder (confidence: 1.00)

Coder:
╭────────────────────────────────────────────────────╮
│ Here's a robust JSON parsing function:            │
│                                                    │
│ ```python                                          │
│ import json                                        │
│ from typing import Dict, Any, Optional            │
│                                                    │
│ def parse_json(                                    │
│     json_string: str,                              │
│     default: Optional[Dict[str, Any]] = None       │
│ ) -> Dict[str, Any]:                               │
│     """                                            │
│     Parse JSON string with error handling.         │
│     ...                                            │
│ ```                                                │
╰────────────────────────────────────────────────────╯
```

## 🔧 Programmatic Usage

### Load and Use Profile in Code
```python
from src.user_profiling import UserProfilingSystem

# Initialize system
profiling = UserProfilingSystem("./data")

# Load profile
profile = profiling.load_profile("john_doe")

# Get adaptive system prompt
adaptive_prompt = profiling.get_adaptive_system_prompt(profile)

# Use in agent initialization
agent = MyAgent(
    system_prompt=adaptive_prompt,
    routing_weights=profile.agent_routing_preferences
)
```

### Update Profile
```python
# Update specific fields
profiling.update_profile("john_doe", {
    "programming_languages": ["Python", "JavaScript", "Rust"],
    "technical_level": "expert"
})

# Profile automatically recalculates:
# - Loaded skill packs
# - Agent routing weights
# - Adaptive prompts
```

### Custom Skill Pack
```python
from src.user_profiling import SkillPack

custom_pack = SkillPack(
    pack_id="data_scientist",
    name="Data Science Pack",
    description="ML, statistics, data analysis",
    target_professions=["data scientist", "ml engineer"],
    target_industries=["Technology/Software"],
    skills=["data_analysis", "ml_models", "visualization"],
    agent_weights={"researcher": 1.3, "coder": 1.2},
    custom_prompt_additions="Focus on statistical rigor and reproducibility."
)

# Add to system
profiling_system.skill_packs.append(custom_pack)
```

## 📊 Benefits

### For Different User Types

**Beginner Users**:
- Simplified language and explanations
- Higher generalist agent weight
- Step-by-step guidance
- Avoids complex jargon

**Advanced Users**:
- Technical precision
- Specialized agent prioritization
- Domain-specific terminology
- Efficient, detailed responses

**Professionals**:
- Industry-specific knowledge
- Relevant skill packs loaded
- Professional communication
- Task-optimized routing

## 🎯 Best Practices

1. **Complete Onboarding First**: Run `onboard` before using adaptive features
2. **Keep Profile Updated**: Update as your role or needs change
3. **Use Adaptive Chat**: Leverage `adaptive-chat` for personalized experience
4. **Review Routing Stats**: Use `stats` command to see agent usage patterns
5. **Try Different Styles**: Experiment with communication preferences

## 🔄 Profile Management

### Update Your Profile
```bash
# Re-run onboarding
python metapersona.py onboard --user-id YOUR_NAME

# Choose "yes" when asked to redo onboarding
```

### Multiple Profiles
```bash
# Create profiles for different contexts
python metapersona.py onboard --user-id work_persona
python metapersona.py onboard --user-id personal_persona

# Use different profiles
python metapersona.py adaptive-chat --user-id work_persona
python metapersona.py adaptive-chat --user-id personal_persona
```

## 🚀 Future Enhancements

Planned features:
- **Learning from interactions**: Auto-adjust weights based on usage
- **Custom skill pack creation**: UI for building your own packs
- **Team profiles**: Share profiles across team members
- **Context switching**: Quickly switch between work/personal modes
- **Skill recommendations**: Suggest new skills based on tasks
- **Profile analytics**: Insights into your usage patterns

## 📚 Related Documentation

- [MULTI_AGENT.md](./MULTI_AGENT.md) - Multi-agent system overview
- [INTELLIGENT_ROUTING.md](./INTELLIGENT_ROUTING.md) - LLM-based routing
- [README.md](./README.md) - Project overview

---

**MetaPersona v2.1** - Adaptive AI Assistant That Learns About You
