from src.agent_messaging import AgentMessagingProtocol, AgentMessage
from src.shared_memory import SharedBlackboard
from src.router import Router
from src.profession.reasoning import ParallelSelfAlignment
from src.delegation.classifier import TaskClassifier
from src.delegation.rules_engine import DelegationRulesEngine
from src.delegation.confidence import DelegationConfidence
from typing import Dict, Any
import time

class PersonaAlignmentAgent(AgentMessagingProtocol):
    def __init__(self, agent_id: str, router: Router, shared_memory: SharedBlackboard, cognitive_profile=None, llm_provider=None):
        self.agent_id = agent_id
        self.router = router
        self.shared_memory = shared_memory
        self.cognitive_profile = cognitive_profile
        self.llm_provider = llm_provider
        self.alignment = ParallelSelfAlignment()
        self.trace_log = []
        self.classifier = TaskClassifier()
        self.rules_engine = DelegationRulesEngine(
            agent_map={
                'alignment': self.agent_id,
                'writing': 'writing_agent',
                'planning': 'planning_agent',
                'research': 'research_agent',
                'critique': 'critique_agent',
            },
            fallback_agent=self.agent_id
        )
        self.router.register_agent(self.agent_id, self.handle_message)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        self._log_action('received', message)
        # Classify the task type
        task_type, clf_conf = self.classifier.classify_task(message.intent)
        confidence_level, confidence_score = DelegationConfidence.estimate_confidence('alignment', task_type)
        # Determine which agent should handle this
        target_agent, rule_info = self.rules_engine.get_agent_for_task(task_type, context=message.metadata)
        # If this agent is the best fit, handle locally
        if target_agent == self.agent_id and confidence_level != 'low':
            if message.intent in ['alignment_request', 'request']:
                output = message.payload.get('output')
                persona_consistent = self._align_output(output)
                # Write aligned output to shared memory
                self.shared_memory.write(f"aligned:{hash(output)}", persona_consistent, self.agent_id, metadata={"source_agent": self.agent_id})
                response = AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    intent='alignment_response',
                    payload={'aligned_output': persona_consistent},
                    metadata={
                        'in_response_to': message.metadata.get('trace_id'),
                        'timestamp': time.time(),
                        'delegation': {
                            'task_type': task_type,
                            'confidence': confidence_score,
                            'rule': rule_info.get('rule')
                        }
                    }
                )
                self._log_action('responded', response)
                return response
            else:
                response = AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    intent='error',
                    payload={'error': f'Unknown intent: {message.intent}'},
                    metadata={'in_response_to': message.metadata.get('trace_id'), 'timestamp': time.time()}
                )
                self._log_action('error', response)
                return response
        else:
            # Delegate to the appropriate agent via the router
            delegation_msg = AgentMessage(
                sender=self.agent_id,
                receiver=target_agent,
                intent=message.intent,
                payload=message.payload,
                metadata={
                    **message.metadata,
                    'delegated_by': self.agent_id,
                    'delegation': {
                        'task_type': task_type,
                        'confidence': confidence_score,
                        'rule': rule_info.get('rule')
                    },
                    'timestamp': time.time()
                }
            )
            self._log_action('delegated', delegation_msg)
            response = self.router.send_message(delegation_msg)
            self._log_action('delegation_response', response)
            return response

    def _align_output(self, output: Any) -> str:
        # Use alignment logic or mock
        if self.cognitive_profile:
            # Simulate alignment (real logic would use self.alignment.create_aligned_persona)
            return f"[Persona-aligned for {self.cognitive_profile.user_id}] {output}"
        return f"[Persona-aligned] {output}"

    def _log_action(self, action: str, message: AgentMessage):
        self.trace_log.append({'action': action, 'message': message, 'timestamp': time.time()})
