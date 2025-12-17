# MetaPersona Skills System 🛠️

**Version 0.2** - Modular plugin architecture for extensible agent capabilities.

---

## Overview

The Skills System allows MetaPersona to perform real actions beyond just generating text. Skills are modular plugins that can:
- Execute calculations
- Read and write files
- Search the web
- Chain together for complex workflows
- Be created by users for custom functionality

---

## Architecture

### Core Components

1. **Skill Base Class** (`src/skills/base.py`)
   - Abstract interface for all skills
   - Parameter validation
   - Metadata definition
   - Result handling

2. **Skill Registry** (`src/skills/base.py`)
   - Global skill registration
   - Discovery and lookup
   - Category organization

3. **Skill Manager** (`src/skills/manager.py`)
   - Skill execution
   - Chain coordination
   - History tracking
   - Dynamic loading

4. **Built-in Skills** (`src/skills/builtin/`)
   - Calculator: Mathematical operations
   - File Operations: Read/write files
   - Web Search: DuckDuckGo API

---

## Built-in Skills

### 1. Calculator Skill

**Name:** `calculator`  
**Category:** Utilities

Performs mathematical calculations with support for common math functions.

**Parameters:**
- `expression` (str, required): Mathematical expression to evaluate

**Supported Functions:**
- Basic: `+`, `-`, `*`, `/`, `**`, `%`
- Math: `sqrt()`, `sin()`, `cos()`, `tan()`, `log()`, `log10()`, `exp()`
- Helpers: `abs()`, `round()`, `min()`, `max()`, `sum()`, `pow()`
- Constants: `pi`, `e`

**Example:**
```python
result = skill_manager.execute_skill(
    "calculator",
    expression="sqrt(16) + 2**3"
)
# Result: 12.0
```

**CLI:**
```powershell
python metapersona.py use-skill calculator -p "expression=sin(pi/2) + log(e)"
```

---

### 2. File Operations Skill

**Name:** `file_ops`  
**Category:** File System

Read, write, and manipulate files safely.

**Parameters:**
- `operation` (str, required): Operation to perform
  - `read`: Read file content
  - `write`: Write content to file (overwrites)
  - `append`: Append content to file
  - `exists`: Check if file exists
  - `size`: Get file size in bytes
  - `list_dir`: List directory contents
- `path` (str, required): Path to file or directory
- `content` (str, optional): Content for write/append operations

**Examples:**

Write to file:
```python
result = skill_manager.execute_skill(
    "file_ops",
    operation="write",
    path="./notes.txt",
    content="My important notes"
)
```

Read from file:
```python
result = skill_manager.execute_skill(
    "file_ops",
    operation="read",
    path="./notes.txt"
)
print(result.data)  # "My important notes"
```

**CLI:**
```powershell
python metapersona.py use-skill file_ops -p "operation=read" -p "path=./data/profile.json"
```

---

### 3. Web Search Skill

**Name:** `web_search`  
**Category:** Information

Search the web using DuckDuckGo Instant Answer API (no API key required).

**Parameters:**
- `query` (str, required): Search query
- `max_results` (int, optional, default=3): Maximum results to return

**Returns:**
List of search results with:
- `title`: Result title
- `snippet`: Text snippet
- `url`: Result URL

**Example:**
```python
result = skill_manager.execute_skill(
    "web_search",
    query="Python programming",
    max_results=3
)

for item in result.data:
    print(f"{item['title']}: {item['url']}")
```

**CLI:**
```powershell
python metapersona.py use-skill web_search -p "query=AI agents" -p "max_results=5"
```

---

## Skill Chaining

Execute multiple skills in sequence, passing data between them.

### Chain Format

```python
skill_chain = [
    {
        "skill": "skill_name",
        "parameters": {"param": "value"},
        "output_var": "variable_name",  # Optional: store result
        "continue_on_error": False       # Optional: continue if fails
    },
    # ... more steps
]

results = skill_manager.chain_skills(skill_chain)
```

### Variable Substitution

Use `$variable_name` in parameters to reference previous results:

```python
chain = [
    {
        "skill": "web_search",
        "parameters": {"query": "Python", "max_results": 1},
        "output_var": "search_result"
    },
    {
        "skill": "file_ops",
        "parameters": {
            "operation": "write",
            "path": "./search.txt",
            "content": "$search_result"  # Uses result from previous step
        }
    }
]
```

### Example: Research and Save

```python
# Search web → Calculate → Save results
chain = [
    {"skill": "web_search", "parameters": {"query": "Earth circumference"}, "output_var": "info"},
    {"skill": "calculator", "parameters": {"expression": "40075 / 24"}, "output_var": "km_per_hour"},
    {
        "skill": "file_ops",
        "parameters": {
            "operation": "write",
            "path": "./calculations.txt",
            "content": "Earth's circumference divided by hours in a day"
        }
    }
]

results = skill_manager.chain_skills(chain)
```

---

## Creating Custom Skills

### Step 1: Define Your Skill

Create a new Python file in `src/skills/builtin/` or your own directory:

