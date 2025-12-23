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

class PersonalizedAgent(AgentMessagingProtocol):
    def _reasoning_pipeline(self, user_query: str, conversation_history=None) -> str:
        """
        Unified generate → reflect → refine reasoning pipeline.
        """
        from .profession.reasoning import ProfessionReasoningLayer
        from .profession.reflection_engine import ReflectionEngine
        reasoning_layer = ProfessionReasoningLayer(self.llm_provider)
        reflection_engine = ReflectionEngine(self.llm_provider)

        # Step 1: Generate initial answer
        initial_answer = reasoning_layer.enhance_prompt(
            user_query,
            self.profession_schema,
            self.cognitive_profile,
            conversation_history or []
        )

        # Step 2: Reflect on the answer
        eval_result = reflection_engine.evaluate_response(initial_answer, self.profession_schema)

        # Step 3: Refine if necessary
        if eval_result.get("needs_refinement"):
            final_answer = reflection_engine.refine_response(initial_answer, self.profession_schema, eval_result)
            return final_answer
        else:
            return initial_answer

    def onboard_from_text(self, raw_text: str, user_id: str):
        """
        Onboard or update profession schema from raw onboarding text, including knowledge expansion.
        """
        interpreter = ProfessionSchemaInterpreter(self.llm_provider)
        schema = interpreter.extract_schema(raw_text, user_id)

        # Knowledge Expansion Layer integration
        google_api_key = os.getenv("GOOGLE_API_KEY", "dummy")
        google_cse_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "dummy")
        knowledge_expander = KnowledgeExpansionLayer(
            llm_provider=self.llm_provider,
            google_api_key=google_api_key,
            google_cse_id=google_cse_id
        )
        enriched_schema = knowledge_expander.expand_schema(schema)
        self.profession_schema = enriched_schema

        self.aligned_persona = self.alignment.create_aligned_persona(
            self.profession_schema,
            self.cognitive_profile
        )
    def __init__(
        self,
        user_id: str,
        profession_schema: ProfessionSchema,
        cognitive_profile: CognitiveProfile,
        llm_provider: Any,
        router: Router = None
    ):
        # Validate input types
        if not isinstance(profession_schema, ProfessionSchema):
            raise TypeError("profession_schema must be a ProfessionSchema instance")
        if not isinstance(cognitive_profile, CognitiveProfile):
            raise TypeError("cognitive_profile must be a CognitiveProfile instance")

        # Optionally, check for required attributes
        required_prof_attrs = [
            'profession_name', 'industry', 'decision_patterns', 'tools_equipment',
            'skill_hierarchy', 'constraints', 'environment', 'role_definition', 'safety_rules', 'terminology'
        ]
        for attr in required_prof_attrs:
            if not hasattr(profession_schema, attr):
                raise AttributeError(f"ProfessionSchema missing required attribute: {attr}")

        required_cog_attrs = ['user_id', 'writing_style', 'decision_pattern']
        for attr in required_cog_attrs:
            if not hasattr(cognitive_profile, attr):
                raise AttributeError(f"CognitiveProfile missing required attribute: {attr}")

        self.user_id = user_id
        self.profession_schema = profession_schema
        self.cognitive_profile = cognitive_profile
        self.llm_provider = llm_provider
        self.router = router

        # Alignment
        self.alignment = ParallelSelfAlignment()
        # Create aligned persona
        self.aligned_persona = self.alignment.create_aligned_persona(
            self.profession_schema,
            self.cognitive_profile
        )

        # Workflow engine for multi-step reasoning
        self.workflow_engine = WorkflowEngine(self, llm_provider, router=router)

        # Register with router if provided
        if self.router:
            self.router.register_agent(self.user_id, self.handle_message)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        """
        Handle incoming agent-to-agent messages. Supports request, response, delegate, status_update.
        Prevent infinite delegation recursion by checking trace_id and a max delegation depth.
        """
        # Prevent infinite recursion: check for delegation depth in metadata
        max_delegation_depth = 5
        depth = message.metadata.get("delegation_depth", 0)
        if depth > max_delegation_depth:
            return AgentMessage(
                sender=self.user_id,
                receiver=message.sender,
                intent="error",
                payload={"error": "Delegation recursion limit exceeded."},
                metadata={"in_response_to": message.metadata.get("trace_id")}
            )
        # Prevent self-delegation loop
        if message.sender == self.user_id and message.intent == "request":
            return AgentMessage(
                sender=self.user_id,
                receiver=message.sender,
                intent="error",
                payload={"error": "Self-delegation detected."},
                metadata={"in_response_to": message.metadata.get("trace_id")}
            )
        if message.intent == "request":
            # Treat as a workflow request
            # Pass message.metadata as context to track delegation_depth
            context = dict(message.metadata) if message.metadata else {}
            result = self.run_workflow(message.payload.get("user_request", ""), conversation_history=message.payload.get("history"), context=context)
            return AgentMessage(
                sender=self.user_id,
                receiver=message.sender,
                intent="response",
                payload={"result": result},
                metadata={"in_response_to": message.metadata.get("trace_id")}
            )
        elif message.intent == "delegate":
            # Delegate a subtask to another agent (if router is present)
            if self.router:
                delegate_to = message.payload.get("delegate_to")
                subtask = message.payload.get("subtask")
                # Increment delegation depth
                new_metadata = dict(message.metadata)
                new_metadata["delegation_depth"] = depth + 1
                response = self.router.delegate_task(
                    from_agent=self.user_id,
                    to_agent=delegate_to,
                    intent="request",
                    payload={"user_request": subtask},
                    metadata={"delegated_by": self.user_id, "parent_trace_id": message.metadata.get("trace_id"), "delegation_depth": depth + 1}
                )
                return AgentMessage(
                    sender=self.user_id,
                    receiver=message.sender,
                    intent="response",
                    payload={"delegation_result": response.payload if response else None},
                    metadata={"in_response_to": message.metadata.get("trace_id")}
                )
            else:
                return AgentMessage(
                    sender=self.user_id,
                    receiver=message.sender,
                    intent="response",
                    payload={"error": "No router available for delegation."},
                    metadata={"in_response_to": message.metadata.get("trace_id")}
                )
        elif message.intent == "status_update":
            # Accept and acknowledge status updates
            return AgentMessage(
                sender=self.user_id,
                receiver=message.sender,
                intent="acknowledge",
                payload={"status": "received"},
                metadata={"in_response_to": message.metadata.get("trace_id")}
            )
        else:
            # Unknown intent
            return AgentMessage(
                sender=self.user_id,
                receiver=message.sender,
                intent="error",
                payload={"error": f"Unknown intent: {message.intent}"},
                metadata={"in_response_to": message.metadata.get("trace_id")}
            )
    def run_workflow(self, user_request: str, conversation_history=None, context=None) -> str:
        """
        Use WorkflowEngine to plan, execute, and assemble a multi-step reasoning workflow.
        """
        # Step 1: Plan
        steps = self.workflow_engine.plan_generation(user_request)
        # Step 2: Execute steps (with reflection after each)
        context = context or {}
        context.setdefault("history", conversation_history or [])
        step_results = self.workflow_engine.step_execution(steps, context=context)
        # Step 3: Assemble final output
        final_output = self.workflow_engine.assemble_final_output(step_results)
        return final_output

    def get_persona_config(self) -> Dict[str, Any]:
        return self.aligned_persona

    def generate_prompt(self, user_query: str, conversation_history=None) -> str:
        """
        Use the unified reasoning pipeline for single-step reasoning.
        """
        return self._reasoning_pipeline(user_query, conversation_history)

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