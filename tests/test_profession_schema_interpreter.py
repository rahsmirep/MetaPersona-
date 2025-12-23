import pytest
from src.profession.profession_schema_interpreter import ProfessionSchemaInterpreter
from src.profession.schema import ProfessionSchema

class DummyLLM:
    pass

def test_mock_extract_schema():
    interpreter = ProfessionSchemaInterpreter(DummyLLM())
    mock_data = {
        "profession_id": "user1_test",
        "profession_name": "Test Profession",
        "industry": "Testing",
        "role_definition": {"primary_responsibilities": ["Test"], "secondary_responsibilities": [], "success_metrics": [], "common_challenges": []},
        "daily_tasks": {"routine": [], "periodic": {}, "situational": []},
        "tools_equipment": {"software": [], "hardware": [], "platforms": [], "methodologies": []},
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
    schema = interpreter.mock_extract_schema(mock_data)
    assert isinstance(schema, ProfessionSchema)
    assert getattr(schema, "profession_name", None) == "Test Profession"
