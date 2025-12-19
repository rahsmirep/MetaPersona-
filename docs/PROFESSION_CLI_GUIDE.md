# Universal Profession Understanding System - CLI Guide

## Quick Start

### 1. Set Up Google Custom Search API

```bash
# Get API credentials (see setup section below)
# Add to your .env file:
GOOGLE_API_KEY=your_api_key_here
GOOGLE_CSE_ID=your_search_engine_id_here
```

### 2. Onboard Your Profession

```bash
python metapersona.py onboard-profession
```

You'll be prompted to describe your profession. Be detailed! Include:
- Job title and industry
- Main responsibilities
- Daily tasks
- Tools and technologies you use
- Work environment
- Any regulations or constraints
- Critical safety rules

### 3. Use Profession-Aware Queries

After onboarding, all your queries will automatically include profession context:

```bash
python metapersona.py task "Should I refactor this module now or wait?"
```

MetaPersona will understand your professional context and provide advice aligned with your role, tools, and constraints.

---

## CLI Commands

### `onboard-profession`
Interactive profession onboarding process.

```bash
python metapersona.py onboard-profession [OPTIONS]

Options:
  --provider TEXT     LLM provider (default: from config)
  --interactive       Enable follow-up clarification questions
  --file PATH         Load profession description from file
  --skip-expansion    Skip initial knowledge expansion (faster)
```

**Example:**
```bash
# Interactive onboarding
python metapersona.py onboard-profession --interactive

# From file
python metapersona.py onboard-profession --file my_profession.txt
```

### `show-profession`
Display your current profession schema.

```bash
python metapersona.py show-profession [OPTIONS]

Options:
  --format TEXT    Output format: json, yaml, summary (default: summary)
  --section TEXT   Show specific section: tools, safety, terminology
```

**Example:**
```bash
# Human-readable summary
python metapersona.py show-profession

# Full JSON
python metapersona.py show-profession --format json

# Just safety rules
python metapersona.py show-profession --section safety
```

### `update-profession`
Update specific parts of your profession schema.

```bash
python metapersona.py update-profession SECTION [OPTIONS]

Options:
  --add TEXT        Add new item
  --remove TEXT     Remove item
  --interactive     Guided update process
```

**Example:**
```bash
# Add a new tool
python metapersona.py update-profession tools --add "Terraform"

# Update safety rules interactively
python metapersona.py update-profession safety --interactive
```

### `expand-knowledge`
Manually trigger knowledge expansion for specific areas.

```bash
python metapersona.py expand-knowledge AREA [OPTIONS]

Options:
  --query TEXT      Specific query to expand for
  --force           Re-fetch even if cached
```

**Example:**
```bash
# Expand knowledge about decision frameworks
python metapersona.py expand-knowledge decision_frameworks

# Expand for specific query
python metapersona.py expand-knowledge tools --query "What are the best CI/CD tools for Python?"
```

### `list-professions`
List all onboarded professions (for multi-role users).

```bash
python metapersona.py list-professions

# Switch active profession
python metapersona.py use-profession PROFESSION_ID
```

### `validate-response`
Check a response against profession safety rules.

```bash
python metapersona.py validate-response --text "Response text here"
```

---

## Profession Description Format

When describing your profession, cover these areas:

### 1. Role Definition
```
I'm a [job title] at [type of organization].

Primary responsibilities:
- [Main duty 1]
- [Main duty 2]
- [Main duty 3]

Secondary responsibilities:
- [Supporting duty 1]
- [Supporting duty 2]
```

### 2. Daily Tasks
```
Daily routine:
- [Regular task 1]
- [Regular task 2]

Weekly/monthly:
- [Periodic task 1]
- [Periodic task 2]

Situational:
- [Ad-hoc task 1] (when X happens)
```

### 3. Tools & Equipment
```
Software: [tool1], [tool2], [tool3]
Hardware: [equipment1], [equipment2]
Platforms: [platform1], [platform2]
Methodologies: [method1], [method2]
```

### 4. Work Environment
```
Setting: [office/remote/hybrid/field/etc.]
Team structure: [solo/small team/large org/etc.]
Pace: [routine/fast/crisis-driven]
Autonomy: [supervised/moderate/independent]
```

### 5. Constraints
```
Regulatory: [regulation1], [regulation2]
Time-sensitive: [deadline type1], [deadline type2]
Ethical: [ethical consideration1]
Legal: [legal requirement1]
```

### 6. Terminology
```
Jargon we use: [term1] = [definition], [term2] = [definition]
Acronyms: [ACRONYM1] = [meaning], [ACRONYM2] = [meaning]
Key concepts: [concept1], [concept2]
```

### 7. Decision Making
```
Framework: [how you make decisions]
Risk tolerance: [conservative/moderate/aggressive]
Information sources: [where you get info]
```

