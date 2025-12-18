"""
Onboarding system for MetaPersona.
Interviews users to understand their profession and automatically generates expert personas.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class OnboardingInterview:
    """Conducts an interactive interview to learn about the user's work."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.user_profile_path = data_dir / "user_profile.json"
        self.responses: Dict[str, Any] = {}
    
    def start(self) -> Dict[str, Any]:
        """Begin the onboarding interview."""
        console.print("\n")
        console.print(Panel.fit(
            "[bold cyan]Welcome to MetaPersona! 🚀[/bold cyan]\n\n"
            "I'll create AI experts tailored to YOUR work.\n"
            "Just answer a few quick questions about what you do.",
            border_style="cyan"
        ))
        console.print("\n")
        
        # Single streamlined interview
        self._ask_quick_profile()
        
        # Save profile
        self._save_profile()
        
        # Show summary
        self._show_summary()
        
        return self.responses
    
    def _ask_quick_profile(self):
        """Ask one simple question about the user."""
        console.print("[bold cyan]Quick question:[/bold cyan]\n")
        
        console.print("What do you do and what do you like to work on?")
        console.print("[dim]Example: I'm a software developer and day trader, I code in Python/JS and use TradingView for trading[/dim]\n")
        
        user_input = Prompt.ask("").strip()
        
        # Parse the response intelligently
        user_lower = user_input.lower()
        
        # Extract profession/roles
        self.responses['profession'] = user_input
        
        # Extract programming languages
        langs = []
        common_langs = {
            'python': 'Python', 'javascript': 'JavaScript', 'js': 'JS', 
            'typescript': 'TypeScript', 'ts': 'TS', 'java': 'Java',
            'c++': 'C++', 'c#': 'C#', 'go': 'Go', 'rust': 'Rust',
            'ruby': 'Ruby', 'php': 'PHP', 'swift': 'Swift', 'kotlin': 'Kotlin',
            'react': 'React', 'vue': 'Vue', 'angular': 'Angular'
        }
        for key, value in common_langs.items():
            if key in user_lower:
                langs.append(value)
        self.responses['programming_languages'] = list(set(langs))
        
        # Extract tools
        tools = []
        common_tools = {
            'vs code': 'VS Code', 'vscode': 'VS Code', 'pycharm': 'PyCharm',
            'git': 'Git', 'docker': 'Docker', 'figma': 'Figma',
            'tradingview': 'TradingView', 'jira': 'Jira', 'notion': 'Notion',
            'slack': 'Slack', 'project x': 'Project X'
        }
        for key, value in common_tools.items():
            if key in user_lower:
                tools.append(value)
        self.responses['tools_used'] = list(set(tools))
        
        # Extract activities/interests
        activities = []
        common_activities = ['trading', 'coding', 'development', 'design', 'writing', 
                            'data analysis', 'machine learning', 'content creation', 
                            'video editing', 'bowling', 'gaming']
        for activity in common_activities:
            if activity in user_lower:
                activities.append(activity)
        self.responses['daily_tasks'] = activities if activities else ['general work']
        self.responses['needed_skills'] = activities if activities else ['general assistance']
        
        # Set defaults for other fields
        self.responses['technical_level'] = 'intermediate'
        self.responses['preferred_communication_style'] = 'professional'
        self.responses['hobbies'] = activities
        
        console.print("\n")
    
    def _save_profile(self):
        """Save the user profile to disk."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.user_profile_path, 'w') as f:
            json.dump(self.responses, f, indent=2)
        
        console.print(f"[green]✓[/green] Profile saved to {self.user_profile_path}\n")
    
    def _show_summary(self):
        """Display a summary of the responses."""
        console.print("\n")
        
        langs = ', '.join(self.responses.get('programming_languages', [])) or 'None specified'
        tools = ', '.join(self.responses.get('tools_used', [])) or 'None specified'
        
        console.print(Panel.fit(
            "[bold green]✨ Profile Created![/bold green]\n\n"
            f"• What you do: {self.responses['profession']}\n"
            f"• Skill level: {self.responses['technical_level']}\n"
            f"• Languages: {langs}\n"
            f"• Tools: {tools}\n\n"
            "Creating specialized AI experts for your work...",
            border_style="green"
        ))
        console.print("\n")
    
    def load_profile(self) -> Dict[str, Any]:
        """Load existing user profile."""
        if self.user_profile_path.exists():
            with open(self.user_profile_path, 'r') as f:
                return json.load(f)
        return {}
    
    def has_profile(self) -> bool:
        """Check if a user profile exists."""
        return self.user_profile_path.exists()


def run_onboarding(data_dir: Path) -> Dict[str, Any]:
    """Run the onboarding interview process."""
    interview = OnboardingInterview(data_dir)
    
    # Check if profile already exists
    if interview.has_profile():
        console.print("[yellow]You already have a profile.[/yellow]")
        if Confirm.ask("Would you like to update it?", default=False):
            profile = interview.start()
            _generate_expert_personas(profile, data_dir)
            return profile
        else:
            console.print("[dim]Loading existing profile...[/dim]")
            return interview.load_profile()
    
    profile = interview.start()
    _generate_expert_personas(profile, data_dir)
    return profile


def _generate_expert_personas(profile: Dict[str, Any], data_dir: Path) -> None:
    """Generate expert personas based on user profile."""
    from .persona_factory import PersonaFactory
    
    console.print("\n[bold cyan]🤖 Generating Expert Personas...[/bold cyan]\n")
    
    factory = PersonaFactory(data_dir)
    created_personas = factory.generate_personas_from_profile(profile)
    
    if created_personas:
        console.print(f"[green]✓ Created {len(created_personas)} expert persona(s):[/green]")
        for persona in created_personas:
            console.print(f"  • [cyan]{persona['name']}[/cyan] - {persona['expertise']}")
    else:
        console.print("[yellow]⚠ No personas were created. You may need to provide more details.[/yellow]")
