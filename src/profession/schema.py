"""
Universal Profession Schema
Core data structure for representing any profession
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import json
from pathlib import Path


class WorkSetting(Enum):
    OFFICE = "office"
    REMOTE = "remote"
    HYBRID = "hybrid"
    FIELD = "field"
    LABORATORY = "laboratory"
    CLINICAL = "clinical"
    MOBILE = "mobile"


class TeamStructure(Enum):
    SOLO = "solo"
    SMALL_TEAM = "small_team"
    LARGE_TEAM = "large_team"
    MATRIX = "matrix"
    CROSS_FUNCTIONAL = "cross_functional"


class PaceLevel(Enum):
    FAST = "fast"
    MODERATE = "moderate"
    METHODICAL = "methodical"
    VARIABLE = "variable"


class AutonomyLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MIXED = "mixed"


class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    CONTEXT_DEPENDENT = "context_dependent"


class ConfidenceLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class RoleDefinition:
    """Core responsibilities and success metrics of the profession."""
    primary_responsibilities: List[str] = field(default_factory=list)
    secondary_responsibilities: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    common_challenges: List[str] = field(default_factory=list)


@dataclass
class DailyTasks:
    """Routine, periodic, and situational tasks."""
    routine: List[str] = field(default_factory=list)  # Daily activities
    periodic: Dict[str, List[str]] = field(default_factory=dict)  # weekly/monthly/yearly
    situational: List[Dict[str, Any]] = field(default_factory=list)  # Event-triggered


@dataclass
class ToolsEquipment:
    """Tools, software, hardware, and methodologies used."""
    software: List[str] = field(default_factory=list)
    hardware: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    methodologies: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)


@dataclass
class Environment:
    """Work environment characteristics."""
    work_setting: WorkSetting = WorkSetting.OFFICE
    team_structure: TeamStructure = TeamStructure.SMALL_TEAM
    pace: PaceLevel = PaceLevel.MODERATE
    autonomy_level: AutonomyLevel = AutonomyLevel.MEDIUM
    physical_demands: List[str] = field(default_factory=list)
    travel_requirements: Optional[str] = None


@dataclass
class Constraints:
    """Limitations and considerations."""
    regulatory: List[str] = field(default_factory=list)
    time_sensitive: List[str] = field(default_factory=list)
    resource_limitations: List[str] = field(default_factory=list)
    ethical_considerations: List[str] = field(default_factory=list)
    legal_requirements: List[str] = field(default_factory=list)


@dataclass
class Terminology:
    """Professional vocabulary."""
    jargon: Dict[str, str] = field(default_factory=dict)  # term: definition
    acronyms: Dict[str, str] = field(default_factory=dict)  # acronym: expansion
    concepts: Dict[str, str] = field(default_factory=dict)  # concept: explanation


@dataclass
class DecisionPatterns:
    """How decisions are made in this profession."""
    common_decisions: List[str] = field(default_factory=list)
    decision_frameworks: List[str] = field(default_factory=list)
    risk_tolerance: RiskTolerance = RiskTolerance.MODERATE
    information_sources: List[str] = field(default_factory=list)
    escalation_criteria: List[str] = field(default_factory=list)


@dataclass
class SafetyRules:
    """Critical safety and compliance rules."""
    critical: List[str] = field(default_factory=list)  # Must never violate
    important: List[str] = field(default_factory=list)  # Should avoid
    best_practices: List[str] = field(default_factory=list)  # Recommended
    emergency_protocols: List[str] = field(default_factory=list)


@dataclass
class SkillHierarchy:
    """Skill progression in the profession."""
    foundational: List[str] = field(default_factory=list)
    intermediate: List[str] = field(default_factory=list)
    advanced: List[str] = field(default_factory=list)
    mastery: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)


@dataclass
class EdgeCases:
    """Uncommon scenarios and exceptions."""
    scenarios: List[Dict[str, str]] = field(default_factory=list)  # scenario: response
    exceptions: List[str] = field(default_factory=list)
    escalation_triggers: List[str] = field(default_factory=list)


@dataclass
class KnowledgeConfidence:
    """Confidence levels for different areas of the schema."""
    high_confidence_areas: List[str] = field(default_factory=list)
    medium_confidence_areas: List[str] = field(default_factory=list)
    needs_expansion: List[str] = field(default_factory=list)


@dataclass
class ProfessionSchema:
    """Universal schema for representing any profession."""
    profession_id: str
    profession_name: str
    industry: str
    last_updated: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    # Core components
    role_definition: RoleDefinition = field(default_factory=RoleDefinition)
    daily_tasks: DailyTasks = field(default_factory=DailyTasks)
    tools_equipment: ToolsEquipment = field(default_factory=ToolsEquipment)
    environment: Environment = field(default_factory=Environment)
    constraints: Constraints = field(default_factory=Constraints)
    terminology: Terminology = field(default_factory=Terminology)
    decision_patterns: DecisionPatterns = field(default_factory=DecisionPatterns)
    safety_rules: SafetyRules = field(default_factory=SafetyRules)
    skill_hierarchy: SkillHierarchy = field(default_factory=SkillHierarchy)
    edge_cases: EdgeCases = field(default_factory=EdgeCases)
    knowledge_confidence: KnowledgeConfidence = field(default_factory=KnowledgeConfidence)
    
    # Metadata
    data_sources: List[str] = field(default_factory=list)
    expansion_history: List[Dict[str, Any]] = field(default_factory=list)
    user_customizations: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        def convert_value(val):
            if isinstance(val, Enum):
                return val.value
            elif isinstance(val, datetime):
                return val.isoformat()
            elif hasattr(val, '__dict__'):
                return {k: convert_value(v) for k, v in val.__dict__.items()}
            elif isinstance(val, list):
                return [convert_value(item) for item in val]
            elif isinstance(val, dict):
                return {k: convert_value(v) for k, v in val.items()}
            return val
        
        return convert_value(self.__dict__)
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filepath: Path):
        """Save schema to file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProfessionSchema':
        """Load from dictionary."""
        # Convert enum strings back to enums
        if 'environment' in data and isinstance(data['environment'], dict):
            env = data['environment']
            if 'work_setting' in env and isinstance(env['work_setting'], str):
                env['work_setting'] = WorkSetting(env['work_setting'])
            if 'team_structure' in env and isinstance(env['team_structure'], str):
                env['team_structure'] = TeamStructure(env['team_structure'])
            if 'pace' in env and isinstance(env['pace'], str):
                env['pace'] = PaceLevel(env['pace'])
            if 'autonomy_level' in env and isinstance(env['autonomy_level'], str):
                env['autonomy_level'] = AutonomyLevel(env['autonomy_level'])
            data['environment'] = Environment(**env)
        
        if 'decision_patterns' in data and isinstance(data['decision_patterns'], dict):
            dp = data['decision_patterns']
            if 'risk_tolerance' in dp and isinstance(dp['risk_tolerance'], str):
                dp['risk_tolerance'] = RiskTolerance(dp['risk_tolerance'])
            data['decision_patterns'] = DecisionPatterns(**dp)
        
        # Convert ISO datetime strings back to datetime
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Reconstruct nested dataclasses
        for field_name in ['role_definition', 'daily_tasks', 'tools_equipment', 
                          'constraints', 'terminology', 'safety_rules', 
                          'skill_hierarchy', 'edge_cases', 'knowledge_confidence']:
            if field_name in data and isinstance(data[field_name], dict):
                field_class = globals()[field_name.title().replace('_', '')]
                data[field_name] = field_class(**data[field_name])
        
        return cls(**data)
    
    @classmethod
    def load(cls, filepath: Path) -> 'ProfessionSchema':
        """Load schema from file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def get_context_summary(self, max_length: int = 1000) -> str:
        """Get a concise summary for LLM context injection."""
        summary = f"Profession: {self.profession_name}\n\n"
        
        if self.role_definition.primary_responsibilities:
            summary += f"Key Responsibilities:\n"
            for resp in self.role_definition.primary_responsibilities[:3]:
                summary += f"- {resp}\n"
            summary += "\n"
        
        if self.tools_equipment.software or self.tools_equipment.platforms:
            tools = self.tools_equipment.software[:3] + self.tools_equipment.platforms[:3]
            summary += f"Common Tools: {', '.join(tools)}\n\n"
        
        if self.decision_patterns.decision_frameworks:
            summary += f"Decision Frameworks: {', '.join(self.decision_patterns.decision_frameworks[:2])}\n\n"
        
        if self.safety_rules.critical:
            summary += f"Critical Rules:\n"
            for rule in self.safety_rules.critical[:3]:
                summary += f"- {rule}\n"
        
        # Truncate if too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary
    
    def identify_knowledge_gaps(self, query: str) -> List[str]:
        """Identify areas needing expansion based on a query."""
        gaps = []
        query_lower = query.lower()
        
        # Check if query involves areas marked as needing expansion
        for area in self.knowledge_confidence.needs_expansion:
            if area.lower() in query_lower:
                gaps.append(area)
        
        # Check for unknown terminology
        words = query_lower.split()
        for word in words:
            if word not in self.terminology.jargon and \
               word not in self.terminology.acronyms and \
               len(word) > 3:  # Skip short words
                gaps.append(f"terminology: {word}")
        
        return gaps
