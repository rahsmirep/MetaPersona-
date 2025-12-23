"""
Integration test: distributed plan executed across three agents with negotiation and merging.
"""
import pytest
from src.distributed.distributed_planning_engine import DistributedPlanningEngine
from src.shared_memory import SharedBlackboard
from src.router import Router

class DummyRulesEngine:
    def classify_task(self, step):
        step_lower = step.lower()
        if 'write' in step_lower:
            return 'writing', 0.9
        if 'research' in step_lower:
            return 'research', 0.8
        return 'planning', 1.0
    def get_candidate_agents(self, task_type):
        if task_type == 'writing':
            return ['writing_agent', 'writing_agent_b']
        if task_type == 'research':
            return ['research_agent']
        return ['planning_agent']

class DummyPlanningAgent:
    def generate_plan_steps(self, user_request, context=None):
        return ["Write introduction", "Research topic", "Write conclusion"]

def test_distributed_plan_execution():
    shared_memory = SharedBlackboard()
    router = Router()
    rules_engine = DummyRulesEngine()
    planning_agent = DummyPlanningAgent()
    engine = DistributedPlanningEngine(router, shared_memory, rules_engine)
    plan = engine.generate_plan("Write a research article", planning_agent)
    fragments = engine.fragment_plan(plan)
    assigned = engine.assign_fragments(fragments)
    # Register three dummy agent handlers
    def handler_write(msg):
        return type('Resp', (), {
            'intent': 'response',
            'payload': {'result': f"written: {msg.payload['fragment']['step']}"},
            'metadata': getattr(msg, 'metadata', {})
        })()
    def handler_research(msg):
        return type('Resp', (), {
            'intent': 'response',
            'payload': {'result': f"researched: {msg.payload['fragment']['step']}"},
            'metadata': getattr(msg, 'metadata', {})
        })()
    router.register_agent('writing_agent', handler_write)
    router.register_agent('writing_agent_b', handler_write)
    router.register_agent('research_agent', handler_research)
    router.register_agent('planning_agent', handler_write)
    executed = engine.execute_distributed_plan(assigned)
    assert all(f.state == "completed" for f in executed)
    assert any(f.result and f.result.startswith("written:") for f in executed)
    assert any(f.result and f.result.startswith("researched:") for f in executed)
    # Check merged results
    results = [f.result for f in executed]
    assert len(results) == 3
