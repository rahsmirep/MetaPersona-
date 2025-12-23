from src.personalized_agents import PersonalizedAgent
from src.profession.schema import ProfessionSchema
from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern

import json
class DummyLLM:
    def generate(self, messages, temperature=0.3):
        # Return a mock ProfessionSchema JSON string
        mock_schema = {
            "profession_id": "user_test_test_engineer",
            "profession_name": "Test Engineer",
            "industry": "Testing",
            "role_definition": {"primary_responsibilities": ["writing test cases", "automating tests"], "secondary_responsibilities": [], "success_metrics": [], "common_challenges": []},
            "daily_tasks": {"routine": ["write tests"], "periodic": {}, "situational": []},
            "tools_equipment": {"software": ["pytest"], "hardware": [], "platforms": [], "methodologies": []},
            "environment": {"work_setting": "office", "team_structure": "solo", "pace": "moderate", "autonomy_level": "medium"},
            "constraints": {"regulatory": [], "time_sensitive": [], "resource_limitations": [], "ethical_considerations": [], "legal_requirements": []},
            "terminology": {"jargon": {}, "acronyms": {}, "concepts": {}},
            "decision_patterns": {"common_decisions": [], "decision_frameworks": [], "risk_tolerance": "moderate", "information_sources": [], "escalation_criteria": []},
            "safety_rules": {"critical": [], "important": [], "best_practices": [], "emergency_protocols": []},
            "skill_hierarchy": {"foundational": [], "intermediate": [], "advanced": [], "mastery": [], "soft_skills": []},
            "edge_cases": {},
            "knowledge_confidence": {},
            "last_updated": "2025-12-22T00:00:00",
            "version": "1.0"
        }
        return json.dumps(mock_schema)

class DummyAlignment:
    def create_aligned_persona(self, schema, profile):
        return {"name": profile.user_id, "profession": schema.profession_name}

def test_onboard_from_text():
    # Minimal mock onboarding text and user_id
    raw_text = "I am a Test Engineer in the Testing industry. My main tasks are writing test cases and automating tests."
    user_id = "user_test"
    # Use actual WritingStyle and DecisionPattern models
    writing_style = WritingStyle(
        tone="neutral",
        vocabulary_level="basic",
        sentence_structure="simple",
        punctuation_style="standard"
    )
    decision_pattern = DecisionPattern(
        approach="systematic",
        risk_tolerance="moderate"
    )
    cognitive_profile = CognitiveProfile(
        user_id=user_id,
        writing_style=writing_style,
        decision_pattern=decision_pattern
    )
    # Create agent with dummy alignment and llm
    agent = PersonalizedAgent(
        user_id=user_id,
        profession_schema=ProfessionSchema(
            profession_id="dummy",
            profession_name="Dummy",
            industry="DummyIndustry"
        ),
        cognitive_profile=cognitive_profile,
        llm_provider=DummyLLM()
    )
    agent.alignment = DummyAlignment()  # Override alignment for test
    agent.onboard_from_text(raw_text, user_id)
    assert agent.profession_schema.profession_name != "Dummy"
    assert agent.aligned_persona["profession"] == agent.profession_schema.profession_name
