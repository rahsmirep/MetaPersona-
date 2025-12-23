
import re
from typing import Dict, Any

class TaskClassifier:
    """
    Multi-signal classifier for intent detection with weighted confidence and signal reporting.
    classify(text) -> {
        'predicted_intent': str,
        'confidence': float,
        'signals': Dict[str, Any]
    }
    """
    # Patterns and signals
    TASK_KEYWORDS = [
        'do', 'run', 'execute', 'start', 'complete', 'finish', 'make', 'build', 'create', 'generate',
        'analyze', 'process', 'calculate', 'solve', 'find', 'update', 'delete', 'add', 'remove',
        'task:', 'please', 'could you', 'would you', 'can you', 'let us', "let's", 'help me', 'assist',
    ]
    STRUCTURAL_PREFIXES = ['/', '!', 'task:', 'run', 'execute']
    GREETING_PATTERNS = [r'\bhi\b', r'\bhello\b', r'\bhey\b', r'\bgreetings\b', r'\bgood (morning|afternoon|evening)\b']
    CONVERSATION_PATTERNS = [r'\bhow are you\b', r"\bwhat's up\b", r'\bcan we talk\b', r"\blet's chat\b"]
    TASK_PATTERNS = [
        ("research", [r"search|find|gather|lookup|investigate|reference|latest|external info"]),
        ("writing", [r"write|draft|compose|summarize|paraphrase|generate text|polish"]),
        ("planning", [r"plan|break down|steps|roadmap|sequence|workflow|organize"]),
        ("critique", [r"critique|review|evaluate|score|rate|feedback|assess|analyze output"]),
        ("alignment", [r"align|persona|style|consistency|match profile|revise for persona"]),
        ("execution", [r"execute|run|perform|carry out|do task"]),
    ]

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        text_lc = text.lower().strip() if text else ''
        signals = {}
        score = 0.0
        contributing = []

        # 1. Structural cues (prefixes, commands)
        structural = any(text_lc.startswith(prefix) for prefix in cls.STRUCTURAL_PREFIXES)
        if structural:
            score += 0.35
            contributing.append('structural_prefix')
        signals['structural_prefix'] = structural

        # 2. Keyword detection
        keyword_hits = [kw for kw in cls.TASK_KEYWORDS if kw in text_lc]
        if keyword_hits:
            score += 0.25
            contributing.append('task_keyword')
        signals['task_keywords'] = keyword_hits

        # 3. Pattern matching for task types
        matched_task_type = None
        for task_type, patterns in cls.TASK_PATTERNS:
            for pat in patterns:
                if re.search(pat, text_lc):
                    matched_task_type = task_type
                    score += 0.25
                    contributing.append(f'task_pattern:{task_type}')
                    break
            if matched_task_type:
                break
        signals['task_pattern'] = matched_task_type

        # 4. Greeting/conversational detection
        greeting = any(re.search(pat, text_lc) for pat in cls.GREETING_PATTERNS)
        conversation = any(re.search(pat, text_lc) for pat in cls.CONVERSATION_PATTERNS)
        if greeting:
            signals['greeting'] = True
            score = max(score, 0.7)  # If greeting, not a task
            contributing.append('greeting')
        else:
            signals['greeting'] = False
        if conversation:
            signals['conversation'] = True
            score = max(score, 0.6)
            contributing.append('conversation')
        else:
            signals['conversation'] = False

        # 5. Ambiguity detection
        ambiguous = False
        if not (structural or keyword_hits or matched_task_type) and not greeting and not conversation:
            ambiguous = True
            contributing.append('ambiguous')
            score = 0.3
        signals['ambiguous'] = ambiguous

        # 6. Final intent decision
        if greeting:
            predicted_intent = 'greeting'
        elif conversation:
            predicted_intent = 'conversational'
        elif structural or keyword_hits or matched_task_type:
            predicted_intent = 'task'
        elif ambiguous:
            predicted_intent = 'ambiguous'
        else:
            predicted_intent = 'unknown'

        # 7. Confidence normalization
        confidence = min(score, 1.0)
        if predicted_intent == 'ambiguous' or predicted_intent == 'unknown':
            confidence = 0.3
        elif predicted_intent == 'greeting':
            confidence = 0.98
        elif predicted_intent == 'conversational':
            confidence = 0.85
        elif confidence < 0.7:
            confidence = 0.6

        # 8. Output schema
        return {
            'predicted_intent': predicted_intent,
            'confidence': round(confidence, 3),
            'signals': signals,
            'contributing_signals': contributing
        }
