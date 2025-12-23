import re
from typing import Tuple

class TaskClassifier:
    """
    Lightweight rule-based classifier for task type detection.
    classify_task(text) -> (task_type, confidence)
    """
    TASK_PATTERNS = [
        ("research", [r"search|find|gather|lookup|investigate|reference|latest|external info"]),
        ("writing", [r"write|draft|compose|summarize|paraphrase|generate text|polish"]),
        ("planning", [r"plan|break down|steps|roadmap|sequence|workflow|organize"]),
        ("critique", [r"critique|review|evaluate|score|rate|feedback|assess|analyze output"]),
        ("alignment", [r"align|persona|style|consistency|match profile|revise for persona"]),
        ("execution", [r"execute|run|perform|carry out|do task"]),
    ]

    @classmethod
    def classify_task(cls, text: str) -> Tuple[str, float]:
        text = text.lower()
        for task_type, patterns in cls.TASK_PATTERNS:
            for pat in patterns:
                if re.search(pat, text):
                    return task_type, 0.95  # High confidence for rule match
        # Fallback: unknown
        return "unknown", 0.5
