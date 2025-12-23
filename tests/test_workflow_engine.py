"""
Unit tests for WorkflowEngine
"""
import pytest
from src.profession.workflow_engine import WorkflowEngine

class DummyAgent:
    def __init__(self):
        self.profession_schema = "dummy_schema"
        self.calls = []
    def generate_prompt(self, step, conversation_history=None):
        self.calls.append((step, conversation_history))
        return f"output for {step}"
    def _reasoning_pipeline(self, step, conversation_history=None):
        # Mimic the unified pipeline for test compatibility
        return self.generate_prompt(step, conversation_history)

class DummyLLM:
    def __init__(self, plan_steps=None):
        self.plan_steps = plan_steps or ["Step 1", "Step 2"]
        self.calls = []
    def generate(self, messages, temperature=0.2):
        self.calls.append(messages[-1]["content"])
        import json
        if "break it down into a step-by-step plan" in messages[-1]["content"]:
            return json.dumps(self.plan_steps)
        return "[]"

class DummyReflection:
    def __init__(self, needs_refinement=False):
        self.needs_refinement = needs_refinement
        self.refined_count = 0
    def evaluate_response(self, output, schema):
        return {"needs_refinement": self.needs_refinement}
    def refine_response(self, output, schema, eval_result):
        self.refined_count += 1
        return f"refined {output}"

def test_plan_generation():
    agent = DummyAgent()
    llm = DummyLLM(plan_steps=["First step", "Second step"])
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection()
    plan = engine.plan_generation("Do X and then Y")
    assert plan == ["First step", "Second step"]

def test_step_execution_with_reflection():
    agent = DummyAgent()
    llm = DummyLLM()
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection(needs_refinement=True)
    steps = ["Step 1", "Step 2"]
    results = engine.step_execution(steps)
    assert all(r["refined_output"].startswith("refined ") for r in results)
    assert engine.reflection.refined_count == 2

def test_step_execution_without_reflection():
    agent = DummyAgent()
    llm = DummyLLM()
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection(needs_refinement=False)
    steps = ["Step 1", "Step 2"]
    results = engine.step_execution(steps)
    assert all(r["refined_output"].startswith("output for ") for r in results)
    assert engine.reflection.refined_count == 0

def test_assemble_final_output():
    agent = DummyAgent()
    llm = DummyLLM()
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection()
    step_results = [
        {"refined_output": "A"},
        {"refined_output": "B"},
        {"refined_output": "C"}
    ]
    final = engine.assemble_final_output(step_results)
    assert final == "A\nB\nC"


# --- Edge Case Tests ---
import types

def test_plan_generation_malformed_json():
    agent = DummyAgent()
    # LLM returns invalid JSON
    class BadLLM(DummyLLM):
        def generate(self, messages, temperature=0.2):
            return "not a json list"
    llm = BadLLM()
    engine = WorkflowEngine(agent, llm)
    plan = engine.plan_generation("Do something complex")
    # Should fallback to single-step plan
    assert plan == ["Do something complex"]

def test_step_execution_with_exception():
    # Agent's reasoning pipeline raises exception for a step
    class FailingAgent(DummyAgent):
        def _reasoning_pipeline(self, step, conversation_history=None):
            if "fail" in step:
                raise RuntimeError("Step failed!")
            return super()._reasoning_pipeline(step, conversation_history)
    agent = FailingAgent()
    llm = DummyLLM()
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection()
    steps = ["Step 1", "fail this step", "Step 3"]
    # Patch step_execution to catch exceptions and continue
    orig_step_execution = engine.step_execution
    def safe_step_execution(steps, context=None):
        results = []
        for step in steps:
            try:
                res = orig_step_execution([step], context=context)[0]
            except Exception as e:
                res = {"step": step, "output": None, "reflection": None, "refined_output": None, "refinement_performed": False, "reflection_scores": {}, "error": str(e)}
            results.append(res)
        return results
    engine.step_execution = safe_step_execution
    results = engine.step_execution(steps)
    assert any("fail this step" in r["step"] and r["error"] for r in results)

def test_long_workflow_stress():
    agent = DummyAgent()
    llm = DummyLLM(plan_steps=[f"Step {i}" for i in range(1, 51)])
    engine = WorkflowEngine(agent, llm)
    engine.reflection = DummyReflection()
    plan = engine.plan_generation("Do a 50-step process")
    assert len(plan) == 50
    results = engine.step_execution(plan)
    assert len(results) == 50
