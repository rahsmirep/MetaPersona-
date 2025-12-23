from typing import Dict, Any, Tuple

class DelegationRulesEngine:
    """
    Maps task types to agent IDs. Supports confidence, fallback, and override logic.
    """
    def __init__(self, agent_map: Dict[str, str], fallback_agent: str = None, overrides: Dict[str, str] = None):
        self.agent_map = agent_map  # e.g., {'research': 'research_agent', ...}
        self.fallback_agent = fallback_agent
        self.overrides = overrides or {}

    def get_agent_for_task(self, task_type: str, context: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
        # Check for override (e.g., user or workflow specifies agent)
        if context and 'override_agent' in context:
            return context['override_agent'], {'rule': 'override'}
        # Check for explicit override in rules
        if task_type in self.overrides:
            return self.overrides[task_type], {'rule': 'explicit_override'}
        # Standard mapping
        if task_type in self.agent_map:
            return self.agent_map[task_type], {'rule': 'standard'}
        # Fallback
        if self.fallback_agent:
            return self.fallback_agent, {'rule': 'fallback'}
        # No match
        return None, {'rule': 'no_match'}
