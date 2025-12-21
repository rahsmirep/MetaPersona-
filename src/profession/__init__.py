"""
Profession Understanding Package
Universal system for understanding any profession
"""

from .schema import (
    ProfessionSchema,
    RoleDefinition,
    DailyTasks,
    ToolsEquipment,
    Environment,
    Constraints,
    Terminology,
    DecisionPatterns,
    SafetyRules,
    SkillHierarchy,
    EdgeCases,
    KnowledgeConfidence,
    WorkSetting,
    TeamStructure,
    PaceLevel,
    AutonomyLevel,
    RiskTolerance
)

from .onboarding_interpreter import OnboardingInterpreter
from .knowledge_expansion import KnowledgeExpansionLayer
from .reasoning import ProfessionReasoningLayer, ParallelSelfAlignment
from .interactive_onboarding import InteractiveOnboarding
from .profession_system import UniversalProfessionSystem

__all__ = [
    # Main system
    "UniversalProfessionSystem",
    
    # Core schema
    "ProfessionSchema",
    "RoleDefinition",
    "DailyTasks",
    "ToolsEquipment",
    "Environment",
    "Constraints",
    "Terminology",
    "DecisionPatterns",
    "SafetyRules",
    "SkillHierarchy",
    "EdgeCases",
    "KnowledgeConfidence",
    
    # Enums
    "WorkSetting",
    "TeamStructure",
    "PaceLevel",
    "AutonomyLevel",
    "RiskTolerance",
    
    # Components
    "OnboardingInterpreter",
    "KnowledgeExpansionLayer",
    "ProfessionReasoningLayer",
    "ParallelSelfAlignment",
]
