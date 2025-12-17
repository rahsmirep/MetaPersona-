"""
Base Skill System
Defines the skill interface and registry.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SkillParameter(BaseModel):
    """Parameter definition for a skill."""
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class SkillMetadata(BaseModel):
    """Metadata describing a skill."""
    name: str
    description: str
    category: str
    version: str = "1.0.0"
    parameters: List[SkillParameter] = Field(default_factory=list)
    returns: str = "Result of the skill execution"


class SkillResult(BaseModel):
    """Result from skill execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Skill(ABC):
    """Base class for all skills."""
    
    def __init__(self):
        self._metadata = self.get_metadata()
    
    @abstractmethod
    def get_metadata(self) -> SkillMetadata:
        """Return skill metadata."""
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> SkillResult:
        """Execute the skill with given parameters."""
        pass
    
    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate parameters against metadata."""
        for param in self._metadata.parameters:
            if param.required and param.name not in params:
                return False
        return True
    
    @property
    def metadata(self) -> SkillMetadata:
        """Get skill metadata."""
        return self._metadata
    
    def __repr__(self) -> str:
        return f"<Skill: {self._metadata.name}>"


class SkillRegistry:
    """Registry for managing available skills."""
    
    def __init__(self):
        self._skills: Dict[str, Skill] = {}
    
    def register(self, skill: Skill) -> None:
        """Register a skill."""
        name = skill.metadata.name
        if name in self._skills:
            print(f"⚠️  Skill '{name}' already registered, overwriting...")
        self._skills[name] = skill
        print(f"✓ Registered skill: {name}")
    
    def unregister(self, skill_name: str) -> bool:
        """Unregister a skill."""
        if skill_name in self._skills:
            del self._skills[skill_name]
            return True
        return False
    
    def get(self, skill_name: str) -> Optional[Skill]:
        """Get a skill by name."""
        return self._skills.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """List all registered skill names."""
        return list(self._skills.keys())
    
    def get_all(self) -> Dict[str, Skill]:
        """Get all registered skills."""
        return self._skills.copy()
    
    def get_by_category(self, category: str) -> List[Skill]:
        """Get all skills in a category."""
        return [
            skill for skill in self._skills.values()
            if skill.metadata.category == category
        ]
    
    def search(self, query: str) -> List[Skill]:
        """Search skills by name or description."""
        query_lower = query.lower()
        return [
            skill for skill in self._skills.values()
            if query_lower in skill.metadata.name.lower() or
               query_lower in skill.metadata.description.lower()
        ]


# Global skill registry
_global_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return _global_registry
