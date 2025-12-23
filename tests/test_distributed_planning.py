"""
Unit tests for distributed planning: plan fragmentation, negotiation, and distributed execution.
"""
import pytest
from src.distributed.plan_fragment import PlanFragment
from src.distributed.negotiation_protocol import NegotiationProtocol
from src.distributed.distributed_planning_engine import DistributedPlanningEngine
from src.shared_memory import SharedBlackboard
from src.router import Router

class DummyRulesEngine:
    def classify_task(self, step):
        # Simple mapping for test
        step_lower = step.lower()
        if 'write introduction' in step_lower or 'write conclusion' in step_lower:
            return 'writing', 0.9
        if 'write' in step_lower:
            return 'writing', 0.9
        if 'research' in step_lower:
            return 'research', 0.8
        return 'planning', 1.0
    def get_candidate_agents(self, task_type):
        # Return only writing agents for writing tasks
        if task_type == 'writing':
            return ['writing_agent', 'writing_agent_b']
        if task_type == 'research':
            return ['research_agent']
        if task_type == 'planning':
            return ['planning_agent']
        return []

class DummyPlanningAgent:
    def generate_plan_steps(self, user_request, context=None):
        return ["Write introduction", "Research topic", "Write conclusion"]

@pytest.fixture
def shared_memory():
    return SharedBlackboard()

@pytest.fixture
def router():
    return Router()

@pytest.fixture
def rules_engine():
    return DummyRulesEngine()

@pytest.fixture
def planning_agent():
    return DummyPlanningAgent()

def test_plan_fragmentation(shared_memory, router, rules_engine, planning_agent):
    engine = DistributedPlanningEngine(router, shared_memory, rules_engine)
    plan = engine.generate_plan("Write a research article", planning_agent)
    fragments = engine.fragment_plan(plan)
    assert len(fragments) == 3
    assert all(isinstance(f, PlanFragment) for f in fragments)

def test_negotiation_protocol(shared_memory):
    protocol = NegotiationProtocol(shared_memory)
    outcome = protocol.initiate_negotiation("frag-1", ["agent_a", "agent_b", "agent_c"])
    assert outcome["selected_agent"] == "agent_a"
    logs = shared_memory.read("negotiation:frag-1")
    assert logs["selected_agent"] == "agent_a"

def test_fragment_assignment(shared_memory, router, rules_engine, planning_agent):
    engine = DistributedPlanningEngine(router, shared_memory, rules_engine)
    plan = engine.generate_plan("Write a research article", planning_agent)
    fragments = engine.fragment_plan(plan)
    assigned = engine.assign_fragments(fragments)
    assert all(f.assigned_agent for f in assigned)
    # Writing step should be negotiated and assigned to a writing agent
    writing_frags = [f for f in assigned if 'Write introduction' in f.step or 'Write conclusion' in f.step]
    for writing_frag in writing_frags:
        assert writing_frag.assigned_agent in ["writing_agent", "writing_agent_b"]

def test_distributed_execution(shared_memory, router, rules_engine, planning_agent):
    engine = DistributedPlanningEngine(router, shared_memory, rules_engine)
    plan = engine.generate_plan("Write a research article", planning_agent)
    fragments = engine.fragment_plan(plan)
    assigned = engine.assign_fragments(fragments)
    # Register dummy agent handlers
    for f in assigned:
        def handler(msg):
            class Resp:
                def __init__(self, step):
                    self.payload = {'result': f"done: {step}"}
                    self.intent = 'response'
                    self.metadata = {}
            return Resp(msg.payload['fragment']['step'])
        router.register_agent(f.assigned_agent, handler)
    executed = engine.execute_distributed_plan(assigned)
    assert all(f.state == "completed" for f in executed)
    assert all(f.result.startswith("done:") for f in executed)
