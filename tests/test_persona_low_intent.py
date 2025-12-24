from src.persona_context import PersonaContext
from src.single_use_agent import SingleUseAgent
import pytest

def test_low_intent_input_suppresses_persona():
    persona = PersonaContext(voice_style="warm", tone_modifiers=["friendly"], signature_phrasing=["- Warmly"])
    agent = SingleUseAgent(agent_id='low_intent', persona_context=persona)
    agent.process_turn('')  # Onboarding
    # Low-intent/casual/dismissive inputs
    low_intent_inputs = [
        "nothing lol", "idk", "nah", "don’t care", "nope", "whatever", "meh", "shrug"
    ]
    for inp in low_intent_inputs:
        resp = agent.process_turn(inp)
        # Should not inject emotional concern or persona greeting
        result = str(resp)
        assert "Is everything okay" not in result
        assert "Warmly" not in result  # signature phrasing suppressed
        assert "friendly" not in result  # tone suppressed
        # Should be neutral/minimal
        assert "[neutral" in result or "[minimal" in result or "[ | ]" in result


def test_fallback_routing_is_neutral():
    persona = PersonaContext(voice_style="cheerful", tone_modifiers=["upbeat"], signature_phrasing=["- Cheers"])
    agent = SingleUseAgent(agent_id='fallback_test', persona_context=persona)
    agent.process_turn('')  # Onboarding
    # Simulate fallback/diagnostic
    agent.mode_manager._mode = 'fallback'
    resp = agent.process_turn('Unroutable input')
    result = str(resp)
    # Should not inject persona greeting or signature
    assert "Hey! I’m" not in result
    assert "Cheers" not in result
    assert "upbeat" not in result
    # Should be neutral/minimal
    assert "[neutral" in result or "[minimal" in result or "[ | ]" in result


def test_persona_suppression_mode_flag():
    persona = PersonaContext(voice_style="quirky", tone_modifiers=["playful"], signature_phrasing=["- Quirkily"])
    persona.persona_suppression_mode = True
    agent = SingleUseAgent(agent_id='suppression', persona_context=persona)
    agent.process_turn('')  # Onboarding
    resp = agent.process_turn('Just checking')
    result = str(resp)
    # Persona shaping should be minimal
    assert "Quirkily" not in result
    assert "playful" not in result
    assert "quirky" not in result
    assert "[neutral" in result or "[minimal" in result or "[ | ]" in result


def test_single_use_agent_is_entry_point():
    # Ensure SingleUseAgent is still the only entry point
    persona = PersonaContext()
    agent = SingleUseAgent(agent_id='entrypoint', persona_context=persona)
    assert hasattr(agent, 'process_turn')
    assert callable(agent.process_turn)
