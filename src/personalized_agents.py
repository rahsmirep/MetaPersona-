"""
Personalized Multi-Agents
Specialized agents that act in YOUR style while having different expertise areas.
"""
from typing import Dict, List, Any, Optional
from .agent_base import BaseAgent, AgentCapability, TaskResult
from .cognitive_profile import CognitiveProfile
from .llm_provider import LLMProvider
from .skills.manager import SkillManager
import json


class PersonalizedBaseAgent(BaseAgent):
    """
    Base agent that combines multi-agent capabilities with your personal cognitive profile.
    All specialized agents inherit from this to maintain YOUR style.
    """
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        description: str,
        cognitive_profile: CognitiveProfile,
        llm_provider: LLMProvider,
        skills_manager: Optional[SkillManager] = None
    ):
        super().__init__(agent_id, role, description, llm_provider, skills_manager)
        self.cognitive_profile = cognitive_profile
        
    def get_system_prompt(self) -> str:
        """Build system prompt that includes both role specialization and personal style."""
        base_prompt = f"""You are a specialized AI agent for Persona.

**Your Role:** {self.role}
**Specialization:** {self.description}

**Personal Writing Style (maintain this across all responses):**
- Tone: {self.cognitive_profile.writing_style.tone}
- Vocabulary Level: {self.cognitive_profile.writing_style.vocabulary_level}
- Sentence Structure: {self.cognitive_profile.writing_style.sentence_structure}
- Punctuation Style: {self.cognitive_profile.writing_style.punctuation_style}

**Decision-Making Approach:**
- Style: {self.cognitive_profile.decision_pattern.approach}
- Risk Tolerance: {self.cognitive_profile.decision_pattern.risk_tolerance}

**Your Capabilities:**
"""
        for cap in self.capabilities:
            base_prompt += f"\n- {cap.name}: {cap.description}"
        
        base_prompt += f"""

**Important:** 
- You ARE Persona, but specialized in {self.role}
- Respond in THEIR writing style, not a generic AI style
- Apply your specialized expertise while maintaining their personality
- Think and communicate as they would in your domain of expertise
"""
        return base_prompt


