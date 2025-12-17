# MetaPersona 🤖

**A lightweight AI system that learns how you think, stores your preferences, and generates an autonomous agent that acts in your style.**

MetaPersona creates a personal AI agent that:
- 📝 Captures your writing tone, decision patterns, and preferences
- 🔐 Uses local identity (keypair + encrypted profile) bound to you
- 🎯 Takes tasks and responds exactly as you would
- 🧠 Learns from each interaction through a feedback loop
- 💬 Provides a simple CLI interface for seamless interaction

---

## 🌟 Features

### 🔐 Identity Layer
- RSA keypair generation for cryptographic identity
- AES-256 encrypted profile storage
- Secure local data management

### 🧠 Cognitive Profile
- **Writing Style**: Tone, vocabulary, sentence structure, common phrases
- **Decision Patterns**: Analytical approach, risk tolerance, priority weights
- **Preferences**: Communication, work style, and custom preferences
- **Learning Metrics**: Tracks interactions, feedback, and accuracy

### 🤖 Persona Agent
- Processes tasks in your unique style
- Makes decisions based on your patterns
- Maintains conversation context
- Updates understanding over time

### 🔄 Memory Loop
- Records all interactions with timestamps
- Collects feedback for continuous improvement
- Analyzes learning progress over time
- Exports training data for fine-tuning

### 🛠️ Modular Skills System
- **Plugin Architecture**: Extensible skill framework
- **Built-in Skills**: Calculator, file operations, web search
- **Skill Chaining**: Execute multi-step workflows
- **Dynamic Loading**: Auto-discover and register custom skills
- **LLM Integration**: Agent can invoke skills automatically

### 🤝 Multi-Agent System (NEW in v2.0!)
- **Specialized Agents**: ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent
- **Intelligent Routing**: Automatic task routing to best agent
- **Agent Registry**: Centralized agent management
- **Task Router**: Confidence-based agent selection
- **Agent Collaboration**: Multiple agents working together
- **Custom Agents**: Easy-to-extend BaseAgent class

### 💻 CLI Interface
- Interactive chat sessions
- Single-task execution
- Multi-agent routing and collaboration
- Skills management
- Status monitoring and history viewing
- Learning from example texts
- Skills management and execution

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- OpenAI/Anthropic API key OR local Ollama installation

### Installation

1. **Clone the repository**
```powershell
git clone <your-repo-url>
cd MetaPersona-
```

2. **Install dependencies**
```powershell
pip install -r requirements.txt
```

3. **Configure environment**
```powershell
cp .env.example .env
# Edit .env with your LLM provider settings
```

4. **Initialize your persona**
```powershell
python metapersona.py init
```

Follow the interactive prompts to set up your cognitive profile.

---

## 📖 Usage

### Interactive Chat
Start a conversation with your agent:
```powershell
python metapersona.py chat
```

Commands during chat:
- `exit` - End session
- `clear` - Clear conversation history
- `status` - Show agent statistics

### Single Task
Execute a one-off task:
```powershell
python metapersona.py ask "Write an email to my team about the project update"
```

### Check Status
View agent metrics and learning progress:
```powershell
python metapersona.py status
```

### View History
See recent interactions:
```powershell
python metapersona.py history --count 20
```

### Learn from Examples
Add your writing examples to improve the agent:
```powershell
python metapersona.py learn path/to/your/writing.txt
```

### Skills Commands
List available skills:
```powershell
python metapersona.py skills
```

Get detailed information about a skill:
```powershell
python metapersona.py skill-info calculator
```

Execute a skill directly:
```powershell
# Calculator
python metapersona.py use-skill calculator -p "expression=sqrt(144) + 10"

# File operations
python metapersona.py use-skill file_ops -p "operation=read" -p "path=./data/test.txt"

# Web search
python metapersona.py use-skill web_search -p "query=Python programming" -p "max_results=3"
```

### Multi-Agent Commands (NEW!)
List all registered agents:
```powershell
python metapersona.py agents-list
```

View agent status:
```powershell
# All agents
python metapersona.py agents-status

# Specific agent
python metapersona.py agents-status --agent-id researcher
```

Route a task to the best agent:
```powershell
# Execute task
python metapersona.py route-task "Research quantum computing"

# Explain routing without executing
python metapersona.py route-task "Write Python code" --explain
```

Interactive multi-agent chat:
```powershell
python metapersona.py multi-agent-chat
```

---

## 🏗️ Architecture

```
MetaPersona-/
├── src/
│   ├── __init__.py              # Package initialization
│   ├── identity.py              # Cryptographic identity & encryption
│   ├── cognitive_profile.py     # Profile management
│   ├── persona_agent.py         # Main agent logic
│   ├── memory_loop.py           # Learning & feedback system
│   ├── llm_provider.py          # LLM integration (OpenAI/Anthropic/Ollama)
│   ├── config.py                # Configuration management
│   ├── skills_system.py         # Modular skills system
│   ├── agent_base.py            # Base agent class (NEW!)
│   ├── agent_registry.py        # Agent management (NEW!)
│   ├── task_router.py           # Task routing (NEW!)
│   └── specialized_agents.py    # Built-in agents (NEW!)
├── data/                        # Local data storage (created automatically)
│   ├── private_key.pem          # Your private key
│   ├── public_key.pem           # Your public key
│   ├── identity.json            # Identity metadata
│   ├── cognitive_profile.json   # Your cognitive profile
│   ├── memory.jsonl             # Interaction history
│   └── agents/                  # Agent memories (NEW!)
├── examples/                    # Example scripts
│   ├── example.py               # Basic usage demo
│   ├── skills_demo.py           # Skills system demo
│   └── multi_agent_demo.py      # Multi-agent demo (NEW!)
├── metapersona.py               # CLI interface
├── requirements.txt             # Python dependencies
├── README.md                    # Main documentation
├── SKILLS.md                    # Skills documentation
├── MULTI_AGENT.md               # Multi-agent documentation (NEW!)
└── .env                         # Configuration (create from .env.example)
```

