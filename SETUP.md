# MetaPersona - Setup and Testing Guide

## First Time Setup

### 1. Create Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Configure Environment
```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit .env with your preferred text editor
notepad .env
```

**Required Configuration:**
- Set `LLM_PROVIDER` to your choice (openai, anthropic, or ollama)
- Add your API key for cloud providers
- For local Ollama: ensure Ollama is running with `ollama serve`

### 4. Initialize Your Persona
```powershell
python metapersona.py init
```

You'll be prompted to:
- Enter a user ID
- Select writing tone (formal, casual, technical, etc.)
- Choose vocabulary level
- Define decision-making style
- Set risk tolerance

---

## Testing Commands

### Test 1: Check Installation
```powershell
python -c "from src import IdentityLayer; print('✓ Import successful')"
```

### Test 2: Initialize Identity
```powershell
python -c "from src.identity import IdentityLayer; id = IdentityLayer('./test_data'); id.generate_keypair(); print('✓ Identity created')"
```

### Test 3: Create Profile
```powershell
python -c "from src import ProfileManager; pm = ProfileManager('./test_data'); p = pm.create_profile('test_user'); print('✓ Profile created')"
```

### Test 4: Quick Task
```powershell
python metapersona.py ask "Say hello and introduce yourself"
```

---

## Interactive Testing

### Start a Chat Session
```powershell
python metapersona.py chat
```

**Try these prompts:**
1. "Write a professional email requesting a meeting"
2. "Explain a complex topic in simple terms"
3. "Make a decision between three options"

### Check Learning Progress
```powershell
# After several interactions with feedback
python metapersona.py status
```

### View Interaction History
```powershell
python metapersona.py history --count 5
```

---

## Using with Different LLM Providers

### OpenAI (GPT-4)
```powershell
# In .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4o-mini
```

### Anthropic (Claude)
```powershell
# In .env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Local Ollama
```powershell
# Start Ollama
ollama serve

# In another terminal
ollama pull llama3

# In .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3
```

---

## Training Your Agent

### Method 1: Add Writing Examples
Create a file with your writing samples:
```powershell
# Create sample.txt with your writing
python metapersona.py learn sample.txt
```

### Method 2: Interactive Feedback
During chat sessions, provide ratings:
```
You: Write a summary of machine learning
Agent: [Response]
Provide feedback? Yes
Rate response (1-5): 4
Feedback (optional): Good but too technical
```

### Method 3: Programmatic Training
```python
from src import ProfileManager

pm = ProfileManager()
profile = pm.load_profile()

# Update writing style
profile.writing_style.tone = "friendly"
profile.writing_style.common_phrases.append("That said,")

# Update decision patterns
profile.decision_pattern.approach = "analytical"
profile.decision_pattern.priority_weights = {
    "speed": 0.3,
    "quality": 0.5,
    "cost": 0.2
}

pm.save_profile(profile)
```

---

## Troubleshooting

### Issue: "Module not found"
```powershell
pip install -r requirements.txt --upgrade
```

### Issue: "Provider not available"
Check your provider setup:
```powershell
# For OpenAI
python -c "from src.llm_provider import OpenAIProvider; p = OpenAIProvider(); print(p.is_available())"

# For Ollama
curl http://localhost:11434/api/tags
```

### Issue: "Permission denied" for data folder
```powershell
# Create data directory manually
New-Item -ItemType Directory -Force -Path .\data
```

### Issue: Import errors in VS Code
Make sure you're using the correct Python interpreter:
1. Press `Ctrl+Shift+P`
2. Type "Python: Select Interpreter"
3. Choose the venv interpreter

---

## Example Workflow

### Complete First-Time Setup
```powershell
# 1. Setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings

# 2. Initialize
python metapersona.py init

# 3. Test with a simple task
python metapersona.py ask "Introduce yourself"

# 4. Start chat session
python metapersona.py chat

# 5. Check your progress
python metapersona.py status
```

---

## Advanced Testing

### Test Encryption
```python
from src.identity import IdentityLayer

id_layer = IdentityLayer("./data")
data = "Secret cognitive profile"
passphrase = "my-secure-password"

encrypted = id_layer.encrypt_data(data, passphrase)
decrypted = id_layer.decrypt_data(encrypted, passphrase)

assert data == decrypted
print("✓ Encryption test passed")
```

### Test Memory Loop
```python
from src.memory_loop import MemoryLoop

memory = MemoryLoop("./data")

# Record interaction
interaction = memory.record_interaction(
    task="Test task",
    response="Test response",
    tags=["test"]
)

# Add feedback
interactions = memory.load_all_interactions()
memory.add_feedback(len(interactions) - 1, 5.0, "Excellent")

# Check summary
summary = memory.get_feedback_summary()
print(summary)
```

### Test Agent Decision Making
```python
from src import AgentManager

am = AgentManager()
agent = am.initialize_agent()

decision = agent.make_decision(
    "Which programming language to use for this project?",
    ["Python", "JavaScript", "Rust"]
)

print(decision['response'])
```

---

## Performance Benchmarks

Typical response times (on modern hardware):
- OpenAI GPT-4: 2-5 seconds
- Anthropic Claude: 2-4 seconds  
- Local Ollama: 5-15 seconds (depends on model size)

Memory usage:
- Base system: ~50MB
- With Ollama model loaded: ~4-8GB (model dependent)

---

## Data Backup

Your persona data is stored in `./data/`. Back it up regularly:

```powershell
# Create backup
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path .\data -DestinationPath ".\backups\persona_backup_$timestamp.zip"

# Restore backup
Expand-Archive -Path .\backups\persona_backup_20241217.zip -DestinationPath .\data -Force
```

---

## VS Code Tasks

Use built-in VS Code tasks (Terminal → Run Task):
- `Install Dependencies`
- `Initialize MetaPersona`
- `Start Chat Session`
- `Show Agent Status`
