from typing import Dict, Any

class MetaReasoning:
    def __init__(self):
        self.trace = []

    def analyze(self, classifier_output: Dict[str, Any], handler_output: Any = None, memory_snapshot: Dict[str, Any] = None) -> Dict[str, Any]:
        meta_signals = {
            'uncertainty_level': 0.0,
            'contradiction': False,
            'missing_information': False,
            'unstable_state': False,
            'recommended_next_mode': None,
            'meta_summary': '',
        }
        confidence = classifier_output.get('confidence', 1.0)
        signals = classifier_output.get('signals', {})
        # Uncertainty detection
        if confidence < 0.5 or signals.get('ambiguous'):
            meta_signals['uncertainty_level'] = 1.0 - confidence
            meta_signals['recommended_next_mode'] = 'reflection'
            meta_signals['meta_summary'] += 'Uncertainty detected. '
        # Contradiction detection (dummy logic)
        if signals.get('contradiction'):
            meta_signals['contradiction'] = True
            meta_signals['recommended_next_mode'] = 'error-recovery'
            meta_signals['meta_summary'] += 'Contradiction detected. '
        # Missing information detection (dummy logic)
        if signals.get('missing_info'):
            meta_signals['missing_information'] = True
            meta_signals['recommended_next_mode'] = 'onboarding'
            meta_signals['meta_summary'] += 'Missing information detected. '
        # Unstable/confused state (dummy logic)
        if memory_snapshot and len(memory_snapshot.get('mode_transitions', [])) > 2:
            last_modes = [m['new_mode'] for m in memory_snapshot['mode_transitions'][-3:]]
            if len(set(last_modes)) > 2:
                meta_signals['unstable_state'] = True
                meta_signals['recommended_next_mode'] = 'reflection'
                meta_signals['meta_summary'] += 'Unstable/confused state detected. '
        # Handler output based checks
        if handler_output and hasattr(handler_output, 'metadata'):
            if handler_output.metadata.get('contradiction'):
                meta_signals['contradiction'] = True
                meta_signals['recommended_next_mode'] = 'error-recovery'
                meta_signals['meta_summary'] += 'Handler contradiction detected. '
            if handler_output.metadata.get('missing_information'):
                meta_signals['missing_information'] = True
                meta_signals['recommended_next_mode'] = 'onboarding'
                meta_signals['meta_summary'] += 'Handler missing information detected. '
        self.trace.append(meta_signals)
        return meta_signals

    def get_trace(self):
        return self.trace
