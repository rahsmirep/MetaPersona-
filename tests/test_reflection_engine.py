"""
Unit tests for ReflectionEngine
"""
import pytest
from unittest.mock import MagicMock
from src.profession.reflection_engine import ReflectionEngine
from src.profession.schema import ProfessionSchema, RoleDefinition, ToolsEquipment, DailyTasks, DecisionPatterns, SafetyRules, KnowledgeConfidence, Terminology, EdgeCases

@pytest.fixture
def dummy_schema():
    return ProfessionSchema(
        profession_id="SE-001",
        profession_name="Software Engineer",
        industry="Technology",
        role_definition=RoleDefinition(primary_responsibilities=["Write code"], secondary_responsibilities=[], success_metrics=[], common_challenges=[]),
        tools_equipment=ToolsEquipment(software=["Python"], hardware=[], platforms=[], methodologies=[], certifications=[]),
        daily_tasks=DailyTasks(routine=["Write code"], periodic={}, situational=[]),
        decision_patterns=DecisionPatterns(common_decisions=[], decision_frameworks=[], risk_tolerance=None, information_sources=[], escalation_criteria=[]),
        safety_rules=SafetyRules(critical=["Never deploy untested code"], important=[], best_practices=[], emergency_protocols=[]),
        knowledge_confidence=KnowledgeConfidence(needs_expansion=[], medium_confidence_areas=[], high_confidence_areas=[]),
        terminology=Terminology(jargon={}, acronyms={}, concepts={}),
        edge_cases=EdgeCases(scenarios=[], exceptions=[], escalation_triggers=[]),
        data_sources=[],
        expansion_history=[],
        last_updated=None
    )

class DummyLLM:
    def __init__(self, eval_result=None, refined_response=None):
        self.eval_result = eval_result or {"clarity": 3, "accuracy": 3, "completeness": 3, "alignment": 3, "needs_refinement": True}
        self.refined_response = refined_response or "This is a refined answer."
        self.last_prompt = None
    def generate(self, messages, temperature=0.0):
        self.last_prompt = messages[-1]["content"]
        # Return JSON string for evaluation, plain string for refinement
        if "Evaluate the following response" in self.last_prompt:
            import json
            return json.dumps(self.eval_result)
        return self.refined_response

def test_evaluate_response_triggers_refinement(dummy_schema):
    llm = DummyLLM()
    engine = ReflectionEngine(llm)
    response = "This is an unclear answer."
    result = engine.evaluate_response(response, dummy_schema)
    assert result["needs_refinement"] is True
    assert all(1 <= result[k] <= 5 for k in ["clarity", "accuracy", "completeness", "alignment"])

def test_evaluate_response_no_refinement(dummy_schema):
    llm = DummyLLM(eval_result={"clarity": 5, "accuracy": 5, "completeness": 5, "alignment": 5, "needs_refinement": False})
    engine = ReflectionEngine(llm)
    response = "This is a perfect answer."
    result = engine.evaluate_response(response, dummy_schema)
    assert result["needs_refinement"] is False

def test_refine_response(dummy_schema):
    llm = DummyLLM(refined_response="Improved answer.")
    engine = ReflectionEngine(llm)
    response = "This is an unclear answer."
    feedback = {"clarity": 2, "accuracy": 3, "completeness": 2, "alignment": 3, "needs_refinement": True}
    improved = engine.refine_response(response, dummy_schema, feedback)
    assert improved == "Improved answer."
    assert "revise and improve" in llm.last_prompt.lower()
