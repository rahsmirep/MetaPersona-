import pytest
import time
from src.router import Router
from src.shared_memory import SharedBlackboard
from src.agent_messaging import AgentMessage
from src.agents.research_agent import ResearchAgent
from src.agents.writing_agent import WritingAgent
from src.agents.planning_agent import PlanningAgent
from src.agents.critique_agent import CritiqueAgent
from src.agents.persona_alignment_agent import PersonaAlignmentAgent


class DummyLLM:
    def generate(self, messages, temperature=0.3):
        # Simple mock for all agents
        if isinstance(messages, list) and messages:
            return f"LLM output for: {messages[-1]['content']}"
        return "LLM output"

# Minimal mock schema with get_context_summary
class MockSchema:
    def get_context_summary(self, n):
        return "Mock schema summary"

def test_multiagent_collaboration():
    router = Router()
    shared_memory = SharedBlackboard()
    llm = DummyLLM()

    # Instantiate three specialized agents
    research_agent = ResearchAgent("research_agent", router, shared_memory, llm_provider=llm)
    # Patch WritingAgent and CritiqueAgent to use mock schema
    writing_agent = WritingAgent("writing_agent", router, shared_memory, llm_provider=llm)
    writing_agent.schema = MockSchema()
    orig_handle_message = writing_agent.handle_message
    def handle_message_with_schema(message):
        # Patch to pass schema to reflection
        if message.intent == 'writing_request':
            structure = message.payload.get('structure')
            content = writing_agent._compose_text(structure)
            refined = content
            if writing_agent.reflection:
                eval_result = writing_agent.reflection.evaluate_response(content, writing_agent.schema)
                if eval_result.get('needs_refinement'):
                    refined = writing_agent.reflection.refine_response(content, writing_agent.schema, eval_result)
            writing_agent.shared_memory.write(f"writing:{structure}", refined, writing_agent.agent_id, metadata={"source_agent": writing_agent.agent_id})
            response = AgentMessage(
                sender=writing_agent.agent_id,
                receiver=message.sender,
                intent='writing_response',
                payload={'output': refined},
                metadata={'in_response_to': message.metadata.get('trace_id'), 'timestamp': time.time()}
            )
            writing_agent._log_action('responded', response)
            return response
        return orig_handle_message(message)
    writing_agent.handle_message = handle_message_with_schema
    router.register_agent("writing_agent", writing_agent.handle_message)

    critique_agent = CritiqueAgent("critique_agent", router, shared_memory, llm_provider=llm)
    critique_agent.schema = MockSchema()
    orig_critique_handle = critique_agent.handle_message
    def handle_message_with_schema_critique(message):
        if message.intent == 'critique_request':
            output = message.payload.get('output')
            if critique_agent.reflection:
                eval_result = critique_agent.reflection.evaluate_response(output, critique_agent.schema)
                critique = {
                    'clarity': eval_result.get('clarity', 0),
                    'accuracy': eval_result.get('accuracy', 0),
                    'alignment': eval_result.get('alignment', 0),
                    'completeness': eval_result.get('completeness', 0),
                    'needs_refinement': eval_result.get('needs_refinement', False),
                    'raw': eval_result
                }
            else:
                critique = {'clarity': 4, 'accuracy': 4, 'alignment': 4, 'completeness': 4, 'needs_refinement': False, 'raw': 'Mock critique'}
            critique_agent.shared_memory.write(f"critique:{hash(output)}", critique, critique_agent.agent_id, metadata={"source_agent": critique_agent.agent_id})
            response = AgentMessage(
                sender=critique_agent.agent_id,
                receiver=message.sender,
                intent='critique_response',
                payload={'critique': critique},
                metadata={'in_response_to': message.metadata.get('trace_id'), 'timestamp': time.time()}
            )
            critique_agent._log_action('responded', response)
            return response
        return orig_critique_handle(message)
    critique_agent.handle_message = handle_message_with_schema_critique
    router.register_agent("critique_agent", critique_agent.handle_message)

    # Step 1: Send a research request
    research_msg = AgentMessage(
        sender="test_user",
        receiver="research_agent",
        intent="research_request",
        payload={"query": "What is the latest in AI?"},
        metadata={}
    )
    research_response = router.route_message(research_msg)
    assert research_response is not None
    assert research_response.intent == "research_response"
    research_result = research_response.payload["results"][0]["result"]
    # Step 2: Send a writing request using the research result
    writing_msg = AgentMessage(
        sender="test_user",
        receiver="writing_agent",
        intent="writing_request",
        payload={"structure": research_result},
        metadata={}
    )
    writing_response = router.route_message(writing_msg)
    assert writing_response is not None
    assert writing_response.intent == "writing_response"
    writing_output = writing_response.payload["output"]
    # Step 3: Send a critique request for the writing output
    critique_msg = AgentMessage(
        sender="test_user",
        receiver="critique_agent",
        intent="critique_request",
        payload={"output": writing_output},
        metadata={}
    )
    critique_response = router.route_message(critique_msg)
    assert critique_response is not None
    assert critique_response.intent == "critique_response"
    critique = critique_response.payload["critique"]
    assert "clarity" in critique and "accuracy" in critique
    # Check shared memory for traceability
    assert shared_memory.read("research:What is the latest in AI?") is not None
    assert any("writing:" in k for k in shared_memory._entries)
    assert any("critique:" in k for k in shared_memory._entries)
