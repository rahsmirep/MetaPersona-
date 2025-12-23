from src.personalized_agents import PersonalizedAgent
from src.profession.schema import ProfessionSchema
from src.cognitive_profile import CognitiveProfile, WritingStyle, DecisionPattern
import json
import pytest

class DummyLLMReflection:
    def __init__(self):
        self.calls = []
    def generate(self, messages, temperature=0.3):
        prompt = messages[-1]["content"]
        self.calls.append(prompt)
        if "Evaluate the following response" in prompt:
            # Simulate a low score to trigger refinement
            return json.dumps({"clarity": 2, "accuracy": 2, "completeness": 2, "alignment": 2, "needs_refinement": True})
        if "revise and improve" in prompt:
            return "This is a refined answer."
        # Fallback: return a generic string
        return "Initial answer."

class DummyAlignment:
    def create_aligned_persona(self, schema, profile):
        return {"name": profile.user_id, "profession": schema.profession_name}

def test_generate_prompt_with_reflection():
    user_id = "user_test"
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
    agent = PersonalizedAgent(
        user_id=user_id,
        profession_schema=ProfessionSchema(
            profession_id="dummy",
            profession_name="Dummy",
            industry="DummyIndustry"
        ),
        cognitive_profile=cognitive_profile,
        llm_provider=DummyLLMReflection()
    )
    agent.alignment = DummyAlignment()
    # Should trigger reflection and refinement
    result = agent.generate_prompt("How do I write good tests?", conversation_history=None)
    assert result == "This is a refined answer."
    # Check that both evaluation and refinement prompts were called
    assert any("Evaluate the following response" in c for c in agent.llm_provider.calls)
    assert any("revise and improve" in c for c in agent.llm_provider.calls)
