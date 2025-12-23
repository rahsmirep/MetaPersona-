from typing import Dict, Any, List

class StabilityMonitor:
    def __init__(self):
        self.mode_history: List[str] = []
        self.uncertainty_history: List[float] = []
        self.contradiction_count = 0
        self.error_recovery_count = 0
        self.stability_score = 1.0
        self.memory_overload = False
        self.stability_events: List[Dict[str, Any]] = []

    def check_stability(self, mode: str, meta_signals: Dict[str, Any], memory_snapshot: Dict[str, Any]):
        event = {}
        # Track mode history
        self.mode_history.append(mode)
        if len(self.mode_history) > 10:
            self.mode_history.pop(0)
        # Detect runaway loops (oscillation)
        if len(self.mode_history) >= 4 and len(set(self.mode_history[-4:])) > 2:
            event['runaway_loop'] = True
        # Detect excessive uncertainty
        uncertainty = meta_signals.get('uncertainty_level', 0.0)
        self.uncertainty_history.append(uncertainty)
        if len(self.uncertainty_history) > 5:
            self.uncertainty_history.pop(0)
        if sum(1 for u in self.uncertainty_history[-5:] if u > 0.5) >= 3:
            event['excessive_uncertainty'] = True
        # Detect repeated contradictions
        if meta_signals.get('contradiction'):
            self.contradiction_count += 1
        if self.contradiction_count >= 2:
            event['repeated_contradiction'] = True
        # Detect repeated error-recovery
        if mode == 'error-recovery':
            self.error_recovery_count += 1
        if self.error_recovery_count >= 2:
            event['repeated_error_recovery'] = True
        # Detect memory overload
        if len(memory_snapshot.get('user_messages', [])) > 10:
            self.memory_overload = True
            event['memory_overload'] = True
        # Compute stability score
        score = 1.0
        if event.get('runaway_loop'):
            score -= 0.3
        if event.get('excessive_uncertainty'):
            score -= 0.3
        if event.get('repeated_contradiction'):
            score -= 0.2
        if event.get('repeated_error_recovery'):
            score -= 0.2
        if event.get('memory_overload'):
            score -= 0.2
        self.stability_score = max(0.0, score)
        event['stability_score'] = self.stability_score
        self.stability_events.append(event)
        return event

    def reset_counters(self):
        self.contradiction_count = 0
        self.error_recovery_count = 0
        self.memory_overload = False

    def get_stability_score(self):
        return self.stability_score

    def get_events(self):
        return self.stability_events
