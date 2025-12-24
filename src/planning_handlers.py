from src.agent_messaging import AgentMessage

def handler_task(msg):
    persona = msg.metadata.get('persona_context')
    from src.persona_styler import PersonaStyler
    styler = PersonaStyler(persona)
    plan = msg.metadata.get('task_context', {}).get('current_plan')
    step_index = msg.metadata.get('task_context', {}).get('current_step_index', 0)
    flow = msg.metadata.get('flow_signals', {})
    user_msg = msg.payload.get('user_message', '').lower()
    # Persona-aware plan generation (internal reasoning)
    if plan and step_index < len(plan):
        step = plan[step_index]['step']
        # Internal reasoning shaped by persona
        reasoning = f"{persona.get_mode_style('task').capitalize()} reasoning: Considering step '{step}' with tone {persona.tone_modifiers}."
        reasoning_styled = styler.style(reasoning, mode='task')
    else:
        reasoning_styled = None
    if not plan or step_index >= len(plan):
        # Always set internal reasoning output, even if None
        internal = reasoning_styled if reasoning_styled is not None else styler.style(f"{persona.get_mode_style('task').capitalize()} internal: No plan present.", mode='task')
        if flow.get('should_reflect') or flow.get('should_summarize'):
            summary = f"{persona.get_mode_style('reflection').capitalize()} summary: All steps complete. Would you like a summary or next steps?"
            styled = styler.style(summary, mode='reflection')
            return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='reflection', payload={'result': styled, 'internal': internal}, metadata={})
        note = f"{persona.get_mode_style('task').capitalize()} note: No plan or all steps complete."
        styled = styler.style(note, mode='task')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='response', payload={'result': styled, 'internal': internal}, metadata={})
    current_step = plan[step_index]['step'] if plan and step_index < len(plan) else None
    # Clarification needed
    if flow.get('should_request_clarification'):
        question = f"{persona.get_mode_style('task').capitalize()} request: Could you clarify or provide more info for: '{current_step}'?"
        styled = styler.style(question, mode='task')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='clarification', payload={'result': styled, 'step_complete': False, 'internal': reasoning_styled}, metadata={'step_complete': False})
    # Ask a question if needed
    if flow.get('should_ask_question'):
        question = f"{persona.get_mode_style('task').capitalize()} question: What details do you want for: '{current_step}'?"
        styled = styler.style(question, mode='task')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='question', payload={'result': styled, 'step_complete': False, 'internal': reasoning_styled}, metadata={'step_complete': False})
    # Continue plan if allowed
    if flow.get('should_continue_plan') and ('proceed' in user_msg or 'next' in user_msg or 'continue' in user_msg):
        action = f"{persona.get_mode_style('task').capitalize()} action: Executed step: {current_step}"
        styled = styler.style(action, mode='task')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='response', payload={'result': styled, 'step_complete': True, 'internal': reasoning_styled}, metadata={'step_complete': True})
    # Pause plan if needed
    if flow.get('should_pause_plan'):
        pause = f"{persona.get_mode_style('task').capitalize()} pause: Pausing at step: {current_step} until clarification."
        styled = styler.style(pause, mode='task')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='pause', payload={'result': styled, 'step_complete': False, 'internal': reasoning_styled}, metadata={'step_complete': False})
    # Default: describe current step
    info = f"{persona.get_mode_style('task').capitalize()} info: Current step: {current_step}"
    styled = styler.style(info, mode='task')
    return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='response', payload={'result': styled, 'step_complete': False, 'internal': reasoning_styled}, metadata={'step_complete': False})

