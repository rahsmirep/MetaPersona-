# 🚀 MetaPersona - Quick Start Guide

Get your personal AI agent running in 5 minutes!

---

## ⚡ Fast Track Setup

### Step 1: Install (30 seconds)
```powershell
# Clone and enter directory
cd MetaPersona-

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure (1 minute)
```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env - Add your API key
notepad .env
```

**Choose ONE provider:**
- **OpenAI**: Set `LLM_PROVIDER=openai` and add your `OPENAI_API_KEY`
- **Anthropic**: Set `LLM_PROVIDER=anthropic` and add your `ANTHROPIC_API_KEY`
- **Local Ollama**: Set `LLM_PROVIDER=ollama` (no API key needed, but run `ollama serve`)

### Step 3: Initialize (1 minute)
```powershell
python metapersona.py init
```

Answer 5 quick questions:
1. User ID (any name you want)
2. Writing tone (casual/formal/technical)
3. Vocabulary level (simple/intermediate/advanced)
4. Decision style (analytical/intuitive/balanced)
5. Risk tolerance (conservative/moderate/aggressive)

### Step 4: Start Using! (instant)
```powershell
# Try a quick task
python metapersona.py ask "Introduce yourself in my style"

# Or start chatting
python metapersona.py chat
```

---

## 🎯 Your First Tasks

Try these to see your agent in action:

```powershell
# Writing task
python metapersona.py ask "Write a professional email about project delays"

# Decision making
python metapersona.py ask "Should I prioritize feature A or bug fixes? Explain reasoning."

# Creative task
python metapersona.py ask "Brainstorm 5 ideas for improving team productivity"
```

---

## 🎓 Training Your Agent

### Quick Training (Optional)
```powershell
# Create a text file with your writing samples
# Then:
python metapersona.py learn my_writing.txt
```

### During Chat Sessions
```
You: [Your task]
Agent: [Response]
Provide feedback? y
Rate (1-5): 4
Feedback: Good, but make it shorter next time
```

The agent learns from ratings 4+ and adjusts its style!

---

## 📊 Check Progress

```powershell
# View statistics
python metapersona.py status

# See recent interactions
python metapersona.py history
```

---

## 🔥 Pro Tips

1. **Rate Often**: Give feedback on at least 5-10 interactions for best results
2. **Be Specific**: Add detailed feedback text, not just ratings
3. **Add Examples**: Use `learn` command with your best writing
4. **Check Progress**: Run `status` regularly to see improvement
5. **Backup Data**: Your `./data` folder contains everything - back it up!

---

## 🐛 Common Issues

### "Provider not available"
- **OpenAI/Anthropic**: Check your API key in `.env`
- **Ollama**: Run `ollama serve` in another terminal first

### "No module named 'src'"
```powershell
pip install -r requirements.txt
```

### "No profile found"
```powershell
python metapersona.py init
```

---

## 🎨 Use Cases to Try

1. **Email Assistant**: "Write responses to these 3 emails: [paste emails]"
2. **Meeting Notes**: "Summarize these meeting notes in my style"
3. **Decision Helper**: "Help me decide between options A, B, C considering [criteria]"
4. **Content Creator**: "Write a blog post intro about [topic]"
5. **Code Reviewer**: "Review this code and provide feedback as I would"

---

## 📈 Next Steps

Once you're comfortable:

1. ✅ Run the example script: `python example.py`
2. ✅ Read full documentation: `README.md`
3. ✅ Advanced setup guide: `SETUP.md`
4. ✅ Run tests: `pytest tests/`
5. ✅ Use as library in your own scripts

---

## 💬 Example Session

```powershell
PS> python metapersona.py chat

💬 MetaPersona Chat Session

Agent active for: john_doe
Interactions: 0
Accuracy: 0.0%

You: Write a short team announcement about our new feature

Agent:
Hey team! 🎉

Quick update - we just shipped the new dashboard feature! 
It's live in production as of today.

Key highlights:
• Real-time analytics
• Custom widgets
• Mobile responsive

Check it out and let me know if you spot any issues. Great work everyone!

Provide feedback? y
Rate response (1-5): 5
Feedback (optional): Perfect tone, just what I needed

You: exit

Chat session ended.
```

---

## 🆘 Get Help

- Read `README.md` for complete documentation
- Check `SETUP.md` for troubleshooting
- Review `example.py` for code usage patterns
- Run tests: `pytest tests/` to verify installation

---

**You're all set! Your personal AI agent is ready to learn and act in your style. 🚀**

Start simple, give feedback, and watch it improve!
