"""MetaPersona package initialization."""
from .identity import IdentityLayer
from .cognitive_profile import CognitiveProfile, ProfileManager
from .persona_agent import PersonaAgent, AgentManager
from .memory_loop import MemoryLoop
from .llm_provider import get_llm_provider
from .skills import Skill, SkillRegistry, SkillManager
from .agent_base import BaseAgent, AgentCapability
from .task_result import TaskResult
from .agent_registry import AgentRegistry
from .task_router import TaskRouter, RoutingDecision
from .specialized_agents import ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent

# from .personalized_agents import (
#     PersonalizedResearchAgent,
#     PersonalizedCodeAgent,
#     PersonalizedWriterAgent,
#     PersonalizedGeneralistAgent
# )
from .user_profiling import UserProfilingSystem, UserProfile, SkillPack

__version__ = "2.1.0"
__all__ = [
 #  "IdentityLayer",
 #  "CognitiveProfile",
 #   "ProfileManager",
 #  "PersonaAgent",
 #  "AgentManager",
 #   "MemoryLoop",
 # "get_llm_provider",
 #  "Skill",
 #  "SkillRegistry",
 #  "SkillManager",
 #  "BaseAgent",
 #  "AgentCapability",
 #  "TaskResult",
 #  "AgentRegistry",
 #  "TaskRouter",
 #  "RoutingDecision",
 #  "ResearchAgent",
 #  "CodeAgent",
 #  "WriterAgent",
 #  "GeneralistAgent",
 #  "PersonalizedResearchAgent",
 #  "PersonalizedCodeAgent",
 #  "PersonalizedWriterAgent",
 #  "PersonalizedGeneralistAgent",
 #  "UserProfilingSystem",
 #  "UserProfile",
 #  "SkillPack"
]