---

## 🔧 Configuration

### LLM Provider Setup

**Option 1: OpenAI**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

**Option 2: Anthropic Claude**
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Option 3: Local Ollama**
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
```

### Security Options
```env
ENCRYPTION_ENABLED=true
DATA_DIR=./data
```

---

## 🎓 How It Learns

1. **Initial Setup**: You define basic preferences during initialization
2. **Task Execution**: Agent responds to tasks using your cognitive profile
3. **Feedback Loop**: You rate responses (1-5 stars)
4. **Profile Update**: System learns from high-rated interactions
5. **Continuous Improvement**: Agent becomes more accurate over time

### Learning Metrics
- **Interaction Count**: Total tasks processed
- **Feedback Received**: Number of rated interactions
- **Accuracy Score**: Running average of feedback scores
- **Trend Analysis**: Improvement over time

---

## 🔒 Security & Privacy

- **Local-First**: All data stored locally on your machine
- **Encrypted Storage**: Profile encrypted with AES-256
- **Keypair Authentication**: RSA-2048 identity binding
- **No Cloud Storage**: Your cognitive profile never leaves your device
- **API Key Safety**: LLM API keys stored in local .env file

---

## 🛠️ Advanced Usage

### Creating Custom Skills

Create your own skills by extending the `Skill` base class:

```python
from src.skills.base import Skill, SkillMetadata, SkillParameter, SkillResult

class MyCustomSkill(Skill):
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="my_skill",
            description="Does something amazing",
            category="Custom",
            parameters=[
                SkillParameter(
                    name="input",
                    type="str",
                    description="Input parameter",
                    required=True
                )
            ]
        )
    
    def execute(self, input: str) -> SkillResult:
        try:
            # Your skill logic here
            result = f"Processed: {input}"
            return SkillResult(success=True, data=result)
        except Exception as e:
            return SkillResult(success=False, error=str(e))

# Register your skill
from src.skills import get_registry
get_registry().register(MyCustomSkill())
```

### Skill Chaining

Chain multiple skills together for complex workflows:

```python
from src.skills import SkillManager

skill_manager = SkillManager()

chain = [
    {"skill": "web_search", "parameters": {"query": "Python"}, "output_var": "search_results"},
    {"skill": "file_ops", "parameters": {"operation": "write", "path": "results.txt", "content": "$search_results"}},
]

results = skill_manager.chain_skills(chain)
```

### Export Training Data
Export high-quality interactions for fine-tuning:
```powershell
python -c "from src.memory_loop import MemoryLoop; m = MemoryLoop(); m.export_training_data()"
```

### Customize Profile Programmatically
```python
from src import ProfileManager, CognitiveProfile

pm = ProfileManager()
profile = pm.load_profile()

# Update preferences
profile.preferences.communication["response_length"] = "concise"
profile.preferences.work_style["detail_level"] = "high"

pm.save_profile(profile)
```

### Use as Library
```python
from src import AgentManager

# Initialize
am = AgentManager(data_dir="./data")
agent = am.initialize_agent()

# Process task
response = agent.process_task("Analyze this data and provide insights")
print(response)

# Save state
am.save_agent_state(agent)
```

---

## 📊 Example Workflow

```powershell
# 1. Initialize
python metapersona.py init

# 2. Start learning
python metapersona.py chat
> "Write a summary of our Q4 goals"
> [Agent responds]
> Provide feedback? Yes
> Rate: 4
> Feedback: Good but could be more concise

# 3. Check progress
python metapersona.py status

# 4. Add your writing examples
python metapersona.py learn my_email.txt

# 5. Use for tasks
python metapersona.py ask "Draft response to client inquiry"

# 6. Try multi-agent routing (NEW!)
python metapersona.py multi-agent-chat
```

---

## 📚 Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[SKILLS.md](SKILLS.md)** - Modular skills system guide
- **[MULTI_AGENT.md](MULTI_AGENT.md)** - Multi-agent system guide (NEW!)
- **[QUICKSTART.md](QUICKSTART.md)** - Quick 5-minute setup
- **[SETUP.md](SETUP.md)** - Detailed setup and troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture diagrams

---

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - Feel free to use and modify for your own purposes.

---

## 🐛 Troubleshooting

**"Provider not available"**
- Check your .env file configuration
- Verify API keys are correct
- For Ollama, ensure service is running: `ollama serve`

**"No profile found"**
- Run `python metapersona.py init` first

**"Import errors"**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (3.8+ required)

---

## 🗺️ Roadmap

- [ ] Web dashboard interface
- [ ] Multi-user support
- [ ] Voice interaction
- [ ] Fine-tuning automation
- [ ] Integration with calendar/email
- [ ] Mobile app
- [ ] Profile sharing (encrypted)

---

## 💡 Use Cases

- **Personal Assistant**: Handle routine communications
- **Decision Support**: Get recommendations in your style
- **Writing Aid**: Generate content matching your voice
- **Learning Tool**: Understand your own patterns
- **Productivity**: Delegate cognitive tasks
- **Research**: Query and analyze in your analytical style

---

Built with ❤️ for personal AI autonomy