### 8. Safety Rules
```
CRITICAL (never do):
- [critical rule 1]
- [critical rule 2]

Important (avoid):
- [important rule 1]
- [important rule 2]

Best practices:
- [practice 1]
- [practice 2]
```

### 9. Skills
```
Foundational: [skill1], [skill2]
Intermediate: [skill3], [skill4]
Advanced: [skill5], [skill6]
Mastery: [skill7]
Soft skills: [skill8], [skill9]
```

### 10. Edge Cases
```
Unusual scenarios I handle:
- [scenario 1] → [how to handle]
- [scenario 2] → [how to handle]

Escalation triggers:
- [When X happens, escalate to Y]
```

---

## Google Custom Search API Setup

### Step 1: Get Google API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable "Custom Search API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### Step 2: Create Custom Search Engine

1. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Click "Add" to create new search engine
3. In "Sites to search", enter: `*` (search entire web)
4. Name your search engine
5. Click "Create"
6. Go to "Setup" → Copy your "Search engine ID"

### Step 3: Configure MetaPersona

Add to your `.env` file:
```bash
GOOGLE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
GOOGLE_CSE_ID=xxxxxxxxxxxxxxx:yyyyyyyyyyy
```

**Note:** Free tier includes 100 queries/day. For more, enable billing.

---

## Usage Examples

### Software Engineer

```bash
$ python metapersona.py onboard-profession

Describe your profession in detail:
> I'm a senior software engineer at a fintech startup. I design and build 
> backend microservices using Python and Go. Daily tasks include writing code,
> reviewing PRs, sprint planning, and on-call rotations. I use Docker, 
> Kubernetes, AWS, PostgreSQL, and Kafka. We follow Agile methodology with
> TDD practices. Critical rules: never deploy without tests, always get code
> review, never commit credentials.

Processing... ⠋

✓ Profession schema created!
✓ Knowledge expanded for: decision frameworks, best practices
✓ Saved to data/professions/user123_software_engineer.json

Summary:
  Role: Senior Software Engineer (Fintech)
  Tools: 10 software tools, 2 platforms
  Safety Rules: 3 critical, 2 important
  Confidence: 85% (high confidence)

$ python metapersona.py task "Should I refactor the payment processor now?"

Analyzing with profession context... ⠋

Based on your role as a software engineer in fintech:

**Decision Factors:**
- Urgency: Moderate (not blocking)
- Risk: High (payment processing is critical)
- Compliance: PCI-DSS considerations

**Recommendation:**
Wait until after the release. Here's why:

1. **Risk Management**: Payment processing is critical infrastructure. Your
   risk tolerance and fintech constraints suggest deferring major changes
   near releases.

2. **Best Practice Alignment**: Follows your TDD methodology - plan the
   refactor, write tests first, then implement in next sprint.

3. **Compliance**: Ensures time for proper testing and security review
   required for PCI-DSS compliance.

**Action Items:**
- [ ] Document refactor plan in Jira
- [ ] Schedule for next sprint
- [ ] Write test suite first
- [ ] Plan code review with at least 2 reviewers

Sources: [3 expanded knowledge areas]
```

### ICU Nurse

```bash
$ python metapersona.py onboard-profession --file nurse_profile.txt

✓ Profession onboarded: Registered Nurse (ICU)
✓ Safety rules: 6 critical, 4 important (regulatory compliance: HIPAA)

$ python metapersona.py task "Patient vitals declining, should I call doctor or continue monitoring?"

⚠️ CRITICAL DECISION DETECTED

Based on ICU nursing protocols:

**IMMEDIATE ACTION REQUIRED:**
Call the doctor NOW. Do not continue monitoring alone.

**Why:**
- Your safety rules: "Immediately report patient deterioration"
- Escalation trigger: Declining vitals = immediate physician notification
- Risk tolerance: Conservative (appropriate for patient safety)

**Protocol:**
1. Call physician immediately (per escalation protocol)
2. Prepare crash cart if significant decline
3. Continue monitoring and document changes
4. Notify charge nurse

**Documentation:**
- Log: Time vitals noted, physician notified, actions taken
- Follow HIPAA-compliant charting in Epic EMR

This aligns with Joint Commission standards and your facility's protocols.
```

### Financial Analyst

