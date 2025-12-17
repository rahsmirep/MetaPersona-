#!/usr/bin/env python3
"""
MetaPersona CLI - Command Line Interface
Interact with your personal AI agent.
"""
import os
import sys
import click
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.identity import IdentityLayer
from src.persona_agent import AgentManager
from src.memory_loop import MemoryLoop
from src.cognitive_profile import ProfileManager
from src.skills import SkillManager
from src.skills.builtin import CalculatorSkill, FileOpsSkill, WebSearchSkill
from src.personalized_agents import (
    PersonalizedResearchAgent,
    PersonalizedCodeAgent, 
    PersonalizedWriterAgent,
    PersonalizedGeneralistAgent
)
from src.user_profiling import UserProfilingSystem, UserProfile

console = Console()


@click.group()
def cli():
    """MetaPersona - Your Personal AI Agent"""
    pass


@cli.command()
@click.option('--user-id', prompt='Enter your user ID', help='Your user identifier')
@click.option('--data-dir', default='./data', help='Data directory path')
def init(user_id: str, data_dir: str):
    """Initialize MetaPersona identity and profile."""
    console.print("\n[bold cyan]🚀 Initializing MetaPersona...[/bold cyan]\n")
    
    # Create identity
    identity = IdentityLayer(data_dir)
    
    if identity.identity_exists():
        if not Confirm.ask("Identity already exists. Recreate?"):
            console.print("[yellow]Using existing identity[/yellow]")
        else:
            identity.generate_keypair()
    else:
        identity.generate_keypair()
    
    # Create profile
    profile_manager = ProfileManager(data_dir)
    profile = profile_manager.load_profile()
    
    if not profile:
        profile = profile_manager.create_profile(user_id)
        
        # Interactive profile setup
        console.print("\n[bold]Let's personalize your agent:[/bold]\n")
        
        # Writing style
        tone = Prompt.ask("Writing tone", 
                         choices=["formal", "casual", "technical", "friendly", "professional"],
                         default="casual")
        profile.writing_style.tone = tone
        
        vocab = Prompt.ask("Vocabulary level",
                          choices=["simple", "intermediate", "advanced", "expert"],
                          default="intermediate")
        profile.writing_style.vocabulary_level = vocab
        
        # Decision style
        decision_style = Prompt.ask("Decision-making approach",
                                   choices=["analytical", "intuitive", "cautious", "bold", "balanced"],
                                   default="analytical")
        profile.decision_pattern.approach = decision_style
        
        risk = Prompt.ask("Risk tolerance",
                         choices=["conservative", "moderate", "aggressive"],
                         default="moderate")
        profile.decision_pattern.risk_tolerance = risk
        
        profile_manager.save_profile(profile)
        
        console.print(f"\n[green]✓ Profile created successfully![/green]")
    else:
        console.print(f"[yellow]Profile already exists for: {profile.user_id}[/yellow]")
    
    info = identity.get_identity_info()
    console.print(Panel(
        f"[bold]Identity Fingerprint:[/bold] {info['public_key_fingerprint'][:32]}...\n"
        f"[bold]User ID:[/bold] {user_id}\n"
        f"[bold]Data Directory:[/bold] {data_dir}",
        title="✓ MetaPersona Initialized",
        border_style="green"
    ))


