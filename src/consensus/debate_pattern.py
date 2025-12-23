"""
DebatePattern: Orchestrates multi-agent debates, tracks argument exchanges, and logs debate states.
Router coordinates debate turns; SharedMemory stores debate history and state.
"""
from typing import List, Dict, Any, Optional
import time

class DebatePattern:
    def __init__(self, router, shared_memory, trace_key_prefix: str = "debate"):
        self.router = router
        self.shared_memory = shared_memory
        self.trace_key_prefix = trace_key_prefix

    def run(
        self,
        agent_ids: List[str],
        topic: str,
        rounds: int = 2,
        context: Optional[Dict] = None,
        trace_id: Optional[str] = None,
        log: bool = True
    ) -> Dict[str, Any]:
        """
        Run a debate among agents on a topic for N rounds.
        Returns dict with all arguments, debate trace, and final state.
        """
        context = context or {}
        debate_trace = []
        current_state = {"topic": topic, "arguments": []}
        for round_num in range(1, rounds + 1):
            for agent_id in agent_ids:
                # Each agent presents or rebuts
                argument = self._send_message(
                    sender="debate_orchestrator",
                    receiver=agent_id,
                    intent="debate_turn",
                    payload={"topic": topic, "state": current_state, **context},
                    trace_id=trace_id
                )
                arg_log = {
                    "agent": agent_id,
                    "argument": argument,
                    "round": round_num,
                    "topic": topic,
                    "timestamp": time.time(),
                    "trace_id": trace_id,
                    "context": context
                }
                current_state["arguments"].append(arg_log)
                if log:
                    self.shared_memory.write(
                        f"{self.trace_key_prefix}:{trace_id or 'noid'}:round{round_num}:{agent_id}",
                        arg_log,
                        author=agent_id,
                        metadata={"debate_round": round_num, "trace_id": trace_id, "topic": topic}
                    )
            # Optionally, allow agents to see all arguments so far in next round
        if log:
            self.shared_memory.write(
                f"{self.trace_key_prefix}:{trace_id or 'noid'}:full_trace",
                current_state,
                author="debate_orchestrator",
                metadata={"trace_id": trace_id, "agent_ids": agent_ids, "topic": topic, "rounds": rounds}
            )
        return {
            "final_state": current_state,
            "trace": current_state["arguments"]
        }

    def _send_message(self, sender, receiver, intent, payload, trace_id=None):
        from src.agent_messaging import AgentMessage
        msg = AgentMessage(
            sender=sender,
            receiver=receiver,
            intent=intent,
            payload=payload,
            metadata={"trace_id": trace_id} if trace_id else {}
        )
        response = self.router.route_message(msg)
        if response and response.payload:
            return response.payload.get("argument") or response.payload.get("output") or response.payload.get("result") or response.payload
        return None
