from dataclasses import dataclass, field
from typing import Any, Dict
import time

@dataclass
class AgentMessage:
    sender: str
    receiver: str
    intent: str  # e.g., 'request', 'response', 'delegate', 'status_update'
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Ensure traceability: add timestamp and trace_id if not present
        if 'timestamp' not in self.metadata:
            self.metadata['timestamp'] = time.time()
        if 'trace_id' not in self.metadata:
            self.metadata['trace_id'] = f"{self.sender}->{self.receiver}:{int(self.metadata['timestamp']*1000)}"

class AgentMessagingProtocol:
    """
    Base protocol for agent-to-agent messaging. Agents should implement handle_message.
    """
    def handle_message(self, message: AgentMessage) -> AgentMessage:
        """
        Process an incoming message and return a response message if needed.
        """
        raise NotImplementedError("Agents must implement handle_message.")