@cli.command()
@click.option('--provider', help='LLM provider (openai/anthropic/ollama)')
@click.option('--data-dir', default='./data', help='Data directory path')
@click.option('--use-profile', is_flag=True, help='Use adaptive user profile if available')
def chat(provider: str, data_dir: str, use_profile: bool):
    """Start interactive chat session with your agent."""
    console.print("\n[bold cyan]💬 MetaPersona Chat Session[/bold cyan]\n")
    
    # Initialize agent
    try:
        # Check if adaptive profile is requested but doesn't exist - trigger onboarding
        if use_profile:
            profile_manager = ProfileManager(data_dir)
            cognitive_profile = profile_manager.load_profile()
            
            if cognitive_profile:
                # Check for adaptive user profile
                profiling_system = UserProfilingSystem(data_dir)
                user_profile = profiling_system.load_profile(cognitive_profile.user_id)
                
                if not user_profile:
                    console.print("[yellow]No adaptive profile found. Let me get to know you first![/yellow]\n")
                    if Confirm.ask("Would you like me to ask you some questions to personalize your experience?", default=True):
                        user_profile = profiling_system.conduct_onboarding(cognitive_profile.user_id, interactive=True)
                        console.print("\n[green]✓ Profile created! Starting chat with personalized settings...[/green]\n")
                    else:
                        console.print("[yellow]Continuing without adaptive profile...[/yellow]\n")
                        use_profile = False
        
        agent_manager = AgentManager(data_dir)
        agent = agent_manager.initialize_agent(provider_name=provider, use_adaptive_profile=use_profile)
        memory = MemoryLoop(data_dir)
        
        # Show profile information
        profile_info = f"Agent active for: [bold]{agent.profile.user_id}[/bold]\n"
        profile_info += f"Interactions: {agent.profile.interaction_count}\n"
        profile_info += f"Accuracy: {agent.profile.accuracy_score:.1%}"
        
        if agent.adaptive_profile:
            profile_info += f"\n\n[bold cyan]Adaptive Profile Active:[/bold cyan]\n"
            profile_info += f"Profession: {agent.adaptive_profile.profession}\n"
            profile_info += f"Style: {agent.adaptive_profile.preferred_communication_style}\n"
            profile_info += f"Skill Packs: {', '.join(agent.adaptive_profile.loaded_skill_packs[:3])}"
        
        console.print(Panel(profile_info, border_style="cyan"))
        
        console.print("\n[dim]Type 'exit' to quit, 'clear' to clear history, 'status' for agent info[/dim]\n")
        
        while True:
            try:
                task = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                
                if task.lower() == 'exit':
                    break
                elif task.lower() == 'clear':
                    agent.clear_conversation()
                    console.print("[yellow]Conversation history cleared[/yellow]")
                    continue
                elif task.lower() == 'status':
                    show_status(agent)
                    continue
                
                # Process task
                response = agent.process_task(task)
                
                # Display response
                console.print(f"\n[bold green]Agent[/bold green]")
                console.print(Panel(Markdown(response), border_style="green"))
                
                # Record interaction
                interaction = memory.record_interaction(task, response)
                agent.profile.interaction_count += 1
                
                # Optional feedback
                if Confirm.ask("\n[dim]Provide feedback?[/dim]", default=False):
                    score = float(Prompt.ask("Rate response (1-5)", default="3"))
                    feedback_text = Prompt.ask("Feedback (optional)", default="")
                    
                    interactions = memory.load_all_interactions()
                    memory.add_feedback(len(interactions) - 1, score, feedback_text)
                    agent.profile.feedback_received += 1
                    
                    # Update accuracy
                    agent.profile.accuracy_score = (
                        (agent.profile.accuracy_score * (agent.profile.feedback_received - 1) + score / 5.0)
                        / agent.profile.feedback_received
                    )
                
                # Save state
                agent_manager.save_agent_state(agent)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
        
        console.print("\n[cyan]Chat session ended.[/cyan]\n")
        
    except Exception as e:
        console.print(f"[red]Failed to initialize agent: {str(e)}[/red]")
        console.print("[yellow]Have you run 'metapersona init' and configured .env?[/yellow]")


@cli.command()
@click.argument('task')
@click.option('--provider', help='LLM provider')
@click.option('--data-dir', default='./data', help='Data directory path')
def ask(task: str, provider: str, data_dir: str):
    """Ask your agent to perform a single task."""
    try:
        agent_manager = AgentManager(data_dir)
        agent = agent_manager.initialize_agent(provider_name=provider)
        memory = MemoryLoop(data_dir)
        
        response = agent.process_task(task)
        
        console.print(f"\n[bold green]Response:[/bold green]")
        console.print(Panel(Markdown(response), border_style="green"))
        
        # Record interaction
        memory.record_interaction(task, response)
        agent.profile.interaction_count += 1
        agent_manager.save_agent_state(agent)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.option('--data-dir', default='./data', help='Data directory path')
