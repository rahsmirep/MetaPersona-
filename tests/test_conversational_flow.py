import pytest
from src.single_use_agent import SingleUseAgent

def test_conversational_flow_signals():
    agent = SingleUseAgent(agent_id='flowtest')
    # Onboarding: should ask onboarding question
    onboarding = agent.process_turn('')
    assert 'onboarding' in onboarding.intent.lower() or 'onboarding' in onboarding.payload['result'].lower()
    # User provides a goal, should continue onboarding or start plan
    resp1 = agent.process_turn('My goal is to learn Python.')
    assert 'onboarding' in resp1.intent.lower() or 'planning' in resp1.intent.lower() or 'plan' in resp1.payload['result'].lower()
    # Agent should ask for clarification if info is missing
    resp2 = agent.process_turn('Proceed')
    assert 'clarify' in resp2.payload['result'].lower() or 'question' in resp2.intent.lower() or 'current step' in resp2.payload['result'].lower()
    # Agent should summarize if plan is complete or reflection requested
    agent.mode_manager._mode = 'reflection'
    resp3 = agent.process_turn('Summarize progress')
    assert 'progress' in resp3.payload['result'].lower() or 'summary' in resp3.payload['result'].lower() or 'reflect' in resp3.payload['result'].lower()
    # Agent should not repeat the same question
    resp4 = agent.process_turn('Proceed')
    resp5 = agent.process_turn('Proceed')
    assert resp4.payload['result'] != resp5.payload['result'] or 'clarify' not in resp5.payload['result'].lower()
    # Agent should maintain continuity and not overwhelm
    for _ in range(3):
        resp = agent.process_turn('Proceed')
        assert 'clarify' not in resp.payload['result'].lower() or 'question' not in resp.intent.lower()
    # Agent should smoothly transition between modes
    agent.mode_manager._mode = 'error-recovery'
    resp6 = agent.process_turn('Repair the plan')
    assert 'plan repaired' in resp6.payload['result'].lower() or 'explain' in resp6.payload['result'].lower()
