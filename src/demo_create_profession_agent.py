import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from types import SimpleNamespace
from src.profession_schema_interpreter import ProfessionSchemaInterpreter
from src.personalized_agents import PersonalizedAgent 

def dict_to_namespace(d):
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_namespace(i) for i in d]
    else:
        return d

# Dummy cognitive profile for testing
class DummyCognitiveProfile:
    def __init__(self):
        self.user_id = "test_user"
        self.writing_style = SimpleNamespace(
            tone="Friendly",
            vocabulary_level="Advanced",
            sentence_structure="Complex",
            punctuation_style="Formal"
        )
        self.decision_pattern = SimpleNamespace(
            approach="Analytical",
            risk_tolerance="Low"
        )

# Dummy LLM provider for testing
class DummyLLMProvider:
    def generate(self, messages, temperature=0.7):
        return "dummy response"

your_cognitive_profile = DummyCognitiveProfile()
your_llm_provider = DummyLLMProvider()

onboarding_text = """
Profession: Data Analyst
Industry: Analytics
Tools: Excel, Word, PowerPoint
Terminology: KPI, ROI, Synergy
Role: Analyze data, prepare reports
Environment: Remote, Flat team
Education: Bachelor's in Statistics
Certifications: CAP
Regulations: GDPR
Soft Skills: Communication, Problem-solving
"""
from src.profession.schema import ProfessionSchema  # Adjust the import path if needed

from inspect import signature

interpreter = ProfessionSchemaInterpreter()
profession_schema_dict = interpreter.extract_profession_schema(onboarding_text)

# Get the parameter names for ProfessionSchema's __init__, skipping 'self'
schema_params = list(signature(ProfessionSchema.__init__).parameters.keys())[1:]

# Filter the dict to only include accepted keys
filtered_dict = {k: v for k, v in profession_schema_dict.items() if k in schema_params}

# Add missing required fields with dummy values if needed
for param in schema_params:
    if param not in filtered_dict:
        filtered_dict[param] = "test_value"  # or another sensible default

profession_schema = ProfessionSchema(**filtered_dict)

agent = PersonalizedAgent(
    agent_id="agent1",
    role="Data Analyst",
    description="Analyzes data and prepares reports",
    cognitive_profile=your_cognitive_profile,
    llm_provider=your_llm_provider,
    profession_schema=profession_schema
)

print(agent)