
from src.cognitive_loop import CognitiveLoop
from src.mode_manager import ModeManager
from src.router import Router
from src.short_term_memory import ShortTermMemory
from src.task_context import TaskContext


from src.persona_context import PersonaContext
from src.persona_styler import PersonaStyler

class SingleUseAgent:
    def __init__(self, agent_id, initial_mode='greeting', persona_context=None):
        from src.planning_handlers import handler_task, handler_reflection, handler_error_recovery, handler_onboarding
        def persona_handler(handler_func, mode):
            def wrapped(msg):
                # Inject persona context into handler
                msg.metadata = dict(msg.metadata) if hasattr(msg, 'metadata') else {}
                msg.metadata['persona_context'] = self.persona_context
                raw = handler_func(msg)
                # Only style if not already styled (avoid double-styling)
                result = raw.payload['result']
                if isinstance(result, str) and result.startswith("[") and "]" in result.split(" ")[0]:
                    # Already styled, do not restyle
                    pass
                else:
                    styled = self.persona_styler.style(result, mode=mode)
                    raw.payload['result'] = styled
                return raw
            return wrapped
        self.agent_id = agent_id
        self.mode_manager = ModeManager(initial_mode=initial_mode)
        self.memory = ShortTermMemory()
        self.task_context = TaskContext()
        self.persona_context = persona_context or PersonaContext()
        self.persona_styler = PersonaStyler(self.persona_context)
        self.router = Router(mode_manager=self.mode_manager, memory=self.memory, task_context=self.task_context)
        # Register persona-aware handlers
        self.router.register_agent('agent_task', persona_handler(handler_task, 'task'))
        self.router.register_agent('agent_reflection', persona_handler(handler_reflection, 'reflection'))
        self.router.register_agent('agent_error_recovery', persona_handler(handler_error_recovery, 'recovery'))
        self.router.register_agent('agent_onboarding', persona_handler(handler_onboarding, 'onboarding'))
        self.router.register_agent('agent_greeter', persona_handler(handler_reflection, 'greeting'))
        self.router.register_agent('agent_fallback', persona_handler(handler_reflection, 'fallback'))
        self.cognitive_loop = CognitiveLoop(self.router, self.mode_manager, self.memory, self.task_context, persona_context=self.persona_context)

    def process_turn(self, user_message: str):
        # Optionally evolve persona context based on memory or feedback
        # (stub: could use self.memory or external feedback)
        # Return the full AgentMessage object for test access
        msg = self.cognitive_loop.router.route_message(
            __import__('src.agent_messaging').agent_messaging.AgentMessage(
                sender="user",
                receiver="agent",
                intent="request",
                payload={"user_message": user_message},
                metadata={"persona_context": self.persona_context}
            )
        )
        # Still run the persona pipeline and memory update
        styled_output = None
        internal_output = None
        if msg and hasattr(msg, 'payload') and isinstance(msg.payload, dict):
            styled_output = msg.payload.get('result', None)
            internal_output = msg.payload.get('internal', None)
        if internal_output:
            self.cognitive_loop.persona_memory_engine.observe_and_update(internal_output, user_message)
        if styled_output:
            self.cognitive_loop.persona_memory_engine.observe_and_update(styled_output, user_message)
        return msg

    def get_mode(self):
        return self.mode_manager.get_mode()

    def get_mode_log(self):
        return self.mode_manager.get_log()
