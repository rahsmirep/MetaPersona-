"""
AI-Powered Persona Generator
Dynamically creates expert personas for ANY profession using AI.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from rich.console import Console
import os

console = Console()


class AIPersonaGenerator:
    """Generates expert personas for any profession using AI."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.personas_dir = data_dir / "personas"
        self.personas_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = data_dir / "persona_templates_cache.json"
        self.template_cache = self._load_cache()
        
        # Use the configured LLM provider (respects .env settings)
        from .llm_provider import get_llm_provider
        self.llm = get_llm_provider()  # Uses Ollama if LLM_PROVIDER=ollama
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load cached persona templates."""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save persona templates to cache."""
        with open(self.cache_file, 'w') as f:
            json.dump(self.template_cache, f, indent=2)
    
    def generate_persona_for_profession(
        self, 
        profession: str, 
        user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an expert persona for any profession.
        
        Args:
            profession: The profession (e.g., "doctor", "electrician", "chef")
            user_context: User's profile info (tools, experience, etc.)
        
        Returns:
            Persona definition dict or None if generation fails
        """
        # Check cache first
        cache_key = profession.lower().strip()
        if cache_key in self.template_cache:
            console.print(f"[dim]Using cached template for {profession}[/dim]")
            return self._instantiate_from_cache(cache_key, user_context)
        
        # Generate new persona using AI
        console.print(f"[cyan]Generating new expert persona for: {profession}...[/cyan]")
        
        try:
            persona_def = self._ai_generate_persona(profession, user_context)
            
            if persona_def:
                # Cache the template for future use
                self.template_cache[cache_key] = persona_def
                self._save_cache()
                console.print(f"[green]✓ Created and cached {profession} expert[/green]")
                return persona_def
            
        except Exception as e:
            console.print(f"[red]Failed to generate persona: {str(e)}[/red]")
            return None
    
    def _ai_generate_persona(
        self, 
        profession: str, 
        user_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Use AI to generate a persona definition."""
        
        tools = user_context.get('tools_used', [])
        languages = user_context.get('programming_languages', [])
        tasks = user_context.get('daily_tasks', [])
        skills = user_context.get('needed_skills', [])
        
        prompt = f"""Create an expert AI persona definition for a {profession}.

User Context:
- Profession: {profession}
- Daily tasks: {', '.join(tasks) if tasks else 'general work'}
- Tools used: {', '.join(tools) if tools else 'standard tools'}
- Programming languages: {', '.join(languages) if languages else 'none'}
- Needed help with: {', '.join(skills) if skills else 'general assistance'}

Generate a JSON persona definition with:
1. name: A professional title (e.g., "Senior Cardiologist", "Master Electrician")
2. role: One-line role description
3. expertise: List of 5-7 specific expertise areas for this profession
4. system_prompt: A detailed system prompt that defines how this expert should help the user

The persona should:
- Be an expert in their field with deep knowledge
- Understand the user's specific context and tools
- Provide practical, actionable advice
- Use professional terminology appropriate to the field
- Have access to all past conversations with the user

Return ONLY valid JSON in this exact format:
{{
  "name": "Professional Title",
  "role": "Brief role description",
  "expertise": ["area1", "area2", "area3", "area4", "area5"],
  "system_prompt": "Detailed system prompt explaining the persona's expertise, how they help, and their understanding of the user's context..."
}}"""

        try:
            # Use the configured LLM provider (Ollama, OpenAI, or Anthropic)
            messages = [
                {"role": "system", "content": "You are an expert at creating AI persona definitions. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            # Generate response (parameters automatically adapted per provider)
            response = self.llm.generate(messages=messages, temperature=0.7)
            content = response.strip()
            
            # Parse JSON response
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            persona_def = json.loads(content.strip())
            
            # Add metadata
            persona_def['profession'] = profession
            persona_def['generated_by'] = 'ai'
            persona_def['user_context'] = user_context
            
            return persona_def
            
        except Exception as e:
            console.print(f"[red]AI generation error: {str(e)}[/red]")
            return None
    
    def _instantiate_from_cache(
        self, 
        cache_key: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a persona instance from cached template."""
        template = self.template_cache[cache_key].copy()
        template['user_context'] = user_context
        return template
    
    def save_persona(self, persona: Dict[str, Any], filename: str):
        """Save generated persona to file."""
        filepath = self.personas_dir / filename
        with open(filepath, 'w') as f:
            json.dump(persona, f, indent=2)
        console.print(f"[green]Saved persona to {filename}[/green]")
