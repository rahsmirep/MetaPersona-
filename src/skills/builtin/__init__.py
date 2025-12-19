"""
Built-in Skills Package
Core skills that come with MetaPersona.
"""
from .calculator import CalculatorSkill
from .file_ops import FileOpsSkill
from .web_search import WebSearchSkill
from .timezone import TimezoneSkill
from .flight import FlightSkill

__all__ = ["CalculatorSkill", "FileOpsSkill", "WebSearchSkill", "TimezoneSkill", "FlightSkill"]
