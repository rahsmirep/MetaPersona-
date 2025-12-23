"""
Unit tests for FragmentDependencyGraph and ParallelExecutionEngine.
"""
import pytest
from src.parallel.fragment_dependency_graph import FragmentDependencyGraph
from src.parallel.parallel_execution_engine import ParallelExecutionEngine

class DummyFragment:
    def __init__(self, fragment_id, dependencies=None, result=None, updated_at=0, metadata=None):
        self.fragment_id = fragment_id
        self.dependencies = dependencies or []
        self.result = result
        self.updated_at = updated_at
        self.metadata = metadata or {}
        self.state = 'pending'
    def update_state(self, new_state, result=None):
        self.state = new_state
        if result is not None:
            self.result = result

# --- Dependency Graph ---
def test_dependency_graph_ready_and_blocked():
    g = FragmentDependencyGraph()
    f1 = DummyFragment('f1')
    f2 = DummyFragment('f2', dependencies=['f1'])
    f3 = DummyFragment('f3', dependencies=['f1'])
    g.add_fragment(f1)
    g.add_fragment(f2, depends_on=f2.dependencies)
    g.add_fragment(f3, depends_on=f3.dependencies)
    assert set(f.fragment_id for f in g.get_ready_fragments()) == {'f1'}
    g.mark_completed('f1')
    ready = set(f.fragment_id for f in g.get_ready_fragments())
    assert ready == {'f2', 'f3'}
    assert g.is_blocked('f2') is False
    assert g.is_blocked('f3') is False
    g.mark_completed('f2')
    g.mark_completed('f3')
    assert g.all_completed()

# --- ParallelExecutionEngine merge logic ---
def test_parallel_merge_last_write():
    class DummyShared:
        def log_merge_decision(self, group_id, merge_info):
            self.logged = (group_id, merge_info)
    shared = DummyShared()
    engine = ParallelExecutionEngine(router=None, shared_memory=shared)
    f1 = DummyFragment('f1', result='A', updated_at=1)
    f2 = DummyFragment('f2', result='B', updated_at=3)
    f3 = DummyFragment('f3', result='C', updated_at=2)
    merged = engine.merge_results([f1, f2, f3], group_id='g1', merge_strategy='last_write_wins')
    assert merged == 'B'
    assert shared.logged[0] == 'g1'
    assert shared.logged[1]['strategy'] == 'last_write_wins'

def test_parallel_merge_priority():
    class DummyShared:
        def log_merge_decision(self, group_id, merge_info):
            self.logged = (group_id, merge_info)
    shared = DummyShared()
    engine = ParallelExecutionEngine(router=None, shared_memory=shared)
    f1 = DummyFragment('f1', result='A', metadata={'priority': 1})
    f2 = DummyFragment('f2', result='B', metadata={'priority': 5})
    merged = engine.merge_results([f1, f2], group_id='g2', merge_strategy='priority')
    assert merged == 'B'
    assert shared.logged[0] == 'g2'
    assert shared.logged[1]['strategy'] == 'priority'

def test_parallel_merge_agent_weighted():
    class DummyShared:
        def log_merge_decision(self, group_id, merge_info):
            self.logged = (group_id, merge_info)
    shared = DummyShared()
    engine = ParallelExecutionEngine(router=None, shared_memory=shared)
    f1 = DummyFragment('f1', result='A', metadata={'agent_weight': 2})
    f2 = DummyFragment('f2', result='B', metadata={'agent_weight': 10})
    merged = engine.merge_results([f1, f2], group_id='g3', merge_strategy='agent_weighted')
    assert merged == 'B'
    assert shared.logged[0] == 'g3'
    assert shared.logged[1]['strategy'] == 'agent_weighted'
