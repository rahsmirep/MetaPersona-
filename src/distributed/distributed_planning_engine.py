"""
DistributedPlanningEngine: Orchestrates distributed plan generation, fragmentation, assignment, negotiation, and execution.
Integrates with Router, SharedMemory, and all agent/consensus modules.
"""
from typing import List, Dict, Any, Optional
from src.distributed.plan_fragment import PlanFragment
from src.distributed.negotiation_protocol import NegotiationProtocol
import uuid
import time

class DistributedPlanningEngine:
    def __init__(self, router, shared_memory, rules_engine):
        self.router = router
        self.shared_memory = shared_memory
        self.rules_engine = rules_engine
        self.negotiation = NegotiationProtocol(shared_memory)

    def generate_plan(self, user_request: str, planning_agent, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Use the PlanningAgent to generate a multi-step plan.
        Store the plan in SharedMemory with traceability.
        """
        context = context or {}
        plan_id = str(uuid.uuid4())
        steps = planning_agent.generate_plan_steps(user_request, context)
        plan = {
            "plan_id": plan_id,
            "user_request": user_request,
            "steps": steps,
            "created_at": time.time(),
            "context": context
        }
        self.shared_memory.write(f"plan:{plan_id}", plan, author="distributed_planning_engine", metadata={"plan_id": plan_id})
        return plan

    def fragment_plan(self, plan: Dict[str, Any]) -> List[PlanFragment]:
        """
        Break a plan into fragments (one per step by default).
        """
        fragments = []
        for step in plan["steps"]:
            fragment = PlanFragment(step=step, parent_plan_id=plan["plan_id"])
            fragments.append(fragment)
        return fragments

    def assign_fragments(self, fragments: List[PlanFragment], context: Optional[Dict[str, Any]] = None) -> List[PlanFragment]:
        """
        Assign each fragment to the best agent (with negotiation if needed).
        Prefer writing agents for writing steps if available.
        """
        context = context or {}
        for fragment in fragments:
            task_type, _ = self.rules_engine.classify_task(fragment.step)
            candidate_agents = self.rules_engine.get_candidate_agents(task_type)
            # Prefer writing agents for writing steps
            if task_type == 'writing':
                writing_agents = [a for a in candidate_agents if 'writing' in a]
                if writing_agents:
                    if len(writing_agents) > 1:
                        negotiation_result = self.negotiation.initiate_negotiation(fragment.fragment_id, writing_agents, context)
                        assigned_agent = negotiation_result["selected_agent"]
                    else:
                        assigned_agent = writing_agents[0]
                else:
                    assigned_agent = candidate_agents[0]
            elif len(candidate_agents) > 1:
                negotiation_result = self.negotiation.initiate_negotiation(fragment.fragment_id, candidate_agents, context)
                assigned_agent = negotiation_result["selected_agent"]
            else:
                assigned_agent = candidate_agents[0]
            fragment.assign_agent(assigned_agent)
            self.shared_memory.write(f"fragment:{fragment.fragment_id}", fragment.to_dict(), author="distributed_planning_engine", metadata={"plan_id": fragment.parent_plan_id, "assigned_agent": assigned_agent})
        return fragments

    def execute_distributed_plan(self, fragments: List[PlanFragment], context: Optional[Dict[str, Any]] = None, parallel: bool = False) -> List[PlanFragment]:
        """
        Execute plan fragments sequentially or in parallel, update states/results in SharedMemory.
        """
        context = context or {}
        has_dependencies = any(getattr(f, 'dependencies', None) for f in fragments)
        if parallel or has_dependencies:
            executed_fragments = self.router.dispatch_parallel_fragments(fragments, self.shared_memory, context)
        else:
            executed_fragments = []
            for fragment in fragments:
                fragment.update_state("in_progress")
                from src.agent_messaging import AgentMessage
                msg = AgentMessage(
                    sender="distributed_planning_engine",
                    receiver=fragment.assigned_agent,
                    intent="execute_fragment",
                    payload={"fragment": fragment.to_dict(), "context": context},
                    metadata={"plan_id": fragment.parent_plan_id, "fragment_id": fragment.fragment_id}
                )
                response = self.router.route_message(msg)
                if response and response.payload:
                    fragment.update_state("completed", result=response.payload.get("result"))
                else:
                    fragment.update_state("failed", result=None)
                self.shared_memory.update(f"fragment:{fragment.fragment_id}", fragment.to_dict(), author="distributed_planning_engine", metadata={"plan_id": fragment.parent_plan_id, "assigned_agent": fragment.assigned_agent})
                executed_fragments.append(fragment)
        return executed_fragments

    # Additional methods for branching, merging, and advanced distributed execution can be added here.
