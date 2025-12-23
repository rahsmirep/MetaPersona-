"""
CritiqueLoop: Reusable framework for multi-agent critique and refinement cycles.
Supports multiple critique rounds, trace logging, and integration with Router/SharedMemory.
"""
from typing import Any, Dict, List, Callable, Optional
import time

class CritiqueLoop:
    def __init__(
        self,
        router,
        shared_memory,
        trace_key_prefix: str = "critique_loop",
    ):
        self.router = router
        self.shared_memory = shared_memory
        self.trace_key_prefix = trace_key_prefix

    def run(
        self,
        producer_agent: str,
        critique_agent: str,
        refine_agent: Optional[str],
        initial_input: Any,
        rounds: int = 1,
        context: Optional[Dict] = None,
        trace_id: Optional[str] = None,
        log: bool = True
    ) -> Dict[str, Any]:
        """
        Run a critique loop: produce → critique → refine, for N rounds.
        Returns dict with all intermediate and final outputs, plus trace log.
        """
        context = context or {}
        trace = []
        current_output = initial_input
        for round_num in range(1, rounds + 1):
            # 1. Producer agent generates output (if first round, use initial_input)
            if round_num == 1 and not context.get("producer_output"):
                producer_output = current_output
            else:
                producer_output = self._send_message(
                    sender=producer_agent,
                    receiver=producer_agent,
                    intent="produce",
                    payload={"input": current_output, **context},
                    trace_id=trace_id
                )
            # 2. Critique agent critiques the output
            critique = self._send_message(
                sender=producer_agent,
                receiver=critique_agent,
                intent="critique_request",
                payload={"output": producer_output, **context},
                trace_id=trace_id
            )
            # 3. Refine agent (or producer) refines the output based on critique
            refine_target = refine_agent or producer_agent
            refined = self._send_message(
                sender=critique_agent,
                receiver=refine_target,
                intent="refine",
                payload={"output": producer_output, "critique": critique, **context},
                trace_id=trace_id
            )
            # Log this round
            round_log = {
                "round": round_num,
                "producer_agent": producer_agent,
                "critique_agent": critique_agent,
                "refine_agent": refine_target,
                "producer_output": producer_output,
                "critique": critique,
                "refined": refined,
                "timestamp": time.time(),
                "trace_id": trace_id,
                "context": context
            }
            trace.append(round_log)
            if log:
                self.shared_memory.write(
                    f"{self.trace_key_prefix}:{trace_id or 'noid'}:round{round_num}",
                    round_log,
                    author=producer_agent,
                    metadata={"critique_round": round_num, "trace_id": trace_id, "agents": [producer_agent, critique_agent, refine_target]}
                )
            current_output = refined
        # Store full trace
        if log:
            self.shared_memory.write(
                f"{self.trace_key_prefix}:{trace_id or 'noid'}:full_trace",
                trace,
                author=producer_agent,
                metadata={"trace_id": trace_id, "agents": [producer_agent, critique_agent, refine_target], "rounds": rounds}
            )
        return {
            "final_output": current_output,
            "trace": trace
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
            # Try to extract main output
            return response.payload.get("output") or response.payload.get("refined") or response.payload.get("critique") or response.payload.get("result") or response.payload.get("final_output") or response.payload
        return None
