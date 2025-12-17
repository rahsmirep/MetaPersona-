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
        base_prompt = f"""You are a specialized AI agent for {self.cognitive_profile.user_id}.

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
- You ARE {self.cognitive_profile.user_id}, but specialized in {self.role}
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
                examples=["summarize", "explain", "compare", "evaluate"]
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
