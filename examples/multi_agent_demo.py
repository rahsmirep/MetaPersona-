"""
Multi-Agent System Demo
Demonstrates the power of multiple specialized agents working together.
"""
import asyncio
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.agent_registry import AgentRegistry
from src.task_router import TaskRouter
from src.specialized_agents import ResearchAgent, CodeAgent, WriterAgent, GeneralistAgent
from src.llm_provider import get_llm_provider
from src.skills import SkillManager

console = Console()


async def demo_basic_routing():
    """Demonstrate basic task routing to different agents."""
    console.print(Panel(
        "[bold cyan]Demo 1: Basic Task Routing[/bold cyan]\n\n"
        "Watch how different tasks are routed to specialized agents",
        border_style="cyan"
    ))
    
    # Setup
    registry = AgentRegistry(Path("./data"))
    llm_provider = get_llm_provider()
    skills_manager = SkillManager()
    
    # Register agents
    console.print("\n[bold]Registering Agents...[/bold]")
    
    researcher = ResearchAgent(
        agent_id="researcher",
        role="researcher",
        description="Specialized in research, information gathering, and analysis",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(researcher)
    console.print("  ✓ ResearchAgent registered")
    
    coder = CodeAgent(
        agent_id="coder",
        role="coder",
        description="Specialized in coding, debugging, and technical tasks",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(coder)
    console.print("  ✓ CodeAgent registered")
    
    writer = WriterAgent(
        agent_id="writer",
        role="writer",
        description="Specialized in writing, content creation, and communication",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(writer)
    console.print("  ✓ WriterAgent registered")
    
    generalist = GeneralistAgent(
        agent_id="generalist",
        role="generalist",
        description="Handles general tasks and conversations",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(generalist)
    console.print("  ✓ GeneralistAgent registered")
    
    # Create router
    router = TaskRouter(registry, default_agent_id="generalist")
    
    # Test tasks
    test_tasks = [
        "Research the history of artificial intelligence",
        "Write a Python function to calculate fibonacci numbers",
        "Draft a professional email thanking a client",
        "What's the weather like today?"
    ]
    
    console.print(f"\n[bold]Testing {len(test_tasks)} different tasks...[/bold]\n")
    
    for i, task in enumerate(test_tasks, 1):
        console.print(f"[cyan]Task {i}:[/cyan] {task}")
        
        # Get routing explanation
        explanation = router.explain_routing(task)
        recommended = explanation['recommended_agent']
        confidence = explanation['recommended_confidence']
        
        console.print(f"  → Routed to: [bold]{recommended}[/bold] (confidence: {confidence:.2f})")
        
        # Execute task
        result = await router.execute_task(task)
        
        if result.success:
            response = str(result.result)[:150]  # Truncate for display
            console.print(f"  ✓ Result: {response}...\n")
        else:
            console.print(f"  ✗ Error: {result.error}\n")


async def demo_routing_explanation():
    """Demonstrate routing decision explanation."""
    console.print(Panel(
        "[bold cyan]Demo 2: Routing Decision Explanation[/bold cyan]\n\n"
        "See how the router analyzes tasks and selects agents",
        border_style="cyan"
    ))
    
    # Setup
    registry = AgentRegistry(Path("./data"))
    llm_provider = get_llm_provider()
    skills_manager = SkillManager()
    
    # Register agents
    registry.register(ResearchAgent(
        agent_id="researcher",
        role="researcher",
        description="Research specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    registry.register(CodeAgent(
        agent_id="coder",
        role="coder",
        description="Coding specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    registry.register(WriterAgent(
        agent_id="writer",
        role="writer",
        description="Writing specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    
    router = TaskRouter(registry, min_confidence=0.5)
    
    # Analyze a task
    task = "Research quantum computing and write a summary"
    console.print(f"\n[bold]Task:[/bold] {task}\n")
    
    explanation = router.explain_routing(task)
    
    console.print(f"[bold]Recommended Agent:[/bold] {explanation['recommended_agent']}")
    console.print(f"[bold]Confidence:[/bold] {explanation['recommended_confidence']:.2f}")
    console.print(f"[bold]Min Threshold:[/bold] {explanation['min_confidence']}\n")
    
    # Show all candidates
    table = Table(title="All Candidate Agents")
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


async def demo_agent_collaboration():
    """Demonstrate multiple agents working on a complex task."""
    console.print(Panel(
        "[bold cyan]Demo 3: Agent Collaboration[/bold cyan]\n\n"
        "Multiple agents working together on a complex project",
        border_style="cyan"
    ))
    
    # Setup
    registry = AgentRegistry(Path("./data"))
    llm_provider = get_llm_provider()
    skills_manager = SkillManager()
    
    # Register agents
    researcher = ResearchAgent(
        agent_id="researcher",
        role="researcher",
        description="Research specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(researcher)
    
    coder = CodeAgent(
        agent_id="coder",
        role="coder",
        description="Coding specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(coder)
    
    writer = WriterAgent(
        agent_id="writer",
        role="writer",
        description="Writing specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    )
    registry.register(writer)
    
    router = TaskRouter(registry)
    
    # Complex project: Build a web scraper
    console.print("\n[bold]Project:[/bold] Build a web scraper with documentation\n")
    
    subtasks = [
        ("Research best practices for web scraping in Python", "researcher"),
        ("Write Python code for a simple web scraper", "coder"),
        ("Write documentation for the web scraper", "writer")
    ]
    
    results = []
    
    for i, (task, preferred_role) in enumerate(subtasks, 1):
        console.print(f"[cyan]Step {i}:[/cyan] {task}")
        
        # Route to preferred role
        result = await router.execute_task(task, preferred_role=preferred_role)
        
        if result.success:
            results.append(result.result)
            agent_id = result.metadata.get('agent_id', 'unknown')
            console.print(f"  ✓ Completed by {agent_id}")
        else:
            console.print(f"  ✗ Failed: {result.error}")
        
        console.print()
    
    console.print("[bold green]✓ Project completed![/bold green]")
    console.print(f"\n[dim]Generated {len(results)} deliverables[/dim]")


async def demo_routing_stats():
    """Demonstrate routing statistics and analytics."""
    console.print(Panel(
        "[bold cyan]Demo 4: Routing Statistics[/bold cyan]\n\n"
        "View analytics about agent usage and routing decisions",
        border_style="cyan"
    ))
    
    # Setup
    registry = AgentRegistry(Path("./data"))
    llm_provider = get_llm_provider()
    skills_manager = SkillManager()
    
    # Register agents
    registry.register(ResearchAgent(
        agent_id="researcher",
        role="researcher",
        description="Research specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    registry.register(CodeAgent(
        agent_id="coder",
        role="coder",
        description="Coding specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    registry.register(GeneralistAgent(
        agent_id="generalist",
        role="generalist",
        description="General tasks",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    
    router = TaskRouter(registry, default_agent_id="generalist")
    
    # Execute various tasks
    console.print("\n[bold]Executing various tasks...[/bold]\n")
    
    tasks = [
        "Search for Python tutorials",
        "Write a hello world program",
        "What time is it?",
        "Research machine learning",
        "Debug this code",
        "Tell me a joke"
    ]
    
    for task in tasks:
        await router.execute_task(task)
        console.print(f"  • Routed: {task[:40]}...")
    
    # Show statistics
    console.print("\n[bold]Routing Statistics:[/bold]\n")
    
    stats = router.get_routing_stats()
    
    console.print(f"Total routes: {stats['total_routes']}")
    console.print(f"Average confidence: {stats['average_confidence']:.2f}")
    console.print(f"Most used agent: {stats['most_used_agent']}")
    
    console.print("\n[bold]Agent Usage:[/bold]")
    table = Table()
    table.add_column("Agent", style="cyan")
    table.add_column("Times Used", style="yellow")
    
    for agent_id, count in stats['agent_usage'].items():
        table.add_row(agent_id, str(count))
    
    console.print(table)
    
    # Recent routes
    console.print("\n[bold]Recent Routes:[/bold]")
    recent = router.get_recent_routes(limit=5)
    
    for route in recent:
        console.print(f"  • {route['task'][:50]}... → {route['selected_agent_id']} ({route['confidence']:.2f})")


async def demo_agent_status():
    """Show detailed agent status information."""
    console.print(Panel(
        "[bold cyan]Demo 5: Agent Status & Capabilities[/bold cyan]\n\n"
        "View detailed information about each agent",
        border_style="cyan"
    ))
    
    # Setup
    registry = AgentRegistry(Path("./data"))
    llm_provider = get_llm_provider()
    skills_manager = SkillManager()
    
    # Register agents
    registry.register(ResearchAgent(
        agent_id="researcher",
        role="researcher",
        description="Research specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    registry.register(CodeAgent(
        agent_id="coder",
        role="coder",
        description="Coding specialist",
        llm_provider=llm_provider,
        skills_manager=skills_manager
    ))
    
    console.print("\n[bold]Agent Details:[/bold]\n")
    
    for agent in registry.list_all():
        status = agent.get_status()
        
        console.print(Panel(
            f"[bold]Role:[/bold] {status['role']}\n"
            f"[bold]Description:[/bold] {status['description']}\n"
            f"[bold]Capabilities:[/bold] {status['capabilities'][0]['name']} (+{len(status['capabilities'])-1} more)\n"
            f"[bold]Skills Available:[/bold] {status['skills_count']}\n"
            f"[bold]Total Interactions:[/bold] {status['interactions_count']}",
            title=f"Agent: {status['agent_id']}",
            border_style="cyan"
        ))
        
        console.print("\n[bold]Capabilities:[/bold]")
        for cap in status['capabilities']:
            console.print(f"  • {cap['name']}: {cap['description']} (confidence: {cap['confidence']})")
        console.print()


async def main():
    """Run all demos."""
    console.print(Panel(
        "[bold cyan]MetaPersona Multi-Agent System Demo[/bold cyan]\n\n"
        "Demonstrating intelligent task routing and agent collaboration",
        title="🤖 Multi-Agent Demo",
        border_style="cyan"
    ))
    
    demos = [
        ("Basic Task Routing", demo_basic_routing),
        ("Routing Decision Explanation", demo_routing_explanation),
        ("Agent Collaboration", demo_agent_collaboration),
        ("Routing Statistics", demo_routing_stats),
        ("Agent Status & Capabilities", demo_agent_status)
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        console.print(f"\n{'='*70}\n")
        await demo_func()
        
        if i < len(demos):
            input("\nPress Enter to continue to next demo...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        import traceback
        traceback.print_exc()
