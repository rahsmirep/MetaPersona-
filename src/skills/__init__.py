"""
MetaPersona Skills System
Plugin architecture for extensible agent capabilities.
"""
from .base import Skill, SkillRegistry
from .manager import SkillManager

__all__ = ["Skill", "SkillRegistry", "SkillManager"]