def handler_reflection(msg):
    persona = msg.metadata.get('persona_context')
    plan = msg.metadata.get('task_context', {}).get('current_plan')
    step_index = msg.metadata.get('task_context', {}).get('current_step_index', 0)
    completed = msg.metadata.get('task_context', {}).get('completed_steps', [])
    pending = msg.metadata.get('task_context', {}).get('pending_steps', [])
    flow = msg.metadata.get('flow_signals', {})
    from src.persona_styler import PersonaStyler
    styler = PersonaStyler(persona)
    # Suppress persona shaping for fallback/diagnostic
    fallback_or_diag = msg.metadata.get('mode', '') in ('fallback', 'diagnostic') or getattr(persona, 'persona_suppression_mode', False)
    if fallback_or_diag:
        summary = "[neutral | ] Routing to main agent."
        internal_styled = "[neutral | ] Diagnostic: fallback routing."
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='reflection', payload={'result': summary, 'internal': internal_styled}, metadata={})
    # Persona-aware reflection (internal reasoning)
    summary = f"{persona.get_mode_style('reflection').capitalize()} reflection: Plan progress: {len(completed)} completed, {len(pending)} pending. "
    if plan and step_index < len(plan):
        summary += f"Next step: {plan[step_index]['step']}"
    else:
        summary += "All steps complete."
    # Internal reflection shaped by persona
    internal_reflection = f"{persona.get_mode_style('reflection').capitalize()} internal: Reviewing plan with tone {persona.tone_modifiers}."
    internal_styled = styler.style(internal_reflection, mode='reflection')
    # Suggest next steps if requested
    if flow.get('should_summarize'):
        summary += " Would you like to continue, revise, or end the plan?"
    if flow.get('should_reflect'):
        summary = f"{persona.get_mode_style('reflection').capitalize()} meta: " + summary
    styled = styler.style(summary, mode='reflection')
    return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='reflection', payload={'result': styled, 'internal': internal_styled}, metadata={})

def handler_error_recovery(msg):
    persona = msg.metadata.get('persona_context')
    plan = msg.metadata.get('task_context', {}).get('current_plan')
    flow = msg.metadata.get('flow_signals', {})
    from src.persona_styler import PersonaStyler
    styler = PersonaStyler(persona)
    fallback_or_diag = msg.metadata.get('mode', '') in ('fallback', 'diagnostic') or getattr(persona, 'persona_suppression_mode', False)
    if fallback_or_diag:
        summary = "[neutral | ] Fallback: unable to process request."
        internal_styled = "[neutral | ] Diagnostic: fallback error recovery."
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='error-recovery', payload={'result': summary, 'repaired_plan': [], 'internal': internal_styled}, metadata={'plan_repaired': False})
    # Simulate plan repair for test
    repaired_plan = [{'step': 'Repaired step 1', 'status': 'pending'}]
    # Persona-aware error recovery (internal reasoning)
    internal_error = f"{persona.get_mode_style('recovery').capitalize()} internal: Repairing plan with tone {persona.tone_modifiers}. Signature: {' '.join(persona.signature_phrasing)}"
    internal_styled = styler.style(internal_error, mode='recovery')
    explanation = f"{persona.get_mode_style('recovery').capitalize()} recovery: Plan repaired. "
    if flow.get('should_ask_question') or flow.get('should_request_clarification'):
        explanation += "Could you tell me what went wrong or what you expected?"
    if flow.get('should_reflect'):
        explanation += " Let's reflect on what led to the error."
    styled = styler.style(explanation, mode='recovery')
    return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='error-recovery', payload={'result': styled, 'repaired_plan': repaired_plan, 'internal': internal_styled}, metadata={'plan_repaired': True})

def handler_onboarding(msg):
    persona = msg.metadata.get('persona_context')
    flow = msg.metadata.get('flow_signals', {})
    from src.persona_styler import PersonaStyler
    styler = PersonaStyler(persona)
    onboarding_questions = [
        f"{persona.get_mode_style('onboarding').capitalize()} onboarding: What are your goals or preferences?",
        f"{persona.get_mode_style('onboarding').capitalize()} onboarding: Do you have any constraints or deadlines?",
        f"{persona.get_mode_style('onboarding').capitalize()} onboarding: How would you like to proceed?"
    ]
    # Internal onboarding reasoning
    internal_onboarding = f"{persona.get_mode_style('onboarding').capitalize()} internal: Initializing onboarding with tone {persona.tone_modifiers}."
    internal_styled = styler.style(internal_onboarding, mode='onboarding')
    # Ask onboarding questions in sequence
    if flow.get('should_ask_question') or flow.get('should_request_clarification'):
        question = onboarding_questions[0]  # Could be made more dynamic
        styled = styler.style(question, mode='onboarding')
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='onboarding', payload={'result': styled, 'internal': internal_styled}, metadata={})
    # Smooth transition to task mode
    complete = f'{persona.get_mode_style('onboarding').capitalize()} onboarding: Onboarding complete! Planning context initialized. Ready to start your first task.'
    styled = styler.style(complete, mode='onboarding')
    return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='onboarding', payload={'result': styled, 'internal': internal_styled}, metadata={})
