from typing import Tuple

class DelegationConfidence:
    """
    Simple confidence scoring for agent-task fit.
    estimate_confidence(agent_role, task_type, context) -> (confidence_level, score)
    """
    # Example: agent_role = 'research', task_type = 'research', etc.
    @staticmethod
    def estimate_confidence(agent_role: str, task_type: str, context=None) -> Tuple[str, float]:
        if agent_role == task_type:
            return 'high', 0.95
        # Related types (e.g., writing agent can handle planning)
        related = {
            'writing': ['planning', 'alignment'],
            'planning': ['research', 'writing'],
            'critique': ['writing', 'alignment'],
            'alignment': ['writing', 'critique'],
            'research': ['planning'],
        }
        if agent_role in related and task_type in related[agent_role]:
            return 'medium', 0.7
        # Otherwise, low confidence
        return 'low', 0.3