```bash
$ python metapersona.py onboard-profession

Describe your profession:
> I'm a senior financial analyst doing equity research at an investment bank.
> I build financial models, analyze companies, write research reports with
> recommendations. Tools: Excel, Bloomberg Terminal, Python. Constraints:
> SEC regulations, Chinese Wall policies, compliance review required.

✓ Onboarded: Senior Financial Analyst (Equity Research)

$ python metapersona.py task "I heard from a friend at the company about upcoming merger. Should I update my model?"

⚠️ COMPLIANCE VIOLATION DETECTED

**DO NOT PROCEED**

Your profession constraints include:
- SEC insider trading regulations
- Chinese Wall policies

**Why this is a problem:**
Information from a company insider about non-public material events (merger)
constitutes insider information. Using this to update your model or trade
would violate SEC Rule 10b-5.

**Required action:**
1. Do NOT update your model
2. Do NOT share this information
3. Report to Compliance immediately
4. Document the disclosure

**Regulatory:**
- Violation risk: High (potential SEC enforcement)
- Your training: SEC regulations on insider trading

This response was validated against your profession's safety rules.
```

---

## Advanced Features

### Interactive Refinement

When using `--interactive`, MetaPersona asks clarifying questions:

```bash
$ python metapersona.py onboard-profession --interactive

You mentioned "safety rules". Can you provide specific examples of critical rules
in your work? This helps me provide better guidance.

You mentioned using "Docker and Kubernetes". Are there specific workflows or
commands you use daily? This helps me give more relevant suggestions.
```

### Multi-Profession Support

For users with multiple roles:

```bash
# Onboard second profession
$ python metapersona.py onboard-profession --id secondary

# Switch active profession
$ python metapersona.py use-profession secondary

# View all
$ python metapersona.py list-professions
  ✓ primary: Software Engineer (active)
  ○ secondary: Tech Writer
```

### Knowledge Confidence Tracking

```bash
$ python metapersona.py show-profession --section confidence

Knowledge Confidence:
  High confidence areas:
    - Software tools and technologies
    - Development methodologies
    - Daily workflows

  Medium confidence areas:
    - Decision frameworks
    - Edge cases

  Needs expansion:
    - Industry-specific regulations
    - Advanced architecture patterns

Use 'expand-knowledge' command to improve these areas.
```

### Aligned Persona

See how your profession blends with your personal style:

```bash
$ python metapersona.py show-aligned-persona

Aligned Persona (Parallel-Self):

Communication Style:
  Personal: Casual, friendly tone
  Professional: Technical terminology, precise language
  Blended: Friendly but precise, uses jargon naturally

Decision Making:
  Personal: Intuitive, considers multiple perspectives
  Professional: Data-driven, framework-based (Agile, TDD)
  Blended: Data-informed with intuitive synthesis

Risk Tolerance:
  Personal: Moderate (willing to experiment)
  Professional: Conservative (safety-critical systems)
  Blended: Conservative with calculated experiments
  Bias: Leans conservative for work decisions

Knowledge Domains:
  - Software engineering (professional)
  - Creative writing (personal)
  - Productivity systems (shared)
```

---

## Troubleshooting

### "Knowledge expansion failed"
- Check your Google API credentials in `.env`
- Verify you haven't exceeded daily quota (100 free queries)
- Check internet connection

### "Profession schema not found"
- Run `onboard-profession` first
- Check `data/professions/` directory exists
- Verify user ID matches

### "Low confidence warning"
- Your profession description may be too brief
- Run `expand-knowledge` for specific areas
- Try interactive onboarding for better extraction

### "Safety validation failed"
- Review your safety rules: `show-profession --section safety`
- This is a protective feature - it means the response might violate your professional rules
- Check if the rule is correct or needs updating

---

## Best Practices

1. **Be Detailed**: More detail = better context. Include specific tools, workflows, constraints.

2. **Update Regularly**: As your role changes, update your profession schema.

3. **Review Safety Rules**: Ensure critical rules are captured. These protect you from bad advice.

4. **Use Knowledge Expansion**: When encountering new topics, let the system expand its knowledge.

5. **Interactive Mode**: Use for first-time onboarding to ensure completeness.

6. **Multi-Profession**: If you have multiple roles, onboard each separately and switch as needed.

7. **Validate Important Decisions**: For critical decisions, always use `validate-response` to check against safety rules.

---

## Privacy & Data

- All profession data stored locally in `data/professions/`
- Web searches cached locally (7-day expiration)
- No profession data sent to servers except:
  - LLM API (for extraction and reasoning)
  - Google Custom Search API (for knowledge expansion)
- You can delete profession data: `rm data/professions/your_profession.json`

---

## Support

For issues or questions:
1. Check `docs/PROFESSION_SYSTEM_ARCHITECTURE.md` for technical details
2. Review examples in `examples/profession_system_examples.py`
3. Open an issue on GitHub

---

## Roadmap

**Coming Soon:**
- [ ] Profession templates (pre-loaded common professions)
- [ ] Visual profession editor
- [ ] Profession sharing/import
- [ ] Analytics dashboard
- [ ] Mobile app support
- [ ] Team profession libraries (for organizations)
