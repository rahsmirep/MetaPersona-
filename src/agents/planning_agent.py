from src.agent_messaging import AgentMessagingProtocol, AgentMessage
from src.shared_memory import SharedBlackboard
from src.router import Router
from src.profession.workflow_engine import WorkflowEngine
from src.delegation.classifier import TaskClassifier
from src.delegation.rules_engine import DelegationRulesEngine
from src.delegation.confidence import DelegationConfidence
from typing import Dict, Any
import time

class PlanningAgent(AgentMessagingProtocol):
    def generate_plan_steps(self, user_request: str, context: Dict[str, Any] = None) -> Any:
        """
        Generate a multi-step plan (list of steps) for a user request, suitable for fragmentation.
        """
        context = context or {}
        if self.workflow_engine:
            steps = self.workflow_engine.plan_generation(user_request)
        else:
            steps = [f"Step 1 for {user_request}", f"Step 2 for {user_request}"]
        # Optionally classify and annotate each step
        classified_steps = []
        for step in steps:
            task_type, clf_conf = self.classifier.classify_task(step)
            classified_steps.append({
                "step": step,
                "task_type": task_type,
                "confidence": clf_conf
            })
        return [s["step"] for s in classified_steps]

    def __init__(self, agent_id: str, router: Router, shared_memory: SharedBlackboard, llm_provider=None):
        self.agent_id = agent_id
        self.router = router
        self.shared_memory = shared_memory
        self.llm_provider = llm_provider
        self.workflow_engine = WorkflowEngine(self, llm_provider) if llm_provider else None
        self.trace_log = []
        self.classifier = TaskClassifier()
        self.rules_engine = DelegationRulesEngine(
            agent_map={
                'planning': self.agent_id,
                'writing': 'writing_agent',
                'research': 'research_agent',
                'critique': 'critique_agent',
                'alignment': 'persona_alignment_agent',
            },
            fallback_agent=self.agent_id
        )
        self.router.register_agent(self.agent_id, self.handle_message)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        self._log_action('received', message)
        # Classify the task type
        task_type, clf_conf = self.classifier.classify_task(message.intent)
        confidence_level, confidence_score = DelegationConfidence.estimate_confidence('planning', task_type)
        # Determine which agent should handle this
        target_agent, rule_info = self.rules_engine.get_agent_for_task(task_type, context=message.metadata)
        # If this agent is the best fit, handle locally
        if target_agent == self.agent_id and confidence_level != 'low':
            if message.intent in ['planning_request', 'request']:
                task = message.payload.get('task')
                plan = self._generate_plan(task)
                # Write plan to shared memory
                self.shared_memory.write(f"plan:{task}", plan, self.agent_id, metadata={"source_agent": self.agent_id})
                response = AgentMessage(
                    sender=self.agent_id,
                    receiver=message.sender,
                    intent='planning_response',
                    payload={'plan': plan},
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

    def _generate_plan(self, task: str) -> Any:
        # Use WorkflowEngine or mock to generate a plan
        if self.workflow_engine:
            return self.workflow_engine.plan_generation(task)
        return [f"Step 1 for {task}", f"Step 2 for {task}"]
        self.trace_log.append({'action': action, 'message': message, 'timestamp': time.time()})
