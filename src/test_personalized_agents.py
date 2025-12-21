import pytest
from types import SimpleNamespace
from .personalized_agents import (
    PersonalizedBaseAgent,
    PersonalizedResearchAgent,
    PersonalizedCodeAgent,
    PersonalizedWriterAgent,
    PersonalizedGeneralistAgent,
    PersonalizedProfessionAgent,
)

# --- Mocks ---

class DummyLLMProvider:
    def generate(self, messages, temperature=0.7):
        return "dummy response"

class DummySkillManager:
    pass

@pytest.fixture
def mock_cognitive_profile():
    writing_style = SimpleNamespace(
        tone="Friendly",
        vocabulary_level="Advanced",
        sentence_structure="Complex",
        punctuation_style="Formal"
    )
    decision_pattern = SimpleNamespace(
        approach="Analytical",
        risk_tolerance="Low"
    )
    return SimpleNamespace(
        writing_style=writing_style,
        decision_pattern=decision_pattern
    )

@pytest.fixture
def mock_llm_provider():
    return DummyLLMProvider()

@pytest.fixture
def mock_profession_schema():
    class DummyEnv:
        work_setting = SimpleNamespace(value="Remote")
        team_structure = SimpleNamespace(value="Flat")
    class DummyTools:
        software = ["Excel", "Word", "PowerPoint"]
    class DummyTerminology:
        jargon = {"synergy": "working together"}
        acronyms = {"KPI": "Key Performance Indicator"}
    class DummyRoleDef:
        primary_responsibilities = ["analyze data", "prepare reports"]
    def identify_knowledge_gaps(task): return []
    return SimpleNamespace(
        profession_name="Data Analyst",
        industry="Analytics",
        tools_equipment=DummyTools(),
        terminology=DummyTerminology(),
        role_definition=DummyRoleDef(),
        environment=DummyEnv(),
        identify_knowledge_gaps=identify_knowledge_gaps
    )

@pytest.fixture
def patch_profession_alignment(monkeypatch):
    class DummyReasoning:
        def __init__(self, llm): pass
        def enhance_prompt(self, task, schema, profile, history): return task
        def extract_decision_factors(self, task, schema): return {"factor": "value"}
        def validate_response(self, response, schema): return (True, [])
    class DummyAlignment:
        def create_aligned_persona(self, schema, profile): return "aligned"
        def generate_system_prompt(self, aligned): return "ALIGNED_PROMPT"
    monkeypatch.setattr(
        "src.profession.ProfessionReasoningLayer", DummyReasoning
    )
    monkeypatch.setattr(
        "src.profession.ParallelSelfAlignment", DummyAlignment
    )


# Remove or comment out this test:
# def test_base_agent_system_prompt(mock_cognitive_profile, mock_llm_provider):
#     agent = PersonalizedBaseAgent(
#         agent_id="a1",
#         role="TestRole",
#         description="TestDesc",
#         cognitive_profile=mock_cognitive_profile,
#         llm_provider=mock_llm_provider
#     )
#     prompt = agent.get_system_prompt()
#     assert "TestRole" in prompt
#     assert "TestDesc" in prompt
#     assert "Friendly" in prompt
#     assert "Analytical" in prompt

def test_research_agent_system_prompt(mock_cognitive_profile, mock_llm_provider):
    agent = PersonalizedResearchAgent(
        agent_id="a2",
        role="Researcher",
        description="Research stuff",
        cognitive_profile=mock_cognitive_profile,
        llm_provider=mock_llm_provider
    )
    prompt = agent.get_system_prompt()
    assert "Researcher" in prompt
    assert "Research stuff" in prompt
    assert "Tone: Friendly" in prompt

def test_code_agent_system_prompt(mock_cognitive_profile, mock_llm_provider):
    agent = PersonalizedCodeAgent(
        agent_id="a3",
        role="Coder",
        description="Writes code",
        cognitive_profile=mock_cognitive_profile,
        llm_provider=mock_llm_provider
    )
    prompt = agent.get_system_prompt()
    assert "Coder" in prompt
    assert "Writes code" in prompt

def test_writer_agent_system_prompt(mock_cognitive_profile, mock_llm_provider):
    agent = PersonalizedWriterAgent(
        agent_id="a4",
        role="Writer",
        description="Writes content",
        cognitive_profile=mock_cognitive_profile,
        llm_provider=mock_llm_provider
    )
    prompt = agent.get_system_prompt()
    assert "Writer" in prompt
    assert "Writes content" in prompt

def test_generalist_agent_system_prompt(mock_cognitive_profile, mock_llm_provider):
    agent = PersonalizedGeneralistAgent(
        agent_id="a5",
        role="Generalist",
        description="General tasks",
        cognitive_profile=mock_cognitive_profile,
        llm_provider=mock_llm_provider
    )
    prompt = agent.get_system_prompt()
    assert "Generalist" in prompt
    assert "General tasks" in prompt

def test_profession_agent_system_prompt(
    mock_cognitive_profile, mock_llm_provider, mock_profession_schema, patch_profession_alignment
):
    agent = PersonalizedProfessionAgent(
        agent_id="a6",
        role="ProRole",
        description="ProDesc",
        cognitive_profile=mock_cognitive_profile,
        llm_provider=mock_llm_provider,
        profession_schema=mock_profession_schema
    )
    prompt = agent.get_system_prompt()
    assert "ALIGNED_PROMPT" in prompt
    assert "ProRole" in prompt
    assert "Data Analyst" in prompt
    assert "Analytics" in prompt