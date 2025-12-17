"""
Built-in Skills Package
Core skills that come with MetaPersona.
"""
from .calculator import CalculatorSkill
from .file_ops import FileOpsSkill
from .web_search import WebSearchSkill

__all__ = ["CalculatorSkill", "FileOpsSkill", "WebSearchSkill"]
