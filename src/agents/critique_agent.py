from src.agent_messaging import AgentMessagingProtocol, AgentMessage
from src.shared_memory import SharedBlackboard
from src.router import Router
from src.profession.reflection_engine import ReflectionEngine
from src.delegation.classifier import TaskClassifier
from src.delegation.rules_engine import DelegationRulesEngine
from src.delegation.confidence import DelegationConfidence
from typing import Dict, Any
import time

class CritiqueAgent(AgentMessagingProtocol):
    def __init__(self, agent_id: str, router: Router, shared_memory: SharedBlackboard, llm_provider=None):
        self.agent_id = agent_id
        self.router = router
        self.shared_memory = shared_memory
        self.llm_provider = llm_provider
        self.reflection = ReflectionEngine(llm_provider) if llm_provider else None
        self.trace_log = []
        self.classifier = TaskClassifier()
        self.rules_engine = DelegationRulesEngine(
            agent_map={
                'critique': self.agent_id,
                'writing': 'writing_agent',
                'planning': 'planning_agent',
                'research': 'research_agent',
                'alignment': 'persona_alignment_agent',
            },
            fallback_agent=self.agent_id
        )
        self.router.register_agent(self.agent_id, self.handle_message)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        self._log_action('received', message)
        # Classify the task type
        task_type, clf_conf = self.classifier.classify_task(message.intent)
        confidence_level, confidence_score = DelegationConfidence.estimate_confidence('critique', task_type)
        # Determine which agent should handle this
        target_agent, rule_info = self.rules_engine.get_agent_for_task(task_type, context=message.metadata)
        # If this agent is the best fit, handle locally
        if target_agent == self.agent_id and confidence_level != 'low':
            if message.intent in ['critique_request', 'request']:
                output = message.payload.get('output')
                critique = self._critique_output(output)
                # Write critique to shared memory
                self.shared_memory.write(f"critique:{hash(output)}", critique, self.agent_id, metadata={"source_agent": self.agent_id})
                response = AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    intent='critique_response',
                    payload={'critique': critique},
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

    def _critique_output(self, output: Any) -> Dict[str, Any]:
        # Use ReflectionEngine or mock to critique output
        if self.reflection:
            eval_result = self.reflection.evaluate_response(output, None)
            return {
                'clarity': eval_result.get('clarity', 0),
                'accuracy': eval_result.get('accuracy', 0),
                'alignment': eval_result.get('alignment', 0),
                'completeness': eval_result.get('completeness', 0),
                'needs_refinement': eval_result.get('needs_refinement', False),
                'raw': eval_result
            }
        # Mock critique
        return {
            'clarity': 4,
            'accuracy': 4,
            'alignment': 4,
            'completeness': 4,
            'needs_refinement': False,
            'raw': 'Mock critique'
        }

    def _log_action(self, action: str, message: AgentMessage):
        self.trace_log.append({'action': action, 'message': message, 'timestamp': time.time()})
