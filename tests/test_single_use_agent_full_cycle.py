from src.persona_context import PersonaContext
from src.single_use_agent import SingleUseAgent

def test_single_use_agent_full_cycle():
    # Persona setup
    persona = PersonaContext(
        voice_style="cosmic",
        tone_modifiers=["inspiring"],
        mode_specific_style={"task": "cosmic", "reflection": "philosophical", "recovery": "gentle", "onboarding": "warm"},
        signature_phrasing=["- Cosmic Regards"]
    )
    agent = SingleUseAgent(agent_id='full_cycle', persona_context=persona)

    # 1. Onboarding (classification: onboarding, routing: onboarding handler)
    onboarding_msg = agent.process_turn('')
    print("ONBOARDING OUTPUT:", onboarding_msg.payload['result'])
    print("ONBOARDING INTERNAL:", onboarding_msg.payload.get('internal'))

    # 2. Planning (classification: task, routing: planning handler)
    plan_msg = agent.process_turn('Please help me with a complex task.')
    print("PLANNING OUTPUT:", plan_msg.payload['result'])
    print("PLANNING INTERNAL:", plan_msg.payload.get('internal'))

    # 3. Step execution (classification: task, routing: planning handler)
    step_msg = agent.process_turn('Proceed')
    print("STEP OUTPUT:", step_msg.payload['result'])
    print("STEP INTERNAL:", step_msg.payload.get('internal'))

    # 4. Reflection (classification: reflection, routing: reflection handler)
    agent.mode_manager._mode = 'reflection'
    reflect_msg = agent.process_turn('Summarize progress')
    print("REFLECTION OUTPUT:", reflect_msg.payload['result'])
    print("REFLECTION INTERNAL:", reflect_msg.payload.get('internal'))

    # 5. Error recovery (classification: error-recovery, routing: error handler)
    agent.mode_manager._mode = 'error-recovery'
    error_msg = agent.process_turn('Repair the plan')
    print("ERROR OUTPUT:", error_msg.payload['result'])
    print("ERROR INTERNAL:", error_msg.payload.get('internal'))

    # 6. Final persona memory state
    print("STYLE HISTORY:", persona.style_history)
    print("TONE HISTORY:", persona.tone_history)
    print("SIGNATURE PATTERNS USED:", persona.signature_patterns_used)
    print("PERSONA EVOLUTION STATE:", persona.persona_evolution_state)
