import pytest
from src.personalized_agents import PersonalizedAgent
from src.profession.schema import ProfessionSchema
from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern

# Minimal mocks for required ProfessionSchema subfields
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
from src.router import Router
from src.agent_messaging import AgentMessage

class DummyLLM:
    def generate(self, messages, temperature=0.3):
        # Return a simple JSON list for planning, or a string for step outputs
        if any("step-by-step plan" in m.get("content", "") for m in messages):
            return '["Step 1: Analyze the problem", "Step 2: Propose a solution"]'
        if any("Evaluate the following response" in m.get("content", "") for m in messages):
            return {"clarity": 5, "accuracy": 5, "completeness": 5, "alignment": 5, "needs_refinement": False}
        return "Step output"

@pytest.fixture
def agent_schema():
    return ProfessionSchema(
        profession_id="test-001",
        profession_name="TestAgent",
        industry="TestIndustry",
        decision_patterns=MockDecisionPatterns(),
        tools_equipment=MockToolsEquipment(),
        skill_hierarchy=MockSkillHierarchy(),
        constraints=MockConstraints(),
        environment=MockEnvironment(),
        role_definition=MockRoleDefinition(),
        safety_rules=MockSafetyRules(),
        terminology=MockTerminology()
    )

@pytest.fixture
def agent_profile():
    writing_style = WritingStyle(tone="neutral", vocabulary_level="basic", sentence_structure="simple")
    decision_pattern = DecisionPattern(approach="direct", risk_tolerance="low")
    return CognitiveProfile(user_id="user", writing_style=writing_style, decision_pattern=decision_pattern)

def test_agent_to_agent_delegation(agent_schema, agent_profile):
    router = Router()
    agent_a = PersonalizedAgent(
        user_id="agent_a",
        profession_schema=agent_schema,
        cognitive_profile=agent_profile,
        llm_provider=DummyLLM(),
        router=router
    )
    agent_b = PersonalizedAgent(
        user_id="agent_b",
        profession_schema=agent_schema,
        cognitive_profile=agent_profile,
        llm_provider=DummyLLM(),
        router=router
    )
    # Agent A delegates a task to Agent B
    msg = AgentMessage(
        sender="agent_a",
        receiver="agent_b",
        intent="request",
        payload={"user_request": "Please analyze and solve this problem."},
        metadata={}
    )
    response = router.route_message(msg)
    assert response is not None
    assert response.intent == "response"
    assert response.sender == "agent_b"
    assert "Step 1: Analyze the problem" in response.payload["result"]
    assert "Step 2: Propose a solution" in response.payload["result"]
