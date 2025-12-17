"""
Skill Manager
Handles skill execution, chaining, and coordination.
"""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from .base import Skill, SkillResult, SkillRegistry, get_registry


class SkillManager:
    """Manages skill execution and coordination."""
    
    def __init__(self, registry: Optional[SkillRegistry] = None):
        self.registry = registry or get_registry()
        self.execution_history: List[Dict[str, Any]] = []
    
    def execute_skill(self, skill_name: str, **parameters) -> SkillResult:
        """Execute a single skill."""
        skill = self.registry.get(skill_name)
        
        if not skill:
            return SkillResult(
                success=False,
                error=f"Skill '{skill_name}' not found"
            )
        
        # Validate parameters
        if not skill.validate_parameters(parameters):
            return SkillResult(
                success=False,
                error=f"Invalid parameters for skill '{skill_name}'"
            )
        
        # Execute skill
        try:
            print(f"🔧 Executing skill: {skill_name}")
            result = skill.execute(**parameters)
            
            # Record execution
            self.execution_history.append({
                "skill": skill_name,
                "parameters": parameters,
                "success": result.success,
                "error": result.error
            })
            
            return result
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Skill execution failed: {str(e)}"
            )
    
    def chain_skills(self, skill_chain: List[Dict[str, Any]]) -> List[SkillResult]:
        """Execute a chain of skills, passing results forward."""
        results = []
        context = {}
        
        for step in skill_chain:
            skill_name = step.get("skill")
            parameters = step.get("parameters", {})
            
            # Support variable substitution from previous results
            for key, value in parameters.items():
                if isinstance(value, str) and value.startswith("$"):
                    var_name = value[1:]
                    if var_name in context:
                        parameters[key] = context[var_name]
            
            result = self.execute_skill(skill_name, **parameters)
            results.append(result)
            
            # Store result in context for next skill
            if result.success and result.data:
                output_var = step.get("output_var", f"{skill_name}_result")
                context[output_var] = result.data
            
            # Stop chain if skill fails and no continue flag
            if not result.success and not step.get("continue_on_error", False):
                break
        
        return results
    
    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a skill."""
        skill = self.registry.get(skill_name)
        if not skill:
            return None
        
        metadata = skill.metadata
        return {
            "name": metadata.name,
            "description": metadata.description,
            "category": metadata.category,
            "version": metadata.version,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in metadata.parameters
            ],
            "returns": metadata.returns
        }
    
    def list_available_skills(self) -> List[Dict[str, str]]:
        """List all available skills with brief info."""
        skills = self.registry.get_all()
        return [
            {
                "name": skill.metadata.name,
                "category": skill.metadata.category,
                "description": skill.metadata.description
            }
            for skill in skills.values()
        ]
    
    def get_skills_by_category(self) -> Dict[str, List[str]]:
        """Get skills organized by category."""
        categories: Dict[str, List[str]] = {}
        
        for skill in self.registry.get_all().values():
            category = skill.metadata.category
            if category not in categories:
                categories[category] = []
            categories[category].append(skill.metadata.name)
        
        return categories
    
    def load_skills_from_directory(self, directory: Path) -> int:
        """Dynamically load skills from a directory."""
        loaded_count = 0
        
        if not directory.exists():
            print(f"⚠️  Skills directory not found: {directory}")
            return 0
        
        # Import all Python files as potential skills
        import importlib.util
        import sys
        
        for file_path in directory.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            
            try:
                # Load module
                spec = importlib.util.spec_from_file_location(
                    f"skills.{file_path.stem}",
                    file_path
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    spec.loader.exec_module(module)
                    
                    # Find and register skill classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Skill) and 
                            attr != Skill):
                            skill_instance = attr()
                            self.registry.register(skill_instance)
                            loaded_count += 1
            except Exception as e:
                print(f"⚠️  Failed to load skill from {file_path.name}: {e}")
        
        return loaded_count
    
    def generate_skill_prompt(self) -> str:
        """Generate a prompt describing available skills for the LLM."""
        skills = self.list_available_skills()
        
        if not skills:
            return "No skills available."
        
        prompt = "**Available Skills:**\n\n"
        
        categories = self.get_skills_by_category()
        for category, skill_names in categories.items():
            prompt += f"**{category}:**\n"
            for skill_name in skill_names:
                skill_info = self.get_skill_info(skill_name)
                if skill_info:
                    prompt += f"- `{skill_name}`: {skill_info['description']}\n"
            prompt += "\n"
        
        return prompt
