"""
ReflectionEngine: Evaluates and refines agent responses for clarity, accuracy, completeness, and schema alignment.
"""
from typing import Any, Dict, Tuple
from src.profession.schema import ProfessionSchema

class ReflectionEngine:
    def __init__(self, llm_provider):
        self.llm = llm_provider

    def evaluate_response(self, response: str, schema: ProfessionSchema) -> Dict[str, Any]:
        """
        Score the response for clarity, accuracy, completeness, and schema alignment.
        Returns a dict with scores and a flag for refinement.
        """
        # For now, use a simple LLM-based rubric (mockable in tests)
        prompt = f"""
Evaluate the following response for:
- Clarity
- Accuracy (per the provided profession schema)
- Completeness
- Alignment with profession schema

Response:
{response}

Profession Schema (summary):
{schema.get_context_summary(500)}

Return a JSON with keys: clarity, accuracy, completeness, alignment (scores 1-5), and needs_refinement (bool, true if any score < 4).
"""
        messages = [
            {"role": "system", "content": "You are an expert evaluator of professional responses."},
            {"role": "user", "content": prompt}
        ]
        eval_json = self.llm.generate(messages, temperature=0.0)
        # In production, parse and validate JSON; here, assume dict for testability
        if isinstance(eval_json, dict):
            return eval_json
        import json
        try:
            return json.loads(eval_json)
        except Exception:
            # Fallback: always trigger refinement if parsing fails
            return {"clarity": 2, "accuracy": 2, "completeness": 2, "alignment": 2, "needs_refinement": True}

    def refine_response(self, response: str, schema: ProfessionSchema, feedback: Dict[str, Any]) -> str:
        """
        Request a second-pass answer, using feedback from evaluation.
        """
        prompt = f"""
The previous response was evaluated as follows:
Clarity: {feedback.get('clarity')}/5
Accuracy: {feedback.get('accuracy')}/5
Completeness: {feedback.get('completeness')}/5
Alignment: {feedback.get('alignment')}/5

Please revise and improve the answer, focusing on any areas with a score below 4. Use the profession schema for reference.

Original Response:
{response}

Profession Schema (summary):
{schema.get_context_summary(500)}
"""
        messages = [
            {"role": "system", "content": "You are an expert professional assistant."},
            {"role": "user", "content": prompt}
        ]
        return self.llm.generate(messages, temperature=0.2)
