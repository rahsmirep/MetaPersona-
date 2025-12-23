"""
ConsensusEngine: Merges outputs from multiple agents using configurable strategies.
Supports majority agreement, weighted scoring, critique-driven refinement, and best-candidate selection.
Logs all consensus actions to SharedMemory.
"""
from typing import List, Dict, Any, Callable, Optional
import time

class ConsensusEngine:
    def __init__(self, shared_memory, trace_key_prefix: str = "consensus"):
        self.shared_memory = shared_memory
        self.trace_key_prefix = trace_key_prefix

    def merge(
        self,
        agent_outputs: List[Dict[str, Any]],
        strategy: str = "majority",
        weights: Optional[Dict[str, float]] = None,
        critiques: Optional[List[Dict[str, Any]]] = None,
        trace_id: Optional[str] = None,
        log: bool = True
    ) -> Dict[str, Any]:
        """
        Merge outputs from multiple agents using the selected strategy.
        Returns dict with consensus output, all inputs, and trace log.
        """
        trace = {
            "strategy": strategy,
            "inputs": agent_outputs,
            "critiques": critiques,
            "weights": weights,
            "trace_id": trace_id,
            "timestamp": time.time(),
            "agents": [o.get('agent') for o in agent_outputs if isinstance(o, dict)],
        }
        if strategy == "majority":
            consensus = self._majority_vote(agent_outputs)
        elif strategy == "weighted":
            consensus = self._weighted_score(agent_outputs, weights)
        elif strategy == "critique_refine":
            consensus = self._critique_driven_refine(agent_outputs, critiques)
        elif strategy == "best_candidate":
            consensus = self._best_candidate(agent_outputs, critiques)
        else:
            consensus = agent_outputs[0] if agent_outputs else None
        trace["consensus"] = consensus
        if log:
            self.shared_memory.write(
                f"{self.trace_key_prefix}:{trace_id or 'noid'}:consensus",
                trace,
                author="consensus_engine",
                metadata={"strategy": strategy, "trace_id": trace_id, "agents": trace.get('agents')}
            )
        return {
            "consensus": consensus,
            "trace": trace
        }

    def _majority_vote(self, agent_outputs: List[Dict[str, Any]]):
        from collections import Counter
        outputs = [o.get("output") or o for o in agent_outputs]
        most_common, _ = Counter(outputs).most_common(1)[0]
        return most_common

    def _weighted_score(self, agent_outputs: List[Dict[str, Any]], weights: Optional[Dict[str, float]]):
        if not weights:
            return self._majority_vote(agent_outputs)
        score_map = {}
        for o in agent_outputs:
            agent = o.get("agent")
            val = o.get("output") or o
            score_map[val] = score_map.get(val, 0) + weights.get(agent, 1.0)
        return max(score_map, key=score_map.get)

    def _critique_driven_refine(self, agent_outputs: List[Dict[str, Any]], critiques: Optional[List[Dict[str, Any]]]):
        # Pick output with best critique score, or merge critiques
        if not critiques:
            return self._majority_vote(agent_outputs)
        scored = [(o.get("output") or o, c.get("score", 0)) for o, c in zip(agent_outputs, critiques)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[0][0]

    def _best_candidate(self, agent_outputs: List[Dict[str, Any]], critiques: Optional[List[Dict[str, Any]]]):
        # Select output with highest overall score or best review
        if not critiques:
            return self._majority_vote(agent_outputs)
        best_idx = 0
        best_score = float('-inf')
        for idx, c in enumerate(critiques):
            score = c.get("score", 0)
            if score > best_score:
                best_score = score
                best_idx = idx
        return agent_outputs[best_idx].get("output") or agent_outputs[best_idx]
