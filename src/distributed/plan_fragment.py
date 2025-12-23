"""
PlanFragment: Data structure for distributed planning and execution.
Represents a sub-task/step in a distributed plan, with traceability and assignment.
"""
from typing import Any, Dict, List, Optional
import uuid
import time

class PlanFragment:
    def __init__(
        self,
        step: str,
        parent_plan_id: Optional[str] = None,
        assigned_agent: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.fragment_id = str(uuid.uuid4())
        self.parent_plan_id = parent_plan_id
        self.step = step
        self.assigned_agent = assigned_agent
        self.dependencies = dependencies or []
        self.state = "pending"  # pending, in_progress, completed, failed
        self.result = None
        self.trace: List[Dict[str, Any]] = []
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.updated_at = self.created_at

    def update_state(self, new_state: str, result: Any = None, info: Optional[Dict[str, Any]] = None):
        self.state = new_state
        self.updated_at = time.time()
        if result is not None:
            self.result = result
        trace_entry = {
            "timestamp": self.updated_at,
            "state": new_state,
            "result": result,
            "info": info or {},
        }
        self.trace.append(trace_entry)

    def assign_agent(self, agent_id: str):
        self.assigned_agent = agent_id
        self.updated_at = time.time()
        self.trace.append({
            "timestamp": self.updated_at,
            "action": "assigned",
            "agent": agent_id
        })

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fragment_id": self.fragment_id,
            "parent_plan_id": self.parent_plan_id,
            "step": self.step,
            "assigned_agent": self.assigned_agent,
            "dependencies": self.dependencies,
            "state": self.state,
            "result": self.result,
            "trace": self.trace,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
