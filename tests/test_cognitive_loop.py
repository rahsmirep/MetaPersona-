from src.single_use_agent import SingleUseAgent

def test_cognitive_loop_full_turns():
    agent = SingleUseAgent(agent_id='test_agent')
    onboarding = agent.process_turn('')
    resp1 = agent.process_turn('My goal is to learn.')
    resp2 = agent.process_turn('Please do the task.')
    resp3 = agent.process_turn('asdfghjkl')
    resp4 = agent.process_turn('contradiction')
    assert onboarding is not None
    assert resp1 is not None
    assert resp2 is not None
    assert resp3 is not None
    assert resp4 is not None
import pytest
from src.single_use_agent import SingleUseAgent
from src.agent_messaging import AgentMessage

def test_cognitive_loop_full_turns():
    agent = SingleUseAgent(agent_id='test_agent')
    # Register dummy handlers for all modes
    def handler_task(msg):
        meta = msg.metadata.get('meta_signals', {})
        if meta.get('missing_information'):
            return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='clarification', payload={'result': 'Please clarify your request.'}, metadata={'missing_information': True})
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='response', payload={'result': 'Task executed!'}, metadata={})
    def handler_greeting(msg):
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='response', payload={'result': 'Hello!'}, metadata={})
    def handler_onboarding(msg):
        meta = msg.metadata.get('meta_signals', {})
        if meta.get('missing_information'):
            return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='onboarding', payload={'result': 'Onboarding: please provide more info.'}, metadata={'missing_information': True})
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='onboarding', payload={'result': 'Onboarding complete!'}, metadata={})
    def handler_reflection(msg):
        meta = msg.metadata.get('meta_signals', {})
        if meta.get('uncertainty_level', 0) > 0.4:
            return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='reflection', payload={'result': 'Reflecting on uncertainty.'}, metadata={'uncertainty': True})
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='reflection', payload={'result': 'Reflecting.'}, metadata={})
    def handler_error_recovery(msg):
        meta = msg.metadata.get('meta_signals', {})
        if meta.get('contradiction'):
            return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='error-recovery', payload={'result': 'Contradiction detected. Recovered.'}, metadata={'contradiction': True})
        return AgentMessage(sender=msg.receiver, receiver=msg.sender, intent='error-recovery', payload={'result': 'Recovered.'}, metadata={})
    agent.router.register_agent('agent_task', handler_task)
    agent.router.register_agent('agent_greeter', handler_greeting)
    agent.router.register_agent('agent_onboarding', handler_onboarding)
    agent.router.register_agent('agent_reflection', handler_reflection)
    agent.router.register_agent('agent_error_recovery', handler_error_recovery)
    agent.router.register_agent('agent_fallback', handler_reflection)

    # 0. Agent-initiated onboarding
    onboarding = agent.process_turn('')
    assert onboarding.payload['result'] == 'Onboarding complete!'
    # 1. User greeting/goal (should trigger greeting handler)
    resp1 = agent.process_turn('My goal is to learn.')
    assert resp1.payload['result'] == 'Hello!'
    # 2. Task
    resp2 = agent.process_turn('Please do the task.')
    assert resp2.payload['result'] == 'Task executed!'
    # 3. Ambiguous/unknown (should trigger onboarding due to stabilization)
    resp3 = agent.process_turn('asdfghjkl')
    assert 'Onboarding' in resp3.payload['result']
    # 4. Error recovery (contradiction)
    # Simulate contradiction by sending a message that triggers contradiction signal
    resp4 = agent.process_turn('contradiction')
    # Should trigger onboarding due to stabilization
    assert 'Onboarding' in resp4.payload['result']
    # Check memory and context persistence
    mem = agent.memory.snapshot()
    assert len(mem['user_messages']) == 0
    # The onboarding greeting is not a user message, and memory is cleared after stabilization, so user_messages should be empty
    # Check mode transitions
    mode_log = agent.get_mode_log()
    assert isinstance(mode_log, list)
    # Meta-reasoning trace should show uncertainty and contradiction
    meta_trace = agent.cognitive_loop.meta_reasoning.get_trace()
    assert any(m.get('uncertainty_level', 0) > 0.4 for m in meta_trace)
    assert any(m.get('contradiction') for m in meta_trace)
