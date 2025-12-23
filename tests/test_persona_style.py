from src.single_use_agent import SingleUseAgent

def test_persona_consistency_across_turns():
    agent = SingleUseAgent(agent_id='persona_test')
    # Turn 1: Onboarding
    resp1 = agent.process_turn('')
    # Turn 2: Task
    resp2 = agent.process_turn('Please help me with a task.')
    # Turn 3: Reflection
    resp3 = agent.process_turn('Summarize progress')
    # Turn 4: Error recovery
    resp4 = agent.process_turn('contradiction')
    # All outputs should include persona style markers
    for resp in [resp1, resp2, resp3, resp4]:
        assert resp is not None
        assert '[' in str(resp) or 'onboarding' in str(resp).lower() or 'reflection' in str(resp).lower()

def test_signature_phrasing():
    from src.persona_context import PersonaContext
    from src.single_use_agent import SingleUseAgent
    persona = PersonaContext(signature_phrasing=["- Yours truly, MetaPersona"])
    agent = SingleUseAgent(agent_id='sig_test', persona_context=persona)
    resp = agent.process_turn('What is your style?')
    assert "Yours truly" in str(resp)

def test_mode_specific_style():
    from src.persona_context import PersonaContext
    from src.single_use_agent import SingleUseAgent
    persona = PersonaContext(mode_specific_style={"task": "cosmic", "reflection": "philosophical", "recovery": "gentle", "onboarding": "warm"})
    agent = SingleUseAgent(agent_id='style_test', persona_context=persona)
    resp_task = agent.process_turn('Please do the task.')
    resp_reflect = agent.process_turn('Summarize progress')
    assert "Cosmic" in str(resp_task) or "cosmic" in str(resp_task)
    assert "Philosophical" in str(resp_reflect) or "philosophical" in str(resp_reflect)

def test_persona_memory_influence():
    from src.persona_context import PersonaContext
    from src.single_use_agent import SingleUseAgent
    persona = PersonaContext()
    persona.update_style('voice_style', 'warm')
    agent = SingleUseAgent(agent_id='mem_test', persona_context=persona)
    resp = agent.process_turn('How do you sound?')
    assert "Warm" in str(resp) or "warm" in str(resp)