def status(data_dir: str):
    """Show agent status and learning progress."""
    try:
        profile_manager = ProfileManager(data_dir)
        profile = profile_manager.load_profile()
        memory = MemoryLoop(data_dir)
        
        if not profile:
            console.print("[yellow]No profile found. Run 'metapersona init' first.[/yellow]")
            return
        
        # Agent status
        table = Table(title="Agent Status", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("User ID", profile.user_id)
        table.add_row("Total Interactions", str(profile.interaction_count))
        table.add_row("Feedback Received", str(profile.feedback_received))
        table.add_row("Accuracy Score", f"{profile.accuracy_score:.1%}")
        table.add_row("Writing Examples", str(len(profile.writing_style.examples)))
        table.add_row("Decision History", str(len(profile.decision_pattern.past_decisions)))
        table.add_row("Last Updated", profile.updated_at)
        
        console.print("\n")
        console.print(table)
        
        # Feedback summary
        feedback = memory.get_feedback_summary()
        console.print(f"\n[bold]Feedback Summary:[/bold]")
        console.print(f"  Average Score: {feedback['average_score']:.2f}/5.0")
        console.print(f"  Feedback Rate: {feedback['feedback_rate']:.1%}")
        
        # Learning progress
        progress = memory.analyze_learning_progress()
        if progress.get('status') == 'analyzed':
            console.print(f"\n[bold]Learning Progress:[/bold]")
            console.print(f"  Trend: {progress['trend']}")
            console.print(f"  Improvement: {progress['improvement']:+.2f}")
        
        # Insights
        insights = memory.extract_learning_insights()
        if insights:
            console.print(f"\n[bold]Insights:[/bold]")
            for insight in insights:
                console.print(f"  {insight}")
        
        console.print()
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


def show_status(agent):
    """Display agent status in chat."""
    status = agent.get_agent_status()
    
    table = Table(show_header=False)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    
    for key, value in status.items():
        table.add_row(key.replace('_', ' ').title(), str(value))
    
    console.print(table)


@cli.command()
@click.argument('example_file', type=click.Path(exists=True))
@click.option('--data-dir', default='./data', help='Data directory path')
def learn(example_file: str, data_dir: str):
    """Add writing examples to improve agent's style."""
    try:
        with open(example_file, 'r', encoding='utf-8') as f:
            example_text = f.read()
        
        profile_manager = ProfileManager(data_dir)
        profile = profile_manager.load_profile()
        
        if not profile:
            console.print("[yellow]No profile found. Run 'metapersona init' first.[/yellow]")
            return
        
        profile_manager.update_writing_style(profile, example_text)
        console.print(f"[green]✓ Added writing example ({len(example_text)} chars)[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.option('--data-dir', default='./data', help='Data directory path')
@click.option('--count', default=10, help='Number of recent interactions to show')
def history(data_dir: str, count: int):
    """View interaction history."""
    try:
        memory = MemoryLoop(data_dir)
        interactions = memory.get_recent_interactions(count)
        
        if not interactions:
            console.print("[yellow]No interactions recorded yet.[/yellow]")
            return
        
        console.print(f"\n[bold]Recent Interactions ({len(interactions)}):[/bold]\n")
        
        for i, interaction in enumerate(interactions[-count:], 1):
            score_text = f"⭐ {interaction.feedback_score:.1f}/5" if interaction.feedback_score else "No feedback"
            
            console.print(f"[bold cyan]{i}. {interaction.timestamp}[/bold cyan] {score_text}")
            console.print(f"[dim]Task:[/dim] {interaction.task[:100]}...")
            console.print(f"[dim]Response:[/dim] {interaction.response[:100]}...")
            console.print()
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.option('--data-dir', default='./data', help='Data directory path')
def skills(data_dir: str):
    """List available skills."""
    try:
        # Initialize skill manager and load built-in skills
        skill_manager = SkillManager()
        skill_manager.registry.register(CalculatorSkill())
        skill_manager.registry.register(FileOpsSkill())
        skill_manager.registry.register(WebSearchSkill())
        
        skills_list = skill_manager.list_available_skills()
        
        if not skills_list:
            console.print("[yellow]No skills available.[/yellow]")
            return
        
        # Group by category
        categories = skill_manager.get_skills_by_category()
        
        console.print("\n[bold cyan]📦 Available Skills:[/bold cyan]\n")
        
        for category, skill_names in categories.items():
            console.print(f"[bold]{category}:[/bold]")
            
            for skill_name in skill_names:
                skill_info = skill_manager.get_skill_info(skill_name)
                if skill_info:
                    console.print(f"  • [cyan]{skill_name}[/cyan]: {skill_info['description']}")
            console.print()
        
        console.print(f"[dim]Total skills: {len(skills_list)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.argument('skill_name')
@click.option('--data-dir', default='./data', help='Data directory path')
def skill_info(skill_name: str, data_dir: str):
    """Get detailed information about a skill."""
    try:
        # Initialize skill manager and load built-in skills
        skill_manager = SkillManager()
        skill_manager.registry.register(CalculatorSkill())
        skill_manager.registry.register(FileOpsSkill())
        skill_manager.registry.register(WebSearchSkill())
        
        info = skill_manager.get_skill_info(skill_name)
        
        if not info:
            console.print(f"[red]Skill '{skill_name}' not found.[/red]")
            return
        
        # Display skill info
        console.print(f"\n[bold cyan]📦 {info['name']}[/bold cyan]")
        console.print(f"[dim]{info['description']}[/dim]\n")
        
        console.print(f"[bold]Category:[/bold] {info['category']}")
        console.print(f"[bold]Version:[/bold] {info['version']}\n")
        
        if info['parameters']:
            console.print("[bold]Parameters:[/bold]")
            for param in info['parameters']:
                required = "[red]*[/red]" if param['required'] else ""
                default = f" (default: {param['default']})" if param['default'] is not None else ""
                console.print(f"  • [cyan]{param['name']}[/cyan] {required}: {param['description']}{default}")
                console.print(f"    Type: [dim]{param['type']}[/dim]")
        
        console.print(f"\n[bold]Returns:[/bold] {info['returns']}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command()
@click.argument('skill_name')
@click.option('--data-dir', default='./data', help='Data directory path')
@click.option('--params', '-p', multiple=True, help='Skill parameters as key=value')
def use_skill(skill_name: str, data_dir: str, params):
    """Execute a skill directly."""
    try:
        # Initialize skill manager and load built-in skills
        skill_manager = SkillManager()
        skill_manager.registry.register(CalculatorSkill())
        skill_manager.registry.register(FileOpsSkill())
        skill_manager.registry.register(WebSearchSkill())
        
        # Parse parameters
        parameters = {}
        for param in params:
            if '=' in param:
                key, value = param.split('=', 1)
                parameters[key.strip()] = value.strip()
        
        # Execute skill
        console.print(f"\n[bold]Executing skill:[/bold] {skill_name}")
        console.print(f"[dim]Parameters: {parameters}[/dim]\n")
        
        result = skill_manager.execute_skill(skill_name, **parameters)
        
        if result.success:
            console.print("[bold green]✓ Success![/bold green]\n")
            console.print(Panel(str(result.data), title="Result", border_style="green"))
            
            if result.metadata:
                console.print(f"\n[dim]Metadata: {result.metadata}[/dim]")
        else:
            console.print(f"[bold red]✗ Failed:[/bold red] {result.error}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command("agents-list")
@click.option('--data-dir', default='./data', help='Data directory path')
def agents_list(data_dir: str):
    """List all registered agents."""
    try:
        from src.agent_registry import AgentRegistry
        
        registry = AgentRegistry(Path(data_dir))
        agents = registry.list_all()
        
        if not agents:
            console.print("[yellow]No agents registered yet.[/yellow]")
            console.print("\n[dim]Tip: Agents are registered when you use multi-agent features.[/dim]")
            return
        
        table = Table(title="Registered Agents")
        table.add_column("Agent ID", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Description", style="white")
        table.add_column("Capabilities", style="yellow")
        table.add_column("Interactions", style="magenta")
        
        for agent in agents:
            table.add_row(
                agent.agent_id,
                agent.role,
                agent.description[:50] + "..." if len(agent.description) > 50 else agent.description,
                str(len(agent.capabilities)),
                str(len(agent.memory.interactions))
            )
        
        console.print(table)
        console.print(f"\n[bold]Total Agents:[/bold] {len(agents)}")
        console.print(f"[bold]Roles:[/bold] {', '.join(registry.list_roles())}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command("agents-status")
@click.option('--data-dir', default='./data', help='Data directory path')
@click.option('--agent-id', help='Specific agent ID to show detailed status')
def agents_status(data_dir: str, agent_id: str):
    """Show detailed status of agents."""
    try:
        from src.agent_registry import AgentRegistry
        
        registry = AgentRegistry(Path(data_dir))
        
        if agent_id:
            # Show specific agent
            agent = registry.get(agent_id)
            if not agent:
                console.print(f"[red]Agent '{agent_id}' not found.[/red]")
                return
            
            status = agent.get_status()
            
            console.print(Panel(
                f"[bold]Agent ID:[/bold] {status['agent_id']}\n"
                f"[bold]Role:[/bold] {status['role']}\n"
                f"[bold]Description:[/bold] {status['description']}\n"
                f"[bold]Skills:[/bold] {status['skills_count']}\n"
                f"[bold]Interactions:[/bold] {status['interactions_count']}\n"
                f"[bold]Learnings:[/bold] {status['learnings_count']}\n"
                f"[bold]Created:[/bold] {status['created_at']}\n"
                f"[bold]Updated:[/bold] {status['updated_at']}",
                title=f"Agent Status: {agent_id}",
                border_style="cyan"
            ))
            
            # Show capabilities
            console.print("\n[bold]Capabilities:[/bold]")
            for cap in status['capabilities']:
                console.print(f"  • {cap['name']}: {cap['description']} (confidence: {cap['confidence']})")
        else:
            # Show registry status
            status = registry.get_status()
            console.print(Panel(
                f"[bold]Total Agents:[/bold] {status['total_agents']}\n"
                f"[bold]Roles:[/bold] {', '.join(status['roles']) if status['roles'] else 'None'}",
                title="Agent Registry Status",
                border_style="cyan"
            ))
            
            if status['agents']:
                table = Table(title="Agents Overview")
                table.add_column("Agent ID", style="cyan")
                table.add_column("Role", style="green")
                table.add_column("Capabilities", style="yellow")
                table.add_column("Skills", style="blue")
                table.add_column("Interactions", style="magenta")
                
                for agent_info in status['agents']:
                    table.add_row(
                        agent_info['agent_id'],
                        agent_info['role'],
                        str(agent_info['capabilities_count']),
                        str(agent_info['skills_count']),
                        str(agent_info['interactions_count'])
                    )
                
                console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")


@cli.command("route-task")
@click.argument('task')
@click.option('--data-dir', default='./data', help='Data directory path')
@click.option('--explain', is_flag=True, help='Explain routing decision without executing')
def route_task(task: str, data_dir: str, explain: bool):
    """Route a task to the best agent (or explain the routing)."""
    try:
        from src.agent_registry import AgentRegistry
        from src.task_router import TaskRouter
        from src.llm_provider import get_llm_provider
        from src.specialized_agents import ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent
        from src.skills import SkillManager
        
        # Initialize registry and router
        registry = AgentRegistry(Path(data_dir))
        
        # Register specialized agents if not already registered
        llm_provider = get_llm_provider()
        skills_manager = SkillManager()
        
        if "researcher" not in registry:
            research_agent = ResearchAgent(
                agent_id="researcher",
                role="researcher",
                description="Specialized in research, information gathering, and analysis",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(research_agent)
        
        if "coder" not in registry:
            code_agent = CodeAgent(
                agent_id="coder",
                role="coder",
                description="Specialized in coding, debugging, and technical tasks",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(code_agent)
        
        if "writer" not in registry:
            writer_agent = WriterAgent(
                agent_id="writer",
                role="writer",
                description="Specialized in writing, content creation, and communication",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(writer_agent)
        
        if "generalist" not in registry:
            generalist_agent = GeneralistAgent(
                agent_id="generalist",
                role="generalist",
                description="Handles general tasks and conversations",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(generalist_agent)
        
        router = TaskRouter(
            registry, 
            default_agent_id="generalist",
            llm_provider=llm_provider,
            use_llm_routing=True
        )
        
        if explain:
            # Explain routing decision
            explanation = router.explain_routing(task)
            
            console.print(Panel(
                f"[bold]Task:[/bold] {explanation['task']}\n"
                f"[bold]Min Confidence:[/bold] {explanation['min_confidence']}\n"
                f"[bold]Recommended Agent:[/bold] {explanation['recommended_agent'] or 'None'}\n"
                f"[bold]Confidence:[/bold] {explanation['recommended_confidence']}",
                title="Routing Analysis",
                border_style="cyan"
            ))
            
            # Show all candidates
            console.print("\n[bold]All Candidates:[/bold]")
            table = Table()
            table.add_column("Agent", style="cyan")
            table.add_column("Role", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Meets Threshold", style="magenta")
            
            for candidate in explanation['all_candidates']:
                meets = "✓" if candidate['meets_threshold'] else "✗"
                table.add_row(
                    candidate['agent_id'],
                    candidate['role'],
                    f"{candidate['confidence']:.2f}",
                    meets
                )
            
            console.print(table)
        else:
            # Actually route and execute
            console.print(f"\n[bold]Routing task:[/bold] {task}\n")
            
            result = router.execute_task(task)
            
            if result.success:
                console.print("[bold green]✓ Task completed successfully![/bold green]\n")
                console.print(Panel(
                    str(result.result),
                    title=f"Result (by {result.metadata.get('agent_id', 'unknown')})",
                    border_style="green"
                ))
            else:
                console.print(f"[bold red]✗ Task failed:[/bold red] {result.error}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


@cli.command("multi-agent-chat")
@click.option('--data-dir', default='./data', help='Data directory path')
def multi_agent_chat(data_dir: str):
    """Interactive chat with automatic agent routing."""
    try:
        from src.agent_registry import AgentRegistry
        from src.task_router import TaskRouter
        from src.llm_provider import get_llm_provider
        from src.specialized_agents import ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent
        from src.skills import SkillManager
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import InMemoryHistory
        import asyncio
        
        console.print(Panel(
            "[bold cyan]Multi-Agent Chat[/bold cyan]\n\n"
            "Your messages will be automatically routed to the best agent.\n"
            "Type 'exit' to quit, 'agents' to list agents, 'stats' for routing stats.",
            border_style="cyan"
        ))
        
        # Initialize registry and router
        registry = AgentRegistry(Path(data_dir))
        llm_provider = get_llm_provider()
        skills_manager = SkillManager()
        
        # Register specialized agents
        if "researcher" not in registry:
            registry.register(ResearchAgent(
                agent_id="researcher",
                role="researcher",
                description="Specialized in research and information gathering",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            ))
        
        if "coder" not in registry:
            registry.register(CodeAgent(
                agent_id="coder",
                role="coder",
                description="Specialized in coding and technical tasks",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            ))
        
        if "writer" not in registry:
            registry.register(WriterAgent(
                agent_id="writer",
                role="writer",
                description="Specialized in writing and content creation",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            ))
        
        if "generalist" not in registry:
            registry.register(GeneralistAgent(
                agent_id="generalist",
                role="generalist",
                description="Handles general tasks",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            ))
        
        router = TaskRouter(
            registry, 
            default_agent_id="generalist",
            llm_provider=llm_provider,
            use_llm_routing=True
        )
        
        # Interactive loop
        session = PromptSession(history=InMemoryHistory())
        
        while True:
            try:
                user_input = session.prompt("\n[You] > ")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == 'agents':
                    agents = registry.list_all()
                    console.print(f"\n[bold]Registered Agents:[/bold]")
                    for agent in agents:
                        console.print(f"  • {agent.agent_id} ({agent.role})")
                    continue
                
                if user_input.lower() == 'stats':
                    stats = router.get_routing_stats()
                    console.print(f"\n[bold]Routing Statistics:[/bold]")
                    console.print(f"  Total routes: {stats['total_routes']}")
                    console.print(f"  Average confidence: {stats['average_confidence']:.2f}")
                    console.print(f"  Most used: {stats['most_used_agent']}")
                    console.print(f"\n[bold]Agent usage:[/bold]")
                    for agent_id, count in stats['agent_usage'].items():
                        console.print(f"  • {agent_id}: {count}")
                    continue
                
                # Route and execute
                agent = router.route_task(user_input)
                if not agent:
                    console.print("[red]No suitable agent found.[/red]")
                    continue
                
                console.print(f"[dim]→ Routed to: {agent.agent_id}[/dim]")
                
                result = agent.handle_task(user_input)
                
                if result.success:
                    console.print(f"\n[{agent.role}] {result.result}")
                else:
                    console.print(f"[red]Error: {result.error}[/red]")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except EOFError:
                break
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


@cli.command('onboard')
@click.option('--user-id', prompt='Your name or username', help='User identifier')
@click.option('--data-dir', default='./data', help='Data directory path')
def onboard(user_id: str, data_dir: str):
    """Complete onboarding to personalize your experience."""
    try:
        profiling_system = UserProfilingSystem(data_dir)
        
        # Check if profile exists
        existing_profile = profiling_system.load_profile(user_id)
        if existing_profile:
            if not Confirm.ask(f"\n[yellow]Profile for '{user_id}' already exists. Redo onboarding?[/yellow]"):
                console.print("[cyan]Keeping existing profile.[/cyan]")
                return
        
        # Conduct onboarding
        profile = profiling_system.conduct_onboarding(user_id, interactive=True)
        
        # Show summary
        console.print(Panel(
            f"[bold]Profile Summary for {profile.user_id}[/bold]\n\n"
            f"Profession: {profile.profession}\n"
            f"Industry: {profile.industry}\n"
            f"Technical Level: {profile.technical_level}\n"
            f"Communication Style: {profile.preferred_communication_style}\n\n"
            f"[bold]Loaded Skill Packs:[/bold]\n" +
            '\n'.join([f"  • {pack}" for pack in profile.loaded_skill_packs]) + "\n\n"
            f"[bold]Agent Routing Weights:[/bold]\n" +
            '\n'.join([f"  • {agent}: {weight:.2f}x" for agent, weight in profile.agent_routing_preferences.items()]),
            title="✓ Onboarding Complete",
            border_style="green"
        ))
        
        console.print("\n[cyan]You can now use:[/cyan]")
        console.print(f"  [bold]python metapersona.py adaptive-chat[/bold] - Chat with adaptive agents")
        console.print(f"  [bold]python metapersona.py profile --user-id {user_id}[/bold] - View your profile\n")
        
    except Exception as e:
        console.print(f"[red]Onboarding failed: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


@cli.command('profile')
@click.option('--user-id', prompt='User ID', help='User identifier')
@click.option('--data-dir', default='./data', help='Data directory path')
def show_profile(user_id: str, data_dir: str):
    """View your user profile and adaptive settings."""
    try:
        profiling_system = UserProfilingSystem(data_dir)
        profile = profiling_system.load_profile(user_id)
        
        if not profile:
            console.print(f"[red]No profile found for '{user_id}'[/red]")
            console.print("[yellow]Run: python metapersona.py onboard[/yellow]")
            return
        
        # Format industry display
        industry_display = ', '.join(profile.industry) if isinstance(profile.industry, list) else profile.industry
        
        # Display profile
        console.print(Panel(
            f"[bold cyan]User Profile: {profile.user_id}[/bold cyan]\n\n"
            f"[bold]Professional Background:[/bold]\n"
            f"  Profession: {profile.profession}\n"
            f"  Industry: {industry_display}\n"
            f"  Level: {profile.job_level}\n"
            f"  Technical Level: {profile.technical_level}\n\n"
            f"[bold]Daily Work:[/bold]\n"
            f"  Tasks: {', '.join(profile.daily_tasks[:3]) if profile.daily_tasks else 'None specified'}\n"
            f"  Tools: {', '.join(profile.tools_used[:3]) if profile.tools_used else 'None specified'}\n" +
            (f"  Languages: {', '.join(profile.programming_languages)}\n" if profile.programming_languages else "") + "\n"
            f"[bold]Preferences:[/bold]\n"
            f"  Communication: {profile.preferred_communication_style}\n"
            f"  Help Frequency: {profile.help_frequency}\n\n"
            f"[bold]Loaded Skill Packs:[/bold]\n" +
            '\n'.join([f"  • {pack}" for pack in profile.loaded_skill_packs]) + "\n\n"
            f"[bold]Agent Routing Weights:[/bold]\n" +
            '\n'.join([f"  • {agent}: {weight:.2f}x" for agent, weight in profile.agent_routing_preferences.items()]),
            border_style="cyan"
        ))
        
        # Display timestamps
        try:
            from datetime import datetime as dt
            created_str = profile.created_at.strftime('%Y-%m-%d %H:%M') if isinstance(profile.created_at, dt) else str(profile.created_at)
            updated_str = profile.updated_at.strftime('%Y-%m-%d %H:%M') if isinstance(profile.updated_at, dt) else str(profile.updated_at)
            console.print(f"\nCreated: {created_str}")
            console.print(f"Updated: {updated_str}\n")
        except:
            pass  # Skip timestamp display if there's an issue
        
    except Exception as e:
        console.print(f"[red]Error loading profile: {str(e)}[/red]")


@cli.command('adaptive-chat')
@click.option('--user-id', prompt='User ID', help='User identifier')
@click.option('--provider', default='ollama', help='LLM provider')
@click.option('--data-dir', default='./data', help='Data directory path')
def adaptive_chat(user_id: str, provider: str, data_dir: str):
    """Chat with agents adapted to YOUR profile and needs."""
    from src.agent_registry import AgentRegistry
    from src.task_router import TaskRouter
    from src.llm_provider import get_llm_provider
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    
    try:
        # Load user profile
        profiling_system = UserProfilingSystem(data_dir)
        profile = profiling_system.load_profile(user_id)
        
        if not profile:
            console.print(f"[red]No profile found for '{user_id}'[/red]")
            console.print("[yellow]Please run onboarding first:[/yellow]")
            console.print("  python metapersona.py onboard\n")
            return
        
        console.print(f"\n[bold cyan]🎭 Adaptive Multi-Agent Chat[/bold cyan]")
        console.print(f"[dim]Personalized for: {profile.user_id} ({profile.profession})[/dim]\n")
        
        # Initialize components
        llm_provider = get_llm_provider(provider)
        skills_manager = SkillManager()
        registry = AgentRegistry(data_dir)
        
        # Get adaptive system prompt
        adaptive_prompt = profiling_system.get_adaptive_system_prompt(profile)
        
        # Register specialized agents (generic versions)
        from src.specialized_agents import ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent
        
        console.print("[cyan]Initializing adaptive agents...[/cyan]")
        
        if "researcher" not in registry:
            researcher = ResearchAgent(
                agent_id="researcher",
                role="researcher",
                description=f"Research specialist adapted for {profile.profession}",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(researcher)
            console.print("  ✓ Research Agent (adapted for your needs)")
        
        if "coder" not in registry:
            coder = CodeAgent(
                agent_id="coder",
                role="coder",
                description=f"Coding specialist adapted for {profile.technical_level} level",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(coder)
            console.print("  ✓ Code Agent (adapted for your technical level)")
        
        if "writer" not in registry:
            writer = WriterAgent(
                agent_id="writer",
                role="writer",
                description=f"Writing specialist using {profile.preferred_communication_style} style",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(writer)
            console.print("  ✓ Writer Agent (adapted for your communication style)")
        
        if "generalist" not in registry:
            generalist = GeneralistAgent(
                agent_id="generalist",
                role="generalist",
                description=f"General assistant for {profile.user_id}",
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(generalist)
            console.print("  ✓ Generalist Agent (your default helper)")
        
        # Create router with profile-based weights
        router = TaskRouter(
            registry,
            default_agent_id="generalist",
            llm_provider=llm_provider,
            use_llm_routing=True
        )
        
        # Apply routing weight adjustments
        console.print(f"\n[bold green]System Ready![/bold green]")
        console.print(f"[dim]Skill Packs: {', '.join(profile.loaded_skill_packs)}[/dim]")
        console.print(f"[dim]Routing optimized for: {profile.profession}[/dim]\n")
        console.print("[dim]Commands: 'exit', 'agents', 'stats', 'profile'[/dim]\n")
        
        # Interactive loop
        session = PromptSession(history=InMemoryHistory())
        
        while True:
            try:
                user_input = session.prompt(f"\n[{profile.user_id}] > ")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == 'agents':
                    agents = registry.list_all()
                    console.print(f"\n[bold]Your Adaptive Agents:[/bold]")
                    for agent in agents:
                        weight = profile.agent_routing_preferences.get(agent.agent_id, 1.0)
                        console.print(f"  • {agent.agent_id} ({agent.role}) - Weight: {weight:.2f}x")
                    continue
                
                if user_input.lower() == 'stats':
                    stats = router.get_routing_stats()
                    console.print(f"\n[bold]Routing Statistics:[/bold]")
                    console.print(f"  Total routes: {stats['total_routes']}")
                    console.print(f"  Average confidence: {stats['average_confidence']:.2f}")
                    console.print(f"  Most used: {stats['most_used_agent']}")
                    console.print(f"\n[bold]Agent usage:[/bold]")
                    for agent_id, count in stats['agent_usage'].items():
                        console.print(f"  • {agent_id}: {count}")
                    continue
                
                if user_input.lower() == 'profile':
                    console.print(f"\n[bold]Your Profile:[/bold]")
                    console.print(f"  Profession: {profile.profession}")
                    console.print(f"  Skill Packs: {', '.join(profile.loaded_skill_packs)}")
                    console.print(f"  Communication: {profile.preferred_communication_style}")
                    continue
                
                # Route with profile-based weight adjustments
                scored_agents = []
                for agent in registry.list_all():
                    base_confidence = agent.can_handle_task(user_input)
                    weight = profile.agent_routing_preferences.get(agent.agent_id, 1.0)
                    adjusted_confidence = min(1.0, base_confidence * weight)
                    if adjusted_confidence >= router.min_confidence:
                        scored_agents.append((agent, adjusted_confidence))
                
                if not scored_agents:
                    console.print("[red]No suitable agent found.[/red]")
                    continue
                
                # Select best agent
                scored_agents.sort(key=lambda x: x[1], reverse=True)
                agent, confidence = scored_agents[0]
                
                console.print(f"[dim]→ Routing to {agent.agent_id} (confidence: {confidence:.2f})[/dim]")
                
                # Add adaptive context to task
                context = {
                    "user_profile": profile.model_dump(),
                    "adaptive_prompt": adaptive_prompt
                }
                
                result = agent.handle_task(user_input, context)
                
                if result.success:
                    console.print(f"\n[bold green]{agent.role.title()}:[/bold green]")
                    console.print(Panel(result.result, border_style="green"))
                else:
                    console.print(f"[red]Error: {result.error}[/red]")
                
                # Record routing for stats
                router._record_routing(user_input, agent, confidence, [])
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except EOFError:
                break
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


@cli.command('persona-chat')
@click.option('--provider', default='ollama', help='LLM provider')
@click.option('--data-dir', default='./data', help='Data directory path')
def persona_chat(provider: str, data_dir: str):
    """Interactive chat with YOUR personalized multi-agent system."""
    from src.agent_registry import AgentRegistry
    from src.task_router import TaskRouter
    from src.llm_provider import get_llm_provider
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
    
    console.print("\n[bold cyan]🎭 Personalized Multi-Agent Chat[/bold cyan]\n")
    console.print("[dim]Your specialized agents, all acting in YOUR style[/dim]\n")
    
    try:
        # Load your cognitive profile
        agent_manager = AgentManager(data_dir)
        persona_agent = agent_manager.initialize_agent(provider_name=provider)
        cognitive_profile = persona_agent.profile
        
        # Initialize components
        llm_provider = get_llm_provider(provider)
        skills_manager = SkillManager()
        registry = AgentRegistry(data_dir)
        
        # Register YOUR personalized agents
        console.print("[cyan]Initializing your personalized agents...[/cyan]")
        
        if "researcher" not in registry:
            researcher = PersonalizedResearchAgent(
                agent_id="researcher",
                role="researcher",
                description=f"Research specialist acting as {cognitive_profile.user_id}",
                cognitive_profile=cognitive_profile,
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(researcher)
            console.print("  ✓ Research Agent (your research style)")
        
        if "coder" not in registry:
            coder = PersonalizedCodeAgent(
                agent_id="coder",
                role="coder",
                description=f"Coding specialist acting as {cognitive_profile.user_id}",
                cognitive_profile=cognitive_profile,
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(coder)
            console.print("  ✓ Code Agent (your coding style)")
        
        if "writer" not in registry:
            writer = PersonalizedWriterAgent(
                agent_id="writer",
                role="writer",
                description=f"Writing specialist acting as {cognitive_profile.user_id}",
                cognitive_profile=cognitive_profile,
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(writer)
            console.print("  ✓ Writer Agent (your writing style)")
        
        if "generalist" not in registry:
            generalist = PersonalizedGeneralistAgent(
                agent_id="generalist",
                role="generalist",
                description=f"General assistant acting as {cognitive_profile.user_id}",
                cognitive_profile=cognitive_profile,
                llm_provider=llm_provider,
                skills_manager=skills_manager
            )
            registry.register(generalist)
            console.print("  ✓ Generalist Agent (your conversational style)")
        
        # Create router with LLM enhancement
        router = TaskRouter(
            registry,
            default_agent_id="generalist",
            llm_provider=llm_provider,
            use_llm_routing=True
        )
        
        console.print(f"\n[bold green]All agents ready![/bold green]")
        console.print(f"[dim]Cognitive Profile: {cognitive_profile.user_id}[/dim]")
        console.print(f"[dim]Writing Tone: {cognitive_profile.writing_style.tone}[/dim]\n")
        console.print("[dim]Type 'exit' to quit, 'agents' to list, 'stats' for analytics[/dim]\n")
        
        # Interactive loop
        session = PromptSession(history=InMemoryHistory())
        
        while True:
            try:
                user_input = session.prompt("\n[You] > ")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() == 'exit':
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                
                if user_input.lower() == 'agents':
                    agents = registry.list_all()
                    console.print(f"\n[bold]Your Personalized Agents:[/bold]")
                    for agent in agents:
                        console.print(f"  • {agent.agent_id} - {agent.description}")
                    continue
                
                if user_input.lower() == 'stats':
                    stats = router.get_routing_stats()
                    console.print(f"\n[bold]Routing Statistics:[/bold]")
                    console.print(f"  Total routes: {stats['total_routes']}")
                    console.print(f"  Average confidence: {stats['average_confidence']:.2f}")
                    console.print(f"  Most used: {stats['most_used_agent']}")
                    console.print(f"\n[bold]Agent usage:[/bold]")
                    for agent_id, count in stats['agent_usage'].items():
                        console.print(f"  • {agent_id}: {count}")
                    continue
                
                # Route and execute
                agent = router.route_task(user_input)
                if not agent:
                    console.print("[red]No suitable agent found.[/red]")
                    continue
                
                console.print(f"[dim]→ Routing to {agent.agent_id}[/dim]")
                
                result = agent.handle_task(user_input)
                
                if result.success:
                    console.print(f"\n[bold green]{agent.role.title()}:[/bold green]")
                    console.print(Panel(result.result, border_style="green"))
                else:
                    console.print(f"[red]Error: {result.error}[/red]")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Use 'exit' to quit.[/yellow]")
            except EOFError:
                break
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    cli()