```python
from src.skills.base import Skill, SkillMetadata, SkillParameter, SkillResult

class WeatherSkill(Skill):
    """Get weather information."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="weather",
            description="Get current weather for a location",
            category="Information",
            version="1.0.0",
            parameters=[
                SkillParameter(
                    name="location",
                    type="str",
                    description="City name or zip code",
                    required=True
                ),
                SkillParameter(
                    name="units",
                    type="str",
                    description="Temperature units (celsius/fahrenheit)",
                    required=False,
                    default="celsius"
                )
            ],
            returns="Weather information including temperature and conditions"
        )
    
    def execute(self, location: str, units: str = "celsius") -> SkillResult:
        """Execute the weather lookup."""
        try:
            # Your implementation here
            # Example: Call weather API
            
            weather_data = {
                "location": location,
                "temperature": 22,
                "conditions": "Sunny",
                "units": units
            }
            
            return SkillResult(
                success=True,
                data=weather_data,
                metadata={"source": "weather_api"}
            )
        
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Weather lookup failed: {str(e)}"
            )
```

### Step 2: Register Your Skill

```python
from src.skills import get_registry
from my_skills import WeatherSkill

# Get global registry
registry = get_registry()

# Register skill
registry.register(WeatherSkill())
```

Or in `metapersona.py`:

```python
from my_skills import WeatherSkill

# In agent initialization
skill_manager.registry.register(WeatherSkill())
```

### Step 3: Use Your Skill

```python
result = skill_manager.execute_skill(
    "weather",
    location="San Francisco",
    units="fahrenheit"
)

if result.success:
    print(result.data)
```

---

## LLM Integration

The persona agent can automatically invoke skills when needed.

### How It Works

1. Agent receives skills list in system prompt
2. LLM decides when to use a skill
3. LLM responds with JSON: `{"action": "use_skill", "skill": "name", "parameters": {...}}`
4. Agent executes skill and returns result

### Example Conversation

**User:** "Calculate the square root of 144"

**Agent (internal):** Recognizes math task, generates:
```json
{
  "action": "use_skill",
  "skill": "calculator",
  "parameters": {"expression": "sqrt(144)"}
}
```

**System:** Executes skill, returns result: `12.0`

**Agent (to user):** "The square root of 144 is 12."

---

## CLI Commands

### List All Skills
```powershell
python metapersona.py skills
```

### Get Skill Details
```powershell
python metapersona.py skill-info <skill_name>
```

### Execute a Skill
```powershell
python metapersona.py use-skill <skill_name> -p "param1=value1" -p "param2=value2"
```

### Examples
```powershell
# Calculator
python metapersona.py use-skill calculator -p "expression=2**10"

# File operations
python metapersona.py use-skill file_ops -p "operation=list_dir" -p "path=./data"

# Web search
python metapersona.py use-skill web_search -p "query=MetaPersona AI" -p "max_results=5"
```

---

## Best Practices

### 1. Skill Design

- **Single Responsibility**: Each skill should do one thing well
- **Clear Metadata**: Provide detailed parameter descriptions
- **Error Handling**: Always return SkillResult with success/error info
- **Validation**: Validate parameters before execution

### 2. Parameter Naming

- Use descriptive names: `file_path` not `fp`
- Use snake_case: `max_results` not `maxResults`
- Mark required vs optional clearly

### 3. Return Data

- Return structured data when possible (dicts, lists)
- Include metadata for context
- Keep data serializable (JSON-compatible)

### 4. Security

- Validate file paths to prevent directory traversal
- Sanitize user inputs
- Limit resource usage (timeouts, size limits)
- Never use `eval()` without sandboxing

---

## Skill Ideas

### Coming Soon
- **Code Execution**: Run Python/JS code safely
- **API Integration**: Call REST APIs
- **Database**: Query local SQLite databases
- **Image Processing**: Resize, crop, convert images
- **Text Analysis**: Sentiment, summarization, translation
- **System Info**: CPU, memory, disk usage

### Community Skills
Want to contribute a skill? Check out the contribution guidelines!

---

## Troubleshooting

### Skill Not Found

```python
# Make sure skill is registered
from src.skills import get_registry
print(get_registry().list_skills())
```

### Import Errors

Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

### Skill Execution Fails

Check error message:
```python
result = skill_manager.execute_skill("skill_name", ...)
if not result.success:
    print(f"Error: {result.error}")
```

### Chain Fails Mid-Way

Use `continue_on_error` flag:
```python
{
    "skill": "risky_skill",
    "parameters": {...},
    "continue_on_error": True  # Don't stop chain if this fails
}
```

---

## API Reference

### Skill Base Class

```python
class Skill(ABC):
    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        """Execute the skill."""
        pass
```

### SkillResult

```python
class SkillResult(BaseModel):
    success: bool               # True if execution succeeded
    data: Any = None           # Result data
    error: Optional[str] = None # Error message if failed
    metadata: Dict[str, Any]    # Additional context
```

### SkillManager

```python
class SkillManager:
    def execute_skill(self, skill_name: str, **parameters) -> SkillResult
    def chain_skills(self, skill_chain: List[Dict]) -> List[SkillResult]
    def list_available_skills(self) -> List[Dict]
    def get_skill_info(self, skill_name: str) -> Optional[Dict]
```

---

## Version History

### v0.2 (Current)
- Initial skills system release
- Built-in skills: calculator, file_ops, web_search
- Skill chaining support
- LLM integration
- CLI commands

### Roadmap
- [ ] Skill marketplace/repository
- [ ] Async skill execution
- [ ] Skill dependencies management
- [ ] Visual skill builder
- [ ] Skill versioning and updates

---

**Questions? Issues?** Open an issue on GitHub or check the main README.md!
