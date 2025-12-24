

# Persona styling is now part of the cognitive pipeline.

from src.persona_context import PersonaContext
from src.persona_styler import PersonaStyler
from src.persona_memory_engine import PersonaMemoryEngine

class CognitiveLoop:
	def __init__(self, router, mode_manager, memory, task_context, persona_context=None):
		self.router = router
		self.mode_manager = mode_manager
		self.memory = memory
		self.task_context = task_context
		self.persona_context = persona_context or PersonaContext()
		self.persona_styler = PersonaStyler(self.persona_context)
		self.persona_memory_engine = PersonaMemoryEngine(self.persona_context)

	def process_turn(self, user_message: str):
		# Wrap user_message in AgentMessage for router compatibility
		from src.agent_messaging import AgentMessage
		agent_msg = AgentMessage(
			sender="user",
			receiver="agent",
			intent="request",
			payload={"user_message": user_message},
			metadata={"persona_context": self.persona_context}
		)

		# Pre-adapt persona context based on user message (simulate anticipation)
		self.persona_memory_engine._adapt_to_user(user_message)
		print(f"[PersonaStyling] Applied style: {self.persona_context.voice_style}, tone: {self.persona_context.tone_modifiers}")

		# Route message and get internal reasoning and final output
		msg = self.router.route_message(agent_msg) if hasattr(self.router, 'route_message') else None
		styled_output = None
		internal_output = None
		metadata = {}
		if msg and hasattr(msg, 'payload') and isinstance(msg.payload, dict):
			styled_output = msg.payload.get('result', None)
			internal_output = msg.payload.get('internal', None)
			# Collect turn-level metadata for Web3 rendering
			metadata = {
				"mode": getattr(self.mode_manager, 'get_mode', lambda: None)(),
				"handler": msg.metadata.get('handler') if hasattr(msg, 'metadata') else None,
				"persona_shaping": getattr(self.persona_context, 'voice_style', None),
				"memory_updates": getattr(self.persona_context, 'persona_memory', None),
				"routing_trace": msg.metadata.get('routing_trace') if hasattr(msg, 'metadata') else None,
				"signature_required": msg.metadata.get('signature_required') if hasattr(msg, 'metadata') else False,
				"persona_state_update": msg.metadata.get('persona_state_update') if hasattr(msg, 'metadata') else False
			}
		# Update persona memory for both internal and external outputs
		if internal_output:
			self.persona_memory_engine.observe_and_update(internal_output, user_message)
		if styled_output:
			self.persona_memory_engine.observe_and_update(styled_output, user_message)
		# Return output and metadata for UI/Web3
		return {
			"display_text": styled_output,
			"reasoning_trace": internal_output,
			"metadata": metadata,
			"persona_state": self.persona_context
		}

