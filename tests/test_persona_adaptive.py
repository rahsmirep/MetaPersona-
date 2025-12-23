from src.persona_context import PersonaContext
from src.single_use_agent import SingleUseAgent
import time

def test_persona_memory_updates():
    persona = PersonaContext()
    agent = SingleUseAgent(agent_id='adaptive_test', persona_context=persona)
    agent.process_turn('Hello!')
    agent.process_turn('Please help me with a task.')
    agent.process_turn('Summarize progress')
    assert len(persona.style_history) >= 3
    assert len(persona.tone_history) >= 3
    assert persona.persona_evolution_state["last_update"] is not None

def test_signature_strengthening():
    persona = PersonaContext(signature_phrasing=["- Sincerely, MetaPersona"])
    agent = SingleUseAgent(agent_id='sig_adapt', persona_context=persona)
    for _ in range(5):
        agent.process_turn('What is your style?')
    # Signature should be reinforced in signature_patterns_used and signature_phrasing
    sigs = [sig for _, sig in persona.signature_patterns_used]
    assert any("Sincerely" in s for s in sigs)
    assert any("Sincerely" in s for s in persona.signature_phrasing)

def test_gradual_style_shift():
    persona = PersonaContext()
    agent = SingleUseAgent(agent_id='shift_test', persona_context=persona)
    # Simulate user using formal language
    for _ in range(3):
        agent.process_turn('Therefore, I request your assistance.')
    # Style should shift to formal, but not abruptly
    styles = [s for _, s in persona.style_history]
    assert styles[-1] == "formal"
    assert len(set(styles[-3:])) <= 2  # No abrupt jumps

def test_user_driven_adaptation():
    persona = PersonaContext()
    agent = SingleUseAgent(agent_id='user_adapt', persona_context=persona)
    agent.process_turn('Hey, can you help?')
    agent.process_turn('Yo, what do you think?')
    assert persona.voice_style == "casual"
    assert persona.user_preference_inferences["formality"] == "casual"

def test_persona_evolution_persistence():
    persona = PersonaContext()
    agent = SingleUseAgent(agent_id='persist_test', persona_context=persona)
    agent.process_turn('Please help me with a task.')
    time.sleep(0.1)
    agent.process_turn('Summarize progress')
    # Evolution state should persist and update
    assert persona.persona_evolution_state["last_update"] is not None
    assert persona.persona_evolution_state["stability"] <= 1.0
