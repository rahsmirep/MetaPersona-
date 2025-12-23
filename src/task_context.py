from typing import Any, Dict, List, Optional

class TaskContext:
    def reset_missing(self):
        # Dummy: clear unresolved questions and parameters
        self.unresolved_questions.clear()
        self.parameters.clear()
    def __init__(self):
        self.current_task: Optional[str] = None
        self.partial_plans: List[Dict[str, Any]] = []
        self.parameters: Dict[str, Any] = {}
        self.unresolved_questions: List[str] = []
        self.progress_state: Dict[str, Any] = {}
        # Planning fields
        self.current_plan: Optional[list] = None
        self.current_step_index: int = 0
        self.completed_steps: list = []
        self.pending_steps: list = []
        self.plan_confidence: float = 0.0
        self.plan_revision_history: list = []

    def set_task(self, task: str):
        self.current_task = task

    def add_plan(self, plan: Dict[str, Any]):
        self.partial_plans.append(plan)

    def set_parameter(self, key: str, value: Any):
        self.parameters[key] = value

    def add_unresolved_question(self, question: str):
        self.unresolved_questions.append(question)

    def set_progress(self, key: str, value: Any):
        self.progress_state[key] = value

    def clear(self):
        self.current_task = None
        self.partial_plans.clear()
        self.parameters.clear()
        self.unresolved_questions.clear()
        self.progress_state.clear()
        self.current_plan = None
        self.current_step_index = 0
        self.completed_steps = []
        self.pending_steps = []
        self.plan_confidence = 0.0
        self.plan_revision_history = []

    def snapshot(self) -> Dict[str, Any]:
        return {
            'current_task': self.current_task,
            'partial_plans': list(self.partial_plans),
            'parameters': dict(self.parameters),
            'unresolved_questions': list(self.unresolved_questions),
            'progress_state': dict(self.progress_state),
            'current_plan': list(self.current_plan) if self.current_plan else None,
            'current_step_index': self.current_step_index,
            'completed_steps': list(self.completed_steps),
            'pending_steps': list(self.pending_steps),
            'plan_confidence': self.plan_confidence,
            'plan_revision_history': list(self.plan_revision_history),
        }
