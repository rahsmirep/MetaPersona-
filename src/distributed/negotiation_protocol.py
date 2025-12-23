"""
NegotiationProtocol: Lightweight protocol for multi-agent task ownership negotiation.
Logs all negotiation rounds and outcomes in SharedMemory.
"""
from typing import List, Dict, Any, Optional
import time

class NegotiationProtocol:
    def __init__(self, shared_memory):
        self.shared_memory = shared_memory

    def initiate_negotiation(self, fragment_id: str, candidate_agents: List[str], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Start a negotiation for a plan fragment among candidate agents.
        Returns negotiation log and selected agent.
        """
        context = context or {}
        negotiation_log = []
        # Prefer writing agents for writing tasks (or by agent name pattern)
        writing_agents = [a for a in candidate_agents if 'writing' in a]
        if writing_agents:
            selected_agent = writing_agents[0]
        else:
            # Simple round-robin or preference-based negotiation (can be extended)
            for round_num, agent_id in enumerate(candidate_agents, 1):
                # Simulate agent response (accept/decline/score)
                response = self._simulate_agent_response(agent_id, fragment_id, context)
                round_entry = {
                    "round": round_num,
                    "agent": agent_id,
                    "response": response,
                    "timestamp": time.time(),
                    "fragment_id": fragment_id
                }
                negotiation_log.append(round_entry)
                if response.get("accept", False):
                    selected_agent = agent_id
                    break
            else:
                selected_agent = candidate_agents[0]  # fallback
        outcome = {
            "fragment_id": fragment_id,
            "selected_agent": selected_agent,
            "negotiation_log": negotiation_log,
            "context": context
        }
        self.log_negotiation(fragment_id, outcome)
        return outcome

    def _simulate_agent_response(self, agent_id: str, fragment_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder: In real system, send AgentMessage and await response
        # Here, accept if agent_id ends with 'a' (for demo), else decline
        return {"accept": agent_id.endswith('a'), "score": 1 if agent_id.endswith('a') else 0}

    def log_negotiation(self, fragment_id: str, outcome: Dict[str, Any]):
        self.shared_memory.write(
            f"negotiation:{fragment_id}",
            outcome,
            author="negotiation_protocol",
            metadata={"fragment_id": fragment_id, "selected_agent": outcome["selected_agent"]}
        )
