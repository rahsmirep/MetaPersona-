
from src.agent_messaging import AgentMessagingProtocol, AgentMessage
from src.shared_memory import SharedBlackboard
from src.router import Router
from src.delegation.classifier import TaskClassifier
from src.delegation.rules_engine import DelegationRulesEngine
from src.delegation.confidence import DelegationConfidence
from typing import Dict, Any
import time

class ResearchAgent(AgentMessagingProtocol):
    def __init__(self, agent_id: str, router: Router, shared_memory: SharedBlackboard, llm_provider=None, rules_engine: DelegationRulesEngine = None):
        self.agent_id = agent_id
        self.router = router
        self.shared_memory = shared_memory
        self.llm_provider = llm_provider  # Can be a mock LLM or real web agent
        self.rules_engine = rules_engine
        self.trace_log = []
        self.router.register_agent(self.agent_id, self.handle_message)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        self._log_action('received', message)
        # Classify the task
        task_text = message.payload.get('query') or message.payload.get('user_request') or ''
        task_type, classifier_conf = TaskClassifier.classify_task(task_text)
        # Estimate confidence
        confidence_level, confidence_score = DelegationConfidence.estimate_confidence('research', task_type)
        # Read context from shared memory (if any)
        context_key = message.payload.get('context_key')
        context_data = self.shared_memory.read(context_key) if context_key else None
        # Delegation logic
        if confidence_level == 'low' and self.rules_engine:
            # Delegate to best-fit agent
            agent_id, rule_info = self.rules_engine.get_agent_for_task(task_type)
            if agent_id and agent_id != self.agent_id:
                self._log_action('delegating', message)
                # Write trace to shared memory
                self.shared_memory.write(f"delegation:{message.metadata.get('trace_id')}", {
                    'from': self.agent_id,
                    'to': agent_id,
                    'task_type': task_type,
                    'reason': 'low confidence',
                    'context': context_data
                }, self.agent_id)
                return self.router.delegate_task(
                    from_agent=self.agent_id,
                    to_agent=agent_id,
                    intent=message.intent,
                    payload=message.payload,
                    metadata=message.metadata
                )
        # Otherwise, handle internally
        if message.intent == 'research_request' or message.intent == 'request':
            query = message.payload.get('query') or message.payload.get('user_request')
            steps = message.payload.get('steps', [query])
            results = []
            for step in steps:
                result = self._perform_research(step)
                results.append(result)
                # Write each result to shared memory
                self.shared_memory.write(f"research:{step}", result, self.agent_id, metadata={"source_agent": self.agent_id})
            response = AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                intent='research_response',
                payload={'results': results, 'handled_by': self.agent_id, 'confidence': confidence_level, 'task_type': task_type},
                metadata={'in_response_to': message.metadata.get('trace_id'), 'timestamp': time.time()}
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

    def _perform_research(self, query: str) -> Dict[str, Any]:
        # Simulate research using LLM or mock
        if self.llm_provider:
            result = self.llm_provider.generate([{"role": "user", "content": query}], temperature=0.2)
        else:
            result = f"Mock research result for: {query}"
        return {'query': query, 'result': result, 'agent': self.agent_id, 'timestamp': time.time()}

    def _log_action(self, action: str, message: AgentMessage):
        self.trace_log.append({'action': action, 'message': message, 'timestamp': time.time()})
