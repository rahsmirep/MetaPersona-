from src.persona_context import PersonaContext
from src.single_use_agent import SingleUseAgent

def test_persona_aware_planning():
    persona = PersonaContext(voice_style="cosmic", tone_modifiers=["inspiring"], signature_phrasing=["- Cosmic Regards"])
    agent = SingleUseAgent(agent_id='plan_test', persona_context=persona)
    agent.process_turn('')  # Onboarding
    resp = agent.process_turn('Please do a complex task.')
    # Planning output should reflect persona style and tone
    assert "cosmic" in str(resp).lower()
    assert "inspiring" in str(resp).lower() or "inspiring" in str(persona.tone_history[-1][1])
    assert "Cosmic Regards" in str(resp)
    # Internal reasoning should also be persona-shaped
    assert hasattr(resp, 'payload') and 'internal' in resp.payload
    assert "cosmic" in str(resp.payload['internal']).lower()

def test_persona_aware_reflection():
    persona = PersonaContext(voice_style="philosophical", tone_modifiers=["thoughtful"], signature_phrasing=["- Deeply Yours"])
    agent = SingleUseAgent(agent_id='reflect_test', persona_context=persona)
    agent.process_turn('')  # Onboarding
    agent.process_turn('Please do a task.')
    agent.process_turn('Proceed')
    agent.mode_manager._mode = 'reflection'
    resp = agent.process_turn('Summarize progress')
    # Reflection output should use persona phrasing and tone
    assert "philosophical" in str(resp).lower()
    assert "thoughtful" in str(resp).lower() or "thoughtful" in str(persona.tone_history[-1][1])
    assert "Deeply Yours" in str(resp)
    # Internal reflection should be persona-shaped
    assert hasattr(resp, 'payload') and 'internal' in resp.payload
    assert "philosophical" in str(resp.payload['internal']).lower()

def test_persona_aware_error_recovery():
    persona = PersonaContext(voice_style="gentle", tone_modifiers=["calm"], signature_phrasing=["- Steady Support"])
    agent = SingleUseAgent(agent_id='error_test', persona_context=persona)
    agent.process_turn('')  # Onboarding
    agent.process_turn('Please do a task.')
    agent.mode_manager._mode = 'error-recovery'
    resp = agent.process_turn('Repair the plan')
    # Error-recovery output should use persona tone and signature
    assert "gentle" in str(resp).lower()
    assert "calm" in str(resp).lower() or "calm" in str(persona.tone_history[-1][1])
    assert "Steady Support" in str(resp)
    # Internal error reasoning should be persona-shaped
    assert hasattr(resp, 'payload') and 'internal' in resp.payload
    assert "gentle" in str(resp.payload['internal']).lower()

def test_persona_memory_updates_after_internal_reasoning():
    persona = PersonaContext(voice_style="warm", tone_modifiers=["friendly"])
    agent = SingleUseAgent(agent_id='mem_test', persona_context=persona)
    agent.process_turn('')  # Onboarding
    resp = agent.process_turn('Please do a task.')
    # Persona memory should update after internal reasoning
    assert len(persona.style_history) > 0
    assert len(persona.tone_history) > 0
    # Internal reasoning should also update memory
    assert any("warm" in s for _, s in persona.style_history)
    assert any("friendly" in t for _, t in persona.tone_history)