class PersonalizedResearchAgent(PersonalizedBaseAgent):
    """Research agent that conducts research in YOUR style."""
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="research_and_analysis",
                description="Research and analyze information in user's analytical style",
                confidence=0.9,
                examples=["research", "find information", "analyze", "investigate"]
            ),
            AgentCapability(
                name="information_synthesis",
                description="Synthesize findings in user's communication style",
                confidence=0.85,
                examples=["summarize", "synthesize", "combine information"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        task_lower = task.lower()
        
        # Exclude other domains
        if any(kw in task_lower for kw in ["write code", "write a function", "program"]):
            return 0.2
        if any(kw in task_lower for kw in ["write email", "write letter", "draft"]):
            return 0.2
        
        # High confidence for research tasks
        if any(kw in task_lower for kw in ["research", "find information", "search for", "investigate"]):
            return 0.9
        
        # Medium for analysis
        if any(kw in task_lower for kw in ["analyze", "compare", "evaluate", "assess"]):
            return 0.75
        
        return 0.3
    
    def handle_task(self, task: str, context: Optional[Dict[str, Any]] = None, use_skills: bool = True) -> TaskResult:
        """Execute research task."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        response = self.llm_provider.generate(messages, temperature=0.7)
        return TaskResult(success=True, result=response, metadata={"agent_id": self.agent_id})


class PersonalizedCodeAgent(PersonalizedBaseAgent):
    """Coding agent that writes code in YOUR style."""
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="code_development",
                description="Write code following user's coding patterns and preferences",
                confidence=0.95,
                examples=["write code", "create function", "implement", "develop"]
            ),
            AgentCapability(
                name="debugging",
                description="Debug and fix code in user's problem-solving style",
                confidence=0.85,
                examples=["debug", "fix", "error", "issue"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        task_lower = task.lower()
        
        # Exclude writing/research
        if any(kw in task_lower for kw in ["write email", "write article", "write letter", "draft"]):
            return 0.15
        if "research" in task_lower and "code" not in task_lower:
            return 0.2
        
        # Very high for explicit coding
        if any(phrase in task_lower for phrase in ["write code", "write a function", "write a script", "create a program"]):
            return 0.95
        
        # High for languages and technical terms
        languages = ["python", "javascript", "java", "c++", "rust", "go", "typescript"]
        if any(lang in task_lower for lang in languages):
            return 0.9
        
        # Medium for technical terms
        if any(kw in task_lower for kw in ["function", "class", "api", "algorithm", "debug"]):
            return 0.7
        
        return 0.3
    
    def handle_task(self, task: str, context: Optional[Dict[str, Any]] = None, use_skills: bool = True) -> TaskResult:
        """Execute coding task."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        response = self.llm_provider.generate(messages, temperature=0.7)
        return TaskResult(success=True, result=response, metadata={"agent_id": self.agent_id})


class PersonalizedWriterAgent(PersonalizedBaseAgent):
    """Writing agent that creates content in YOUR style."""
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="professional_writing",
                description="Write professional documents in user's voice",
                confidence=0.95,
                examples=["write email", "write letter", "draft memo", "compose message"]
            ),
            AgentCapability(
                name="content_creation",
                description="Create articles and content in user's writing style",
                confidence=0.9,
                examples=["write article", "write blog", "create content"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        task_lower = task.lower()
        
        # Exclude code and research
        if any(kw in task_lower for kw in ["code", "function", "program", "script"]):
            return 0.15
        if "research" in task_lower and not any(kw in task_lower for kw in ["write", "draft", "compose"]):
            return 0.2
        
        # Very high for professional documents
        if any(phrase in task_lower for phrase in ["write email", "write letter", "write memo", "draft email"]):
            return 0.95
        
        # High for content creation
        if any(kw in task_lower for kw in ["article", "blog", "post", "essay", "report"]):
            return 0.9
        
        # Medium for general writing
        if any(kw in task_lower for kw in ["write", "compose", "draft", "create"]):
            return 0.7
        
        return 0.3
    
    def handle_task(self, task: str, context: Optional[Dict[str, Any]] = None, use_skills: bool = True) -> TaskResult:
        """Execute writing task."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        response = self.llm_provider.generate(messages, temperature=0.7)
        return TaskResult(success=True, result=response, metadata={"agent_id": self.agent_id})


class PersonalizedGeneralistAgent(PersonalizedBaseAgent):
    """Generalist agent for conversations in YOUR style."""
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="conversation",
                description="Natural conversation in user's communication style",
                confidence=0.8,
                examples=["chat", "discuss", "explain", "help"]
            ),
            AgentCapability(
                name="general_assistance",
                description="General tasks and questions in user's decision-making style",
                confidence=0.7,
                examples=["help with", "tell me about", "what is", "how to"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Handle general tasks with moderate confidence."""
        task_lower = task.lower()
        
        # Lower confidence for specialized tasks
        specialized_keywords = [
            "research", "search for", "find information",
            "write code", "function", "program",
            "write email", "write letter", "draft"
        ]
        
        if any(kw in task_lower for kw in specialized_keywords):
            return 0.3
        
        # Good for explanations and conversations
        return 0.5
    
    def handle_task(self, task: str, context: Optional[Dict[str, Any]] = None, use_skills: bool = True) -> TaskResult:
        """Execute general task."""
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": task}
        ]
        response = self.llm_provider.generate(messages, temperature=0.7)
        return TaskResult(success=True, result=response, metadata={"agent_id": self.agent_id})


class PersonalizedProfessionAgent(PersonalizedBaseAgent):
    """Professional expert agent that uses profession schema and acts in YOUR professional style."""
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        description: str,
        cognitive_profile: CognitiveProfile,
        llm_provider: LLMProvider,
        profession_schema,
        skills_manager: Optional[SkillManager] = None
    ):
        # Set profession_schema BEFORE calling super().__init__
        # because _define_capabilities() needs it
        self.profession_schema = profession_schema
        
        super().__init__(agent_id, role, description, cognitive_profile, llm_provider, skills_manager)
        
        # Initialize profession reasoning layer
        from .profession import ProfessionReasoningLayer, ParallelSelfAlignment
        self.reasoning = ProfessionReasoningLayer(llm_provider)
        self.alignment = ParallelSelfAlignment()
        
        # Create aligned persona
        self.aligned_persona = self.alignment.create_aligned_persona(
            profession_schema,
            cognitive_profile
        )
    
    def _define_capabilities(self) -> List[AgentCapability]:
        """Capabilities based on profession schema."""
        capabilities = [
            AgentCapability(
                name="professional_expertise",
                description=f"Expert in {self.profession_schema.profession_name} - {self.profession_schema.industry}",
                confidence=0.95,
                examples=[
                    self.profession_schema.profession_name.lower(),
                    self.profession_schema.industry.lower()
                ]
            ),
            AgentCapability(
                name="professional_decisions",
                description=f"Make decisions using {self.profession_schema.profession_name} frameworks and best practices",
                confidence=0.9,
                examples=["decision", "should i", "recommend", "advise"]
            ),
            AgentCapability(
                name="safety_validation",
                description="Validate responses against professional safety rules",
                confidence=0.95,
                examples=["safe", "compliant", "allowed"]
            )
        ]
        
        # Add capabilities for key tools
        if self.profession_schema.tools_equipment.software:
            capabilities.append(
                AgentCapability(
                    name="tools_expertise",
                    description=f"Expert with tools: {', '.join(self.profession_schema.tools_equipment.software[:5])}",
                    confidence=0.85,
                    examples=self.profession_schema.tools_equipment.software[:5]
                )
            )
        
        return capabilities
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if task is related to this profession."""
        task_lower = task.lower()
        
        # Check profession name and industry
        if self.profession_schema.profession_name.lower() in task_lower:
            return 0.95
        if self.profession_schema.industry.lower() in task_lower:
            return 0.9
        
        # Check tools
        for tool in self.profession_schema.tools_equipment.software[:10]:
            if tool.lower() in task_lower:
                return 0.85
        
        # Check terminology/jargon
        for term in list(self.profession_schema.terminology.jargon.keys())[:20]:
            if term.lower() in task_lower:
                return 0.8
        
        for acronym in list(self.profession_schema.terminology.acronyms.keys())[:20]:
            if acronym.lower() in task_lower:
                return 0.8
        
        # Check responsibilities keywords
        for resp in self.profession_schema.role_definition.primary_responsibilities[:10]:
            # Extract key nouns/verbs from responsibilities
            resp_words = set(resp.lower().split())
            task_words = set(task_lower.split())
            if len(resp_words & task_words) >= 2:  # At least 2 matching words
                return 0.75
        
        # Check decision-making keywords
        decision_keywords = ["should i", "recommend", "advise", "best practice", "how to"]
        if any(kw in task_lower for kw in decision_keywords):
            return 0.6
        
        return 0.3
    
    def get_system_prompt(self) -> str:
        """Build system prompt with profession context and aligned persona."""
        # Use aligned persona system prompt
        aligned_prompt = self.alignment.generate_system_prompt(
            self.aligned_persona
        )
        
        # Add role context
        profession_context = f"""

**Your Specialized Role:** {self.role}
**Professional Identity:** {self.profession_schema.profession_name} in {self.profession_schema.industry}
**Work Environment:** {self.profession_schema.environment.work_setting.value}, {self.profession_schema.environment.team_structure.value}

**Your Capabilities:**
"""
        for cap in self.capabilities:
            profession_context += f"\n- {cap.name}: {cap.description}"
        
        return aligned_prompt + profession_context
    
    def process_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> TaskResult:
        """Process task with profession-aware context enhancement."""
        # Identify knowledge gaps
        gaps = self.profession_schema.identify_knowledge_gaps(task)
        
        # Build context from conversation history if available
        history = context.get("conversation_history", []) if context else []
        
        # Enhance prompt with profession context
        enhanced_prompt = self.reasoning.enhance_prompt(
            task,
            self.profession_schema,
            self.cognitive_profile,
            history
        )
        
        # Extract decision factors if applicable
        decision_factors = None
        if any(kw in task.lower() for kw in ["should", "recommend", "decide", "choose"]):
            decision_factors = self.reasoning.extract_decision_factors(
                task,
                self.profession_schema
            )
        
        # Generate response
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": enhanced_prompt}
        ]
        
        response = self.llm_provider.generate(messages, temperature=0.7)
        
        # Validate response against safety rules
        is_safe, violations = self.reasoning.validate_response(
            response,
            self.profession_schema
        )
        
        if not is_safe:
            warning = f"\n\n⚠️ **Safety Warning:** This response may violate professional safety rules:\n"
            for violation in violations:
                warning += f"- {violation}\n"
            response += warning
        
        # Build metadata
        metadata = {
            "agent_id": self.agent_id,
            "agent_role": self.role,
            "profession": self.profession_schema.profession_name,
            "knowledge_gaps": gaps,
            "safety_validated": is_safe,
            "aligned_persona": True,
            "confidence": 0.9
        }
        
        if decision_factors:
            metadata["decision_factors"] = decision_factors
        
        return TaskResult(
            success=True,
            result=response,
            metadata=metadata
        )
    
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute task with profession context. Alias for process_task."""
        return self.process_task(task, context)
