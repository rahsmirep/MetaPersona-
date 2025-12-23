from typing import Dict, Callable, Optional, List, Any
from src.agent_messaging import AgentMessage
import time

class Router:
    def route_message(self, msg):
        print(f"[ROUTER] route_message called: sender={msg.sender}, receiver={msg.receiver}, fragment_id={msg.payload.get('fragment', {}).get('fragment_id', 'N/A')}")
        handler = self._agents.get(msg.receiver)
        if handler:
            return handler(msg)
        else:
            print(f"[ROUTER] No handler for agent {msg.receiver}")
            return None

    def dispatch_parallel_fragments(self, fragments: List[Any], shared_memory, context: dict = None) -> List[Any]:
        """
        Dispatch multiple plan fragments concurrently using ParallelExecutionEngine.
        Tracks parallel execution groups and ensures traceability.
        """
        from src.parallel.parallel_execution_engine import ParallelExecutionEngine
        from src.parallel.fragment_dependency_graph import FragmentDependencyGraph
        context = context or {}
        # Build dependency graph from fragment dependencies (if any)
        dep_graph = FragmentDependencyGraph()
        for fragment in fragments:
            depends_on = getattr(fragment, 'dependencies', None)
            dep_graph.add_fragment(fragment, depends_on=depends_on)
        # Track group id for traceability
        group_id = f"parallel_group:{int(time.time()*1000)}"
        for fragment in fragments:
            if not hasattr(fragment, 'metadata') or fragment.metadata is None:
                fragment.metadata = {}
            fragment.metadata['parallel_group_id'] = group_id
        shared_memory.write(f"parallel_group:{group_id}", [f.fragment_id for f in fragments], author="router", metadata={"group_id": group_id})
        # Execute in parallel
        engine = ParallelExecutionEngine(self, shared_memory)
        executed = engine.execute(fragments, dep_graph, context)
        # Log completion
        self._log_event('parallel_group_complete', 'router', None, 'parallel_execution', {'group_id': group_id, 'fragments': [f.fragment_id for f in executed]}, {'group_id': group_id})
        return executed
    def route_plan_fragments(self, fragments: List[Any], context: dict = None) -> List[Any]:
        """
        Orchestrate distributed execution of plan fragments (sequentially or in parallel).
        Each fragment must have assigned_agent and fragment_id.
        """
        context = context or {}
        results = []
        for fragment in fragments:
            self._log_event('route_fragment', 'router', fragment.assigned_agent, 'execute_fragment', fragment.step, {'fragment_id': fragment.fragment_id, 'plan_id': fragment.parent_plan_id})
            from src.agent_messaging import AgentMessage
            msg = AgentMessage(
                sender='router',
                receiver=fragment.assigned_agent,
                intent='execute_fragment',
                payload={'fragment': fragment.to_dict(), 'context': context},
                metadata={'plan_id': fragment.parent_plan_id, 'fragment_id': fragment.fragment_id}
            )
            response = self.route_message(msg)
            results.append({'fragment_id': fragment.fragment_id, 'response': response})
        return results

    def orchestrate_distributed_plan(self, plan: dict, fragments: List[Any], context: dict = None) -> dict:
        """
        High-level orchestration for distributed plan execution.
        Logs all routing decisions and fragment results.
        """
        context = context or {}
        self._log_event('orchestrate_plan', 'router', None, 'distributed_plan', plan, {'plan_id': plan.get('plan_id')})
        fragment_results = self.route_plan_fragments(fragments, context)
        self._log_event('plan_execution_complete', 'router', None, 'distributed_plan', plan, {'plan_id': plan.get('plan_id'), 'fragment_results': fragment_results})
        return {'plan_id': plan.get('plan_id'), 'fragment_results': fragment_results}
    """
    Central orchestrator for agent collaboration.
    Handles agent registry, message routing, delegation, and workflow coordination.
    Designed for future parallel execution support.
    Tracks delegation decisions and task lineage for traceability.
    """
    def __init__(self):
        self._agents: Dict[str, Callable[[AgentMessage], AgentMessage]] = {}
        self._log: List[Dict] = []
        self._task_lineage: Dict[str, List[Dict]] = {}  # trace_id -> list of delegation hops

    def register_agent(self, agent_id: str, handler: Callable[[AgentMessage], AgentMessage]):
        self._agents[agent_id] = handler
        self._log_event('register', agent_id)

    def unregister_agent(self, agent_id: str):
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._log_event('unregister', agent_id)

    def route_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        self._log_event('route', message.sender, message.receiver, message.intent, message.payload, message.metadata)
        handler = self._agents.get(message.receiver)
        if handler:
            response = handler(message)
            self._log_event('response', message.receiver, message.sender, response.intent, response.payload, response.metadata)
            return response
        else:
            self._log_event('route_failed', message.sender, message.receiver, message.intent, message.payload, message.metadata)
            return None

    def delegate_task(self, from_agent: str, to_agent: str, intent: str, payload: dict, metadata: dict = None) -> Optional[AgentMessage]:
        msg = AgentMessage(sender=from_agent, receiver=to_agent, intent=intent, payload=payload, metadata=metadata or {})
        # Log delegation decision
        self._log_event('delegate', from_agent, to_agent, intent, payload, msg.metadata)
        # Track task lineage
        trace_id = msg.metadata.get('trace_id')
        if trace_id:
            hop = {
                'from': from_agent,
                'to': to_agent,
                'intent': intent,
                'payload': payload,
                'metadata': msg.metadata,
                'timestamp': time.time()
            }
            self._task_lineage.setdefault(trace_id, []).append(hop)
        return self.route_message(msg)

    def get_task_lineage(self, trace_id: str):
        return self._task_lineage.get(trace_id, [])

    def broadcast(self, from_agent: str, intent: str, payload: dict, metadata: dict = None) -> List[AgentMessage]:
        responses = []
        for agent_id in self._agents:
            if agent_id != from_agent:
                msg = AgentMessage(sender=from_agent, receiver=agent_id, intent=intent, payload=payload, metadata=metadata or {})
                resp = self.route_message(msg)
                if resp:
                    responses.append(resp)
        return responses

    def _log_event(self, action: str, sender: str = None, receiver: str = None, intent: str = None, payload: dict = None, metadata: dict = None):
        self._log.append({
            'timestamp': time.time(),
            'action': action,
            'sender': sender,
            'receiver': receiver,
            'intent': intent,
            'payload': payload,
            'metadata': metadata
        })

    def get_log(self) -> List[Dict]:
        return list(self._log)
