import pytest
from src.single_use_agent import SingleUseAgent

def test_planning_engine_multi_turn():
    agent = SingleUseAgent(agent_id='planner')
    # 0. Onboarding
    onboarding = agent.process_turn('')
    assert 'Onboarding' in onboarding.payload['result']
    # 1. User requests a complex task (should trigger plan generation)
    resp1 = agent.process_turn('Please do a complex-task for me')
    plan_ctx = agent.task_context
    assert plan_ctx.current_plan is not None
    assert len(plan_ctx.current_plan) > 1
    assert plan_ctx.current_step_index == 0
    # 2. Execute first step
    resp2 = agent.process_turn('Proceed')
    assert 'Executed step' in resp2.payload['result']
    assert plan_ctx.current_step_index == 1
    # 3. Execute next step
    resp3 = agent.process_turn('Proceed')
    assert 'Executed step' in resp3.payload['result']
    assert plan_ctx.current_step_index == 2
    # 4. Complete final step
    resp4 = agent.process_turn('Proceed')
    assert 'Executed step' in resp4.payload['result'] or 'No plan or all steps complete.' in resp4.payload['result']
    # 5. Plan revision (user changes requirements)
    resp5 = agent.process_turn('Please revise the plan')
    assert plan_ctx.current_step_index == 0
    assert plan_ctx.plan_revision_history
    # 6. Reflection handler summarizes plan
    agent.mode_manager._mode = 'reflection'
    resp6 = agent.process_turn('Summarize plan progress')
    assert 'Plan progress' in resp6.payload['result']
    # 7. Error recovery handler repairs plan
    agent.mode_manager._mode = 'error-recovery'
    resp7 = agent.process_turn('Repair the plan')
    assert 'Plan repaired' in resp7.payload['result']
