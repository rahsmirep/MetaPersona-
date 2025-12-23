"""
CrossAgentReflectionEngine: Extends ReflectionEngine for cross-agent reflection.
Allows agents to reflect on each other's outputs, detect contradictions, gaps, or misalignment.
"""
from typing import List, Dict, Any
from src.profession.schema import ProfessionSchema

class CrossAgentReflectionEngine:
    def __init__(self, llm_provider):
        self.llm = llm_provider

    def reflect_on_outputs(
        self,
        outputs: List[Dict[str, Any]],
        schemas: List[ProfessionSchema],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Compare and reflect on outputs from multiple agents.
        Returns dict with contradictions, gaps, misalignments, and suggestions.
        """
        context = context or {}
        outputs_text = "\n\n".join([
            f"Agent {i+1} ({schemas[i].profession_name}):\n{outputs[i].get('output') or outputs[i]}"
            for i in range(len(outputs))
        ])
        prompt = f"""
Compare the following outputs from multiple agents. Identify:
- Contradictions or disagreements
- Gaps or missing information
- Misalignment with profession schemas
- Suggestions for convergence or improvement

{outputs_text}

Profession Schemas:
""" + "\n\n".join([
            f"Agent {i+1} Schema:\n{schemas[i].get_context_summary(300)}" for i in range(len(schemas))
        ])
        messages = [
            {"role": "system", "content": "You are an expert evaluator of multi-agent outputs."},
            {"role": "user", "content": prompt}
        ]
        eval_json = self.llm.generate(messages, temperature=0.0)
        import json
        import time
        try:
            result = json.loads(eval_json)
            # Add trace/logging if context requests it
            if context.get('log', False) and hasattr(self, 'shared_memory'):
                trace_log = {
                    "timestamp": time.time(),
                    "outputs": outputs,
                    "schemas": [s.profession_name for s in schemas],
                    "reflection_result": result,
                    "context": context
                }
                self.shared_memory.write(
                    f"cross_agent_reflection:{context.get('trace_id', 'noid')}",
                    trace_log,
                    author="cross_agent_reflection",
                    metadata={"trace_id": context.get('trace_id'), "agents": [s.profession_name for s in schemas]}
                )
            return result
        except Exception:
            # Fallback: return a basic structure
            fallback = {
                "contradictions": [],
                "gaps": [],
                "misalignments": [],
                "suggestions": ["Review outputs for consistency."]
            }
            if context.get('log', False) and hasattr(self, 'shared_memory'):
                trace_log = {
                    "timestamp": time.time(),
                    "outputs": outputs,
                    "schemas": [s.profession_name for s in schemas],
                    "reflection_result": fallback,
                    "context": context
                }
                self.shared_memory.write(
                    f"cross_agent_reflection:{context.get('trace_id', 'noid')}",
                    trace_log,
                    author="cross_agent_reflection",
                    metadata={"trace_id": context.get('trace_id'), "agents": [s.profession_name for s in schemas]}
                )
            return fallback
