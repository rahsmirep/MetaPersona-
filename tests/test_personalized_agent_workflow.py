import pytest
from src.personalized_agents import PersonalizedAgent
from src.profession.schema import ProfessionSchema
from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern

class DummyLLM:
    def generate(self, messages, temperature=0.3):
        # Return a simple JSON list for planning, or a string for step outputs
        if any("step-by-step plan" in m.get("content", "") for m in messages):
            return '["Step 1: Analyze the problem", "Step 2: Propose a solution", "Step 3: Summarize findings"]'
        if any("Evaluate the following response" in m.get("content", "") for m in messages):
            return {"clarity": 5, "accuracy": 5, "completeness": 5, "alignment": 5, "needs_refinement": False}
        return "Step output"

class MockDecisionPatterns:
    decision_frameworks = ["framework1", "framework2"]
    risk_tolerance = type("RiskTolerance", (), {"value": "moderate"})()
    information_sources = ["source1", "source2"]

class MockToolsEquipment:
    software = ["ToolA"]
    platforms = ["PlatformA"]
    methodologies = ["MethodA"]

class MockSkillHierarchy:
    advanced = ["SkillA", "SkillB"]

class MockConstraints:
    regulatory = ["RegulationA"]
    ethical_considerations = ["EthicsA"]
    time_sensitive = ["TimeA"]

class MockEnvironment:
    autonomy_level = type("AutonomyLevel", (), {"value": "high"})()
    team_structure = type("TeamStructure", (), {"value": "collaborative"})()
    pace = type("Pace", (), {"value": "fast"})()
    work_setting = type("WorkSetting", (), {"value": "remote"})()

class MockRoleDefinition:
    primary_responsibilities = ["ResponsibilityA"]

class MockSafetyRules:
    critical = ["Never do X"]
    important = ["Avoid Y"]

class MockTerminology:
    jargon = {"termA": "definitionA"}

class MockWritingStyle:
    tone = "formal"
    vocabulary_level = "advanced"
    sentence_structure = "complex"

class MockDecisionPattern:
    approach = "analytical"
    risk_tolerance = "moderate"

@pytest.fixture
def agent():
    profession_schema = ProfessionSchema(
        profession_id="eng-001",
        profession_name="Engineer",
        industry="Tech",
        decision_patterns=MockDecisionPatterns(),
        tools_equipment=MockToolsEquipment(),
        skill_hierarchy=MockSkillHierarchy(),
        constraints=MockConstraints(),
        environment=MockEnvironment(),
        role_definition=MockRoleDefinition(),
        safety_rules=MockSafetyRules(),
        terminology=MockTerminology()
    )
    writing_style = WritingStyle(
        tone="formal",
        vocabulary_level="advanced",
        sentence_structure="complex"
    )
    decision_pattern = DecisionPattern(
        approach="analytical",
        risk_tolerance="moderate"
    )
    cognitive_profile = CognitiveProfile(
        user_id="user123",
        writing_style=writing_style,
        decision_pattern=decision_pattern
    )
    return PersonalizedAgent(
        user_id="agent1",
        profession_schema=profession_schema,
        cognitive_profile=cognitive_profile,
        llm_provider=DummyLLM()
    )

def test_run_workflow_basic(agent):
    user_request = "Please analyze the problem and propose a solution."
    output = agent.run_workflow(user_request)
    # Check that each planned step appears in the output
    assert "Step 1: Analyze the problem" in output
    assert "Step 2: Propose a solution" in output
    assert "Step 3: Summarize findings" in output

def test_run_workflow_with_history(agent):
    user_request = "Summarize the findings from the last meeting."
    history = [{"role": "user", "content": "What happened in the meeting?"}]
    output = agent.run_workflow(user_request, conversation_history=history)
    # Check that each planned step appears in the output
    assert "Step 1: Analyze the problem" in output
    assert "Step 2: Propose a solution" in output
    assert "Step 3: Summarize findings" in output


# --- Edge Case Tests ---
import types

def test_run_workflow_with_malformed_schema():
    # ProfessionSchema missing required attribute
    from src.personalized_agents import PersonalizedAgent
    from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern
    class IncompleteSchema:
        profession_name = "Broken"
        industry = "None"
    writing_style = WritingStyle(tone="formal", vocabulary_level="basic", sentence_structure="simple")
    decision_pattern = DecisionPattern(approach="direct", risk_tolerance="low")
    cognitive_profile = CognitiveProfile(user_id="u", writing_style=writing_style, decision_pattern=decision_pattern)
    with pytest.raises(TypeError):
        PersonalizedAgent(user_id="u", profession_schema=IncompleteSchema(), cognitive_profile=cognitive_profile, llm_provider=DummyLLM())

def test_run_workflow_with_missing_cognitive_profile():
    from src.personalized_agents import PersonalizedAgent
    from src.profession.schema import ProfessionSchema
    class IncompleteProfile:
        user_id = "u"
    schema = ProfessionSchema(
        profession_id="id",
        profession_name="n",
        industry="i",
        decision_patterns=MockDecisionPatterns(),
        tools_equipment=MockToolsEquipment(),
        skill_hierarchy=MockSkillHierarchy(),
        constraints=MockConstraints(),
        environment=MockEnvironment(),
        role_definition=MockRoleDefinition(),
        safety_rules=MockSafetyRules(),
        terminology=MockTerminology()
    )
    with pytest.raises(TypeError):
        PersonalizedAgent(user_id="u", profession_schema=schema, cognitive_profile=IncompleteProfile(), llm_provider=DummyLLM())

def test_run_workflow_with_reflection_failure(agent, monkeypatch):
    # Patch agent's workflow engine reflection to raise error
    def bad_evaluate_response(*a, **kw):
        raise RuntimeError("Reflection failed!")
    agent.workflow_engine.reflection.evaluate_response = bad_evaluate_response
    user_request = "Do something"
    try:
        agent.run_workflow(user_request)
    except RuntimeError as e:
        assert "Reflection failed!" in str(e)

def test_run_workflow_with_llm_failure(agent, monkeypatch):
    # Patch LLM to raise error
    def bad_generate(*a, **kw):
        raise RuntimeError("LLM failure!")
    agent.llm_provider.generate = bad_generate
    user_request = "Do something else"
    try:
        agent.run_workflow(user_request)
    except RuntimeError as e:
        assert "LLM failure!" in str(e)
