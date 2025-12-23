from typing import Dict, Any

class ConversationFlowEngine:
    """
    Manages conversational flow and turn management for the agent.
    Decides when to ask, answer, continue, pause, reflect, escalate, clarify, or summarize
    based on classifier, meta-signals, stability, planning, and memory context.
    """
    def __init__(self):
        self.last_question = None
        self.last_mode = None
        self.last_clarification = None
        self.last_summary_turn = -1
        self.turn_count = 0

    def analyze_flow(self, *,
                     classifier_output: Dict[str, Any],
                     meta_signals: Dict[str, Any],
                     stability_signals: Dict[str, Any],
                     planning_state: Dict[str, Any],
                     memory_context: Dict[str, Any],
                     current_mode: str,
                     handler_output: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Returns a dict of flow-signals for the current turn.
        """
        flow_signals = {
            'should_ask_question': False,
            'should_continue_plan': False,
            'should_pause_plan': False,
            'should_reflect': False,
            'should_summarize': False,
            'should_request_clarification': False,
            'flow_reason': '',
        }
        # Example rules (expand as needed):
        intent = classifier_output.get('predicted_intent')
        unstable = meta_signals.get('unstable_state') or stability_signals.get('stability_score', 1.0) < 0.7
        missing_info = meta_signals.get('missing_information') or 'clarification' in (handler_output or {}).get('intent', '')
        plan_exists = planning_state.get('current_plan') is not None
        plan_complete = planning_state.get('current_plan') and planning_state.get('current_step_index', 0) >= len(planning_state.get('current_plan', []))
        # Pacing: avoid repeating questions, mode switches, or clarifications
        if self.last_mode == current_mode and current_mode == 'reflection' and self.turn_count - self.last_summary_turn < 2:
            flow_signals['should_reflect'] = False
            flow_signals['should_summarize'] = False
            flow_signals['flow_reason'] = 'Recently summarized, skipping.'
        elif intent == 'reflection' or (unstable and current_mode != 'reflection'):
            flow_signals['should_reflect'] = True
            flow_signals['should_summarize'] = True
            flow_signals['flow_reason'] = 'Reflection or instability detected.'
            self.last_summary_turn = self.turn_count
        elif missing_info:
            flow_signals['should_pause_plan'] = True
            flow_signals['should_request_clarification'] = True
            flow_signals['should_ask_question'] = True
            flow_signals['flow_reason'] = 'Missing information, pausing for clarification.'
            self.last_clarification = self.turn_count
        elif plan_exists and not plan_complete:
            flow_signals['should_continue_plan'] = True
            flow_signals['flow_reason'] = 'Plan in progress, continuing.'
        elif plan_complete:
            flow_signals['should_reflect'] = True
            flow_signals['should_summarize'] = True
            flow_signals['flow_reason'] = 'Plan complete, summarizing.'
            self.last_summary_turn = self.turn_count
        else:
            flow_signals['flow_reason'] = 'Default flow.'
        # Avoid overwhelming user
        if memory_context.get('clarification_count', 0) > 2:
            flow_signals['should_request_clarification'] = False
            flow_signals['should_ask_question'] = False
            flow_signals['flow_reason'] += ' Too many clarifications, suppressing.'
        self.last_mode = current_mode
        self.turn_count += 1
        return flow_signals
