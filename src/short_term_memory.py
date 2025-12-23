from collections import deque
from typing import Any, Dict, List, Optional

class ShortTermMemory:
    def __init__(self, max_user_msgs: int = 10, max_agent_responses: int = 10, max_classifier: int = 10, max_modes: int = 10):
        self.user_messages = deque(maxlen=max_user_msgs)
        self.agent_responses = deque(maxlen=max_agent_responses)
        self.classifier_outputs = deque(maxlen=max_classifier)
        self.mode_transitions = deque(maxlen=max_modes)

    def add_user_message(self, msg: Dict[str, Any]):
        self.user_messages.append(msg)

    def add_agent_response(self, resp: Dict[str, Any]):
        self.agent_responses.append(resp)

    def add_classifier_output(self, output: Dict[str, Any]):
        self.classifier_outputs.append(output)

    def add_mode_transition(self, prev_mode: str, new_mode: str, reason: str):
        self.mode_transitions.append({'prev_mode': prev_mode, 'new_mode': new_mode, 'reason': reason})

    def clear(self):
        self.user_messages.clear()
        self.agent_responses.clear()
        self.classifier_outputs.clear()
        self.mode_transitions.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            'user_messages': list(self.user_messages),
            'agent_responses': list(self.agent_responses),
            'classifier_outputs': list(self.classifier_outputs),
            'mode_transitions': list(self.mode_transitions)
        }
