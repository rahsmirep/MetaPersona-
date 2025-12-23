
class ModeManager:
    """
    Context-aware manager for agent cognitive modes.
    Modes: greeting, onboarding, task-execution, reflection, error-recovery
    Provides a unified update_mode() API for the Router.
    """
    MODES = [
        'greeting',
        'onboarding',
        'task-execution',
        'reflection',
        'error-recovery',
    ]

    def __init__(self, initial_mode='greeting'):
        self._mode = initial_mode if initial_mode in self.MODES else 'greeting'
        self._log = []

    def get_mode(self):
        return self._mode

    def get_log(self):
        return list(self._log)

    def update_mode(self, classifier_result, prev_mode, message_context=None):
        """
        Centralized, context-aware mode transition logic.
        classifier_result: dict with 'predicted_intent', 'confidence', etc.
        prev_mode: previous mode string
        message_context: dict (optional)
        Returns: (new_mode, reason)
        """
        intent = classifier_result.get('predicted_intent')
        confidence = classifier_result.get('confidence', 0)
        if confidence is None:
            confidence = 0.0
        signals = classifier_result.get('signals', {})
        ambiguous = signals.get('ambiguous', False)
        reason = None
        new_mode = prev_mode

        # Mode transition rules (context-aware)
        if prev_mode == 'greeting':
            # Prevent transition away from greeting on the very first turn
            if len(self._log) == 0:
                new_mode = 'greeting'
                reason = 'First turn: remain in greeting mode.'
            elif intent == 'greeting' and confidence >= 0.7:
                new_mode = 'onboarding'
                reason = 'Greeting detected, transitioning to onboarding.'
            elif intent == 'task' and confidence >= 0.7:
                new_mode = 'task-execution'
                reason = 'Task intent detected, entering task-execution.'
            elif ambiguous or confidence < 0.5:
                new_mode = 'reflection'
                reason = 'Ambiguous or low-confidence message, entering reflection.'
        elif prev_mode == 'onboarding':
            if intent == 'task' and confidence >= 0.7:
                new_mode = 'task-execution'
                reason = 'Onboarding complete, task intent detected.'
            elif intent == 'greeting' and confidence >= 0.7:
                new_mode = 'onboarding'
                reason = 'Still onboarding (greeting loop).'
            elif ambiguous or confidence < 0.5:
                new_mode = 'reflection'
                reason = 'Ambiguous or low-confidence during onboarding, entering reflection.'
        elif prev_mode == 'task-execution':
            if intent == 'reflection':
                new_mode = 'reflection'
                reason = 'Reflection intent detected, exiting task mode.'
            elif intent == 'greeting' and confidence >= 0.7:
                new_mode = 'greeting'
                reason = 'Greeting detected, returning to greeting mode.'
            elif intent == 'error' or (confidence is not None and confidence < 0.3):
                new_mode = 'error-recovery'
                reason = 'Error or very low confidence, entering error-recovery.'
            elif intent == 'task' and confidence >= 0.7:
                new_mode = 'task-execution'
                reason = 'Continue task-execution (multi-turn).'
            elif ambiguous or confidence < 0.5:
                new_mode = 'reflection'
                reason = 'Ambiguous or low-confidence during task, entering reflection.'
        elif prev_mode == 'reflection':
            if intent == 'task' and confidence >= 0.7:
                new_mode = 'task-execution'
                reason = 'Recovered from reflection, task intent detected.'
            elif intent == 'greeting' and confidence >= 0.7:
                new_mode = 'greeting'
                reason = 'Greeting detected, returning to greeting mode.'
            elif intent == 'onboarding':
                new_mode = 'onboarding'
                reason = 'Onboarding intent detected.'
            elif ambiguous or confidence < 0.5:
                new_mode = 'reflection'
                reason = 'Remain in reflection (ambiguous/low-confidence).'
        elif prev_mode == 'error-recovery':
            if intent == 'greeting' and confidence >= 0.7:
                new_mode = 'greeting'
                reason = 'Recovered from error, greeting detected.'
            elif intent == 'task' and confidence >= 0.7:
                new_mode = 'task-execution'
                reason = 'Recovered from error, task intent detected.'
            elif ambiguous or confidence < 0.5:
                new_mode = 'reflection'
                reason = 'Remain in error-recovery or move to reflection.'

        # Default fallback
        if new_mode == prev_mode and (ambiguous or confidence < 0.5):
            new_mode = 'reflection'
            reason = 'Default fallback: ambiguous or low-confidence.'

        # Log transition
        if new_mode != prev_mode:
            self._log.append({
                'prev_mode': prev_mode,
                'new_mode': new_mode,
                'reason': reason,
                'intent': intent,
                'confidence': confidence,
                'signals': signals
            })
            self._mode = new_mode
        return new_mode, reason
