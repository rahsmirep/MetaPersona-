
import pytest
from src.single_use_agent import SingleUseAgent
from src.agent_messaging import AgentMessage

def test_multiagent_collaboration():
    # Create a single unified agent for all cognition
    agent = SingleUseAgent(agent_id="test_agent")

    # Step 1: Send a research request
    research_msg = AgentMessage(
        sender="test_user",
        receiver="test_agent",
        intent="research_request",
        payload={"user_message": "What is the latest in AI?"},
        metadata={}
    )
    research_response = agent.process_turn(research_msg.payload["user_message"])
    assert research_response is not None

    # Step 2: Send a writing request using the research result (mocked)
    writing_msg = AgentMessage(
        sender="test_user",
        receiver="test_agent",
        intent="writing_request",
        payload={"user_message": "Write a summary about the latest in AI."},
        metadata={}
    )
    writing_response = agent.process_turn(writing_msg.payload["user_message"])
    assert writing_response is not None

    # Step 3: Send a critique request for the writing output (mocked)
    critique_msg = AgentMessage(
        sender="test_user",
        receiver="test_agent",
        intent="critique_request",
        payload={"user_message": "Critique the previous summary."},
        metadata={}
    )
    critique_response = agent.process_turn(critique_msg.payload["user_message"])
    assert critique_response is not None
