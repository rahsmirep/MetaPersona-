import pytest
from src.personalized_agents import PersonalizedAgent
from src.profession.schema import ProfessionSchema
from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern

class DummyLLM:
    def generate(self, messages, temperature=0.3):
        return '{"decision_type": "technical", "urgency": "immediate", "risk_level": "low"}'

class MockDecisionPatterns:
    decision_frameworks = ["framework1"]
    risk_tolerance = type("Mock", (), {"value": "moderate"})()
    information_sources = ["source1"]

class MockToolsEquipment:
    software = ["ToolA"]
    platforms = ["PlatformA"]
    methodologies = ["MethodA"]

class MockSkillHierarchy:
    advanced = ["SkillA"]

class MockConstraints:
    regulatory = ["RegulationA"]
    ethical_considerations = ["EthicsA"]
    time_sensitive = ["TimeA"]

class MockEnvironment:
    autonomy_level = type("Mock", (), {"value": "high"})()
    team_structure = type("Mock", (), {"value": "collaborative"})()
    pace = type("Mock", (), {"value": "fast"})()
    work_setting = type("Mock", (), {"value": "remote"})()

class MockRoleDefinition:
    primary_responsibilities = ["ResponsibilityA"]

class MockSafetyRules:
    critical = ["Never do X"]
    important = ["Avoid Y"]

class MockTerminology:
    jargon = {"termA": "definitionA"}

@pytest.fixture
def agent():
    profession_schema = ProfessionSchema(
        profession_id="test_id",
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

def test_persona_config(agent):
    config = agent.get_persona_config()
    assert isinstance(config, dict)
    assert config["name"] == "user123 (Professional Mode)"
    assert config["profession"] == "Engineer"
    assert config["industry"] == "Tech"