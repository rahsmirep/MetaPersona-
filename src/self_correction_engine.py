from typing import Dict, Any

class SelfCorrectionEngine:
    def __init__(self):
        self.corrections = []

    def revise_task_context(self, task_context: Any, meta_signals: Dict[str, Any]):
        # If contradiction, clear context; if missing info, reset
        if meta_signals.get('contradiction'):
            task_context.clear()
            self.corrections.append('Task context cleared due to contradiction.')
        elif meta_signals.get('missing_information'):
            task_context.reset_missing()
            self.corrections.append('Task context reset for missing information.')
        # Stability-driven: if instability, rebuild context
        if meta_signals.get('stability_signals'):
            stability = meta_signals['stability_signals']
            if stability.get('runaway_loop') or stability.get('excessive_uncertainty') or stability.get('repeated_contradiction') or stability.get('repeated_error_recovery') or stability.get('memory_overload') or stability.get('stability_score', 1.0) < 0.5:
                task_context.clear()
                self.corrections.append('Task context rebuilt due to instability.')

    def prune_memory(self, memory: Any, meta_signals: Dict[str, Any]):
        # If unstable, clear oldest user message
        if meta_signals.get('unstable_state') and hasattr(memory, 'user_messages') and memory.user_messages:
            memory.user_messages.popleft()
            self.corrections.append('Oldest user message pruned due to instability.')
        # Stability-driven: if memory overload or instability, clear all
        if meta_signals.get('stability_signals'):
            stability = meta_signals['stability_signals']
            if stability.get('memory_overload') or stability.get('stability_score', 1.0) < 0.5:
                memory.user_messages.clear()
                memory.agent_responses.clear()
                self.corrections.append('Memory cleared due to overload or instability.')

    def reset_mode(self, mode_manager: Any, meta_signals: Dict[str, Any]):
        if meta_signals.get('unstable_state'):
            mode_manager._mode = 'reflection'
            self.corrections.append('Mode reset to reflection due to instability.')

    def refine_output(self, handler_output: Any, meta_signals: Dict[str, Any]):
        # If contradiction, add correction note
        if meta_signals.get('contradiction') and hasattr(handler_output, 'payload'):
            handler_output.payload['correction'] = 'Output revised due to contradiction.'
            self.corrections.append('Handler output revised for contradiction.')
        # Stability-driven: if instability, simplify output
        if meta_signals.get('stability_signals') and hasattr(handler_output, 'payload'):
            stability = meta_signals['stability_signals']
            if stability.get('runaway_loop') or stability.get('excessive_uncertainty') or stability.get('repeated_contradiction') or stability.get('repeated_error_recovery') or stability.get('memory_overload') or stability.get('stability_score', 1.0) < 0.5:
                handler_output.payload['correction'] = 'Output simplified due to instability.'
                self.corrections.append('Handler output simplified for instability.')

    def get_corrections(self):
        return self.corrections
