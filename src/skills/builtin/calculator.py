"""
Calculator Skill
Performs mathematical calculations.
"""
import math
from typing import Any
from ..base import Skill, SkillMetadata, SkillParameter, SkillResult


class CalculatorSkill(Skill):
    """Mathematical calculator skill."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="calculator",
            description="Performs mathematical calculations and evaluates expressions",
            category="Utilities",
            parameters=[
                SkillParameter(
                    name="expression",
                    type="str",
                    description="Mathematical expression to evaluate (e.g., '2 + 2', 'sqrt(16)', 'sin(3.14)')",
                    required=True
                )
            ],
            returns="The calculated result as a number"
        )
    
    def execute(self, expression: str) -> SkillResult:
        """Evaluate a mathematical expression."""
        try:
            # Safe eval with math functions
            safe_dict = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "log10": math.log10,
                "exp": math.exp,
                "pi": math.pi,
                "e": math.e,
                "__builtins__": {}
            }
            
            result = eval(expression, safe_dict, {})
            
            return SkillResult(
                success=True,
                data=result,
                metadata={"expression": expression}
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Calculation error: {str(e)}"
            )
