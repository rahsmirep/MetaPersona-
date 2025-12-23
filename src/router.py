

from typing import Dict, Callable, Optional, List, Any
from src.agent_messaging import AgentMessage
import time
from src.mode_manager import ModeManager
from src.short_term_memory import ShortTermMemory
from src.task_context import TaskContext

class Router:
    def __init__(self, mode_manager: ModeManager = None, memory: ShortTermMemory = None, task_context: TaskContext = None):
        self._agents: Dict[str, Callable[[AgentMessage], AgentMessage]] = {}
        self._log: List[Dict] = []
        self._task_lineage: Dict[str, List[Dict]] = {}  # trace_id -> list of delegation hops
        self.mode_manager = mode_manager or ModeManager()
        self.memory = memory or ShortTermMemory()
        self.task_context = task_context or TaskContext()
    def log_routing_trace(self, message, handler_name=None, reason=None, fallback_triggered=False, override_triggered=False, prev_mode=None, new_mode=None, mode_reason=None):
        """
        Structured diagnostic logging for routing trace.
        Prints:
            - Raw user message
            - Classifier's predicted intent
            - Confidence score/signal (if available)
            - Handler selected
            - Reason for handler selection
            - Fallback/override logic
        """
        print("\n[ROUTING TRACE INSPECTOR]")
        # Raw user message
        user_msg = getattr(message, 'payload', {}).get('user_message') or getattr(message, 'payload', {}).get('text') or str(getattr(message, 'payload', {}))
        print(f"  Raw user message: {user_msg}")
        # Classifier prediction and confidence
        intent = getattr(message, 'metadata', {}).get('predicted_intent') or getattr(message, 'intent', None)
        confidence = getattr(message, 'metadata', {}).get('confidence') or getattr(message, 'metadata', {}).get('score')
        print(f"  Predicted intent: {intent}")
        print(f"  Confidence/score: {confidence}")
        # Handler selected
        print(f"  Handler selected: {handler_name}")
        print(f"  Reason: {reason}")
        print(f"  Fallback triggered: {fallback_triggered}")
        print(f"  Override triggered: {override_triggered}")
        if prev_mode is not None or new_mode is not None:
            print(f"  Previous mode: {prev_mode}")
            print(f"  New mode: {new_mode}")
            print(f"  Mode transition reason: {mode_reason}")
        print("[END ROUTING TRACE INSPECTOR]\n")

        # Log memory snapshot
        print("[MEMORY SNAPSHOT]")
        mem = self.memory.snapshot()
        for k, v in mem.items():
            print(f"  {k}: {v}")
        print("[END MEMORY SNAPSHOT]\n")
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
    # Removed duplicate __init__ (see above)

    def register_agent(self, agent_id: str, handler: Callable[[AgentMessage], AgentMessage]):
        self._agents[agent_id] = handler
        self._log_event('register', agent_id)

    def unregister_agent(self, agent_id: str):
        if agent_id in self._agents:
            del self._agents[agent_id]
            self._log_event('unregister', agent_id)

    def route_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        self._log_event('route', message.sender, message.receiver, message.intent, message.payload, message.metadata)

        # --- Unified cognitive decision pipeline ---
        metadata = getattr(message, 'metadata', {}) or {}
        predicted_intent = metadata.get('predicted_intent') or getattr(message, 'intent', None)
        confidence = metadata.get('confidence') or metadata.get('score')
        user_msg = getattr(message, 'payload', {}).get('user_message') or getattr(message, 'payload', {}).get('text') or ''
        user_msg_lower = user_msg.lower() if isinstance(user_msg, str) else ''

        # ABSOLUTE FIRST USER TURN: always use onboarding handler and return immediately
        if len(self._log) == 0:
            print("[ROUTER DEBUG] ABSOLUTE FIRST TURN: onboarding handler forced and returned immediately.")
            handler = self._agents.get('agent_onboarding')
            handler_name = handler.__name__ if handler else None
            reason = 'ABSOLUTE FIRST TURN: onboarding handler forced.'
            if handler:
                return handler(message)
            else:
                return None

        # Compose classifier_result for mode manager
        classifier_result = {
            'predicted_intent': predicted_intent,
            'confidence': confidence,
            'signals': metadata.get('signals', {}),
        }
        prev_mode = self.mode_manager.get_mode() if self.mode_manager else None
        # Centralized, context-aware mode update
        new_mode, mode_reason = self.mode_manager.update_mode(classifier_result, prev_mode, message_context=message.payload)

        # --- Update short-term memory ---
        self.memory.add_user_message({'message': user_msg, 'metadata': metadata})
        self.memory.add_classifier_output(classifier_result)
        self.memory.add_mode_transition(prev_mode, new_mode, mode_reason)

        print(f"[ROUTER DEBUG] prev_mode={prev_mode}, new_mode={new_mode}, mode_reason={mode_reason}")
        # Handler selection logic (mode-driven, context-aware)
        handler = None
        handler_name = None
        reason = None
        fallback_triggered = False
        override_triggered = False

        # Heuristic: if user_msg looks like a task, force mode to 'task-execution' and use task handler
        if any(word in user_msg_lower for word in ["task", "do", "help"]):
            print("[ROUTER DEBUG] Heuristic: user_msg looks like a task, forcing mode to 'task-execution' and using agent_task handler.")
            new_mode = 'task-execution'
            handler = self._agents.get('agent_task')
            handler_name = handler.__name__ if handler else None
            reason = 'Heuristic: user_msg looks like a task.'
        elif new_mode == 'task-execution':
            print("[ROUTER DEBUG] Looking for handler: agent_task")
            handler = self._agents.get('agent_task')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for task-execution mode.'
        elif new_mode == 'greeting' or new_mode == 'onboarding':
            print("[ROUTER DEBUG] Using handler: agent_onboarding (for greeting/onboarding mode)")
            handler = self._agents.get('agent_onboarding')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for onboarding/greeting mode.'
        elif new_mode == 'reflection':
            print("[ROUTER DEBUG] Looking for handler: agent_reflection")
            handler = self._agents.get('agent_reflection')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for reflection mode.'
        elif new_mode == 'error-recovery':
            print("[ROUTER DEBUG] Looking for handler: agent_error_recovery")
            handler = self._agents.get('agent_error_recovery')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for error-recovery mode.'
        else:
            print("[ROUTER DEBUG] Looking for handler: agent_fallback")
            handler = self._agents.get('agent_fallback')
            handler_name = handler.__name__ if handler else None
            reason = 'Fallback handler selected: unknown or ambiguous mode.'
            fallback_triggered = True

        # (Removed duplicate ABSOLUTE FIRST USER TURN blocks)
        if new_mode == 'task-execution':
            print("[ROUTER DEBUG] Looking for handler: agent_task")
            handler = self._agents.get('agent_task')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for task-execution mode.'
        elif new_mode == 'greeting':
            print("[ROUTER DEBUG] Looking for handler: agent_greeter")
            handler = self._agents.get('agent_greeter')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for greeting mode.'
        elif new_mode == 'onboarding':
            print("[ROUTER DEBUG] Looking for handler: agent_onboarding")
            handler = self._agents.get('agent_onboarding')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for onboarding mode.'
        elif new_mode == 'reflection':
            print("[ROUTER DEBUG] Looking for handler: agent_reflection")
            handler = self._agents.get('agent_reflection')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for reflection mode.'
        elif new_mode == 'error-recovery':
            print("[ROUTER DEBUG] Looking for handler: agent_error_recovery")
            handler = self._agents.get('agent_error_recovery')
            handler_name = handler.__name__ if handler else None
            reason = 'Handler selected for error-recovery mode.'
        else:
            print("[ROUTER DEBUG] Looking for handler: agent_fallback")
            handler = self._agents.get('agent_fallback')
            handler_name = handler.__name__ if handler else None
            reason = 'Fallback handler selected: unknown or ambiguous mode.'
            fallback_triggered = True

        print(f"[ROUTER DEBUG] Handler found: {handler_name}")

        # Always return a valid AgentMessage with persona-styled output
        from src.agent_messaging import AgentMessage
        if handler:
            try:
                result = handler(message)
                if isinstance(result, AgentMessage):
                    return result
                # If handler returns a string or dict, wrap it
                return AgentMessage(
                    sender="agent",
                    receiver=message.sender,
                    intent="response",
                    payload={"result": result},
                    metadata={}
                )
            except Exception as e:
                return AgentMessage(
                    sender="agent",
                    receiver=message.sender,
                    intent="response",
                    payload={"result": f"[Error] {str(e)}"},
                    metadata={}
                )
        else:
            # Fallback: always return a persona-styled message
            return AgentMessage(
                sender="agent",
                receiver=message.sender,
                intent="response",
                payload={"result": "[MetaPersona] I'm here, but I couldn't find a suitable handler for your request. (Fallback response)"},
                metadata={}
            )
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
