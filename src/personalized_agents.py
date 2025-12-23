from typing import Any, Dict
from .profession.schema import ProfessionSchema
from .profession.profession_schema_interpreter import ProfessionSchemaInterpreter
from .profession.knowledge_expansion import KnowledgeExpansionLayer
import os
from .cognitive_profile import CognitiveProfile
from .profession.reasoning import ParallelSelfAlignment
from .profession.workflow_engine import WorkflowEngine
from src.agent_messaging import AgentMessagingProtocol, AgentMessage
from src.router import Router


# Unified MetaPersona agent: all cognition is routed through SingleUseAgent.process_turn(message)
from src.single_use_agent import SingleUseAgent
from src.agent_messaging import AgentMessage

class PersonalizedAgent(AgentMessagingProtocol):
    def __init__(self, agent_id: str, initial_mode: str = 'greeting'):
        self.agent_id = agent_id
        self._single_use_agent = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        # All cognition is unified through SingleUseAgent
        result = self._single_use_agent.process_turn(message.payload.get('user_message', ''))
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            intent='response',
            payload={'result': result},
            metadata={}
        )

    def get_persona_config(self) -> Dict[str, Any]:
        # Optionally return config from SingleUseAgent or static config
        return {'agent_id': self.agent_id, 'mode': self._single_use_agent.get_mode()}

    def generate_prompt(self, user_query: str, conversation_history=None) -> str:
        # Route prompt through unified cognition
        return self._single_use_agent.process_turn(user_query)

# Example usage (for testing, remove in production)
if __name__ == "__main__":
    # You must construct ProfessionSchema and CognitiveProfile with all required fields
    # Here is a minimal mockup for demonstration:
    class MockDecisionPatterns:
        decision_frameworks = ["framework1", "framework2"]
        risk_tolerance = type("RiskTolerance", (), {"value": "moderate"})()
        information_sources = ["source1", "source2"]

    class MockToolsEquipment:
        software = ["ToolA"]
        platforms = ["PlatformA"]
        methodologies = ["MethodA"]

    class MockSkillHierarchy:
        advanced = ["SkillA", "SkillB"]

    class MockConstraints:
        regulatory = ["RegulationA"]
        ethical_considerations = ["EthicsA"]
        time_sensitive = ["TimeA"]

    class MockEnvironment:
        autonomy_level = type("AutonomyLevel", (), {"value": "high"})()
        team_structure = type("TeamStructure", (), {"value": "collaborative"})()
        pace = type("Pace", (), {"value": "fast"})()
        work_setting = type("WorkSetting", (), {"value": "remote"})()

    class MockRoleDefinition:
        primary_responsibilities = ["ResponsibilityA"]

    class MockSafetyRules:
        critical = ["Never do X"]
        important = ["Avoid Y"]

    class MockTerminology:
        jargon = {"termA": "definitionA"}

    class MockWritingStyle:
        tone = "formal"
        vocabulary_level = "advanced"
        sentence_structure = "complex"

    class MockDecisionPattern:
        approach = "analytical"
        risk_tolerance = "moderate"

    profession_schema = ProfessionSchema(
        profession_name="Engineer",
        industry="Tech",
        decision_patterns=MockDecisionPatterns(),
        tools_equipment=MockToolsEquipment(),
        skill_hierarchy=MockSkillHierarchy(),
        constraints=MockConstraints(),
        environment=MockEnvironment(),
        role_definition=MockRoleDefinition(),
        safety_rules=MockSafetyRules(),
        terminology=MockTerminology()
    )

    cognitive_profile = CognitiveProfile(
        user_id="user123",
        writing_style=MockWritingStyle(),
        decision_pattern=MockDecisionPattern()
    )

    class DummyLLM:
        def generate(self, messages, temperature=0.3):
            return '{"decision_type": "technical", "urgency": "immediate", "risk_level": "low", "stakeholders": ["team"], "constraints": ["budget"], "key_considerations": ["timeline"]}'

    agent = PersonalizedAgent(
        user_id="agent1",
        profession_schema=profession_schema,
        cognitive_profile=cognitive_profile,  # use the mock defined above
        llm_provider=DummyLLM()               # use the mock defined above
    )
    print(agent.get_persona_config())

class PersonalizedResearchAgent:
    """Minimal stub for PersonalizedResearchAgent to unblock chat interface."""
    def __init__(self, *args, **kwargs):
        self.agent_id = "research_agent"
        self.role = "research"
    def handle_message(self, message):
        # Simple echo for demonstration
        return f"[PersonalizedResearchAgent] Echo: {message}"

class PersonalizedCodeAgent:
    """Minimal stub for PersonalizedCodeAgent to unblock chat interface."""
    def __init__(self, *args, **kwargs):
        self.agent_id = "code_agent"
        self.role = "code"
    def handle_message(self, message):
        # Simple echo for demonstration
        return f"[PersonalizedCodeAgent] Echo: {message}"

class PersonalizedWriterAgent:
    """Minimal stub for PersonalizedWriterAgent to unblock chat interface."""
    def __init__(self, *args, **kwargs):
        self.agent_id = "writer_agent"
        self.role = "writer"
    def handle_message(self, message):
        return f"[PersonalizedWriterAgent] Echo: {message}"

class PersonalizedPlannerAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "planner_agent"
        self.role = "planner"
    def handle_message(self, message):
        return f"[PersonalizedPlannerAgent] Echo: {message}"

class PersonalizedCriticAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "critic_agent"
        self.role = "critic"
    def handle_message(self, message):
        return f"[PersonalizedCriticAgent] Echo: {message}"

class PersonalizedAnalystAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "analyst_agent"
        self.role = "analyst"
    def handle_message(self, message):
        return f"[PersonalizedAnalystAgent] Echo: {message}"

class PersonalizedDesignerAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "designer_agent"
        self.role = "designer"
    def handle_message(self, message):
        return f"[PersonalizedDesignerAgent] Echo: {message}"

class PersonalizedGeneralistAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "generalist_agent"
        self.role = "generalist"
    def handle_message(self, message):
        return f"[PersonalizedGeneralistAgent] Echo: {message}"

class PersonalizedSupportAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "support_agent"
        self.role = "support"
    def handle_message(self, message):
        return f"[PersonalizedSupportAgent] Echo: {message}"

class PersonalizedHelperAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "helper_agent"
        self.role = "helper"
    def handle_message(self, message):
        return f"[PersonalizedHelperAgent] Echo: {message}"

class PersonalizedResponderAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "responder_agent"
        self.role = "responder"
    def handle_message(self, message):
        return f"[PersonalizedResponderAgent] Echo: {message}"

class PersonalizedAdvisorAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "advisor_agent"
        self.role = "advisor"
    def handle_message(self, message):
        return f"[PersonalizedAdvisorAgent] Echo: {message}"

class PersonalizedSpecialistAgent:
    def __init__(self, *args, **kwargs):
        self.agent_id = "specialist_agent"
        self.role = "specialist"
    def handle_message(self, message):
        return f"[PersonalizedSpecialistAgent] Echo: {message}"