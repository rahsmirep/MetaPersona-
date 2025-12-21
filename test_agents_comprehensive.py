"""
Comprehensive test of QuestionRouter and all agents
Tests routing logic and agent responses without onboarding new professions
"""
from pathlib import Path
from src.question_router import QuestionRouter
from src.cognitive_profile import ProfileManager
from src.llm_provider import get_llm_provider
from src.personalized_agents import (
    PersonalizedResearchAgent,
    PersonalizedCodeAgent,
    PersonalizedWriterAgent,
    PersonalizedGeneralistAgent,
    PersonalizedProfessionAgent
)
from src.profession import UniversalProfessionSystem
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def test_router_only():
    """Test just the routing logic"""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST 1: Question Router - Routing Logic Only[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    router = QuestionRouter(Path("data/personas"))
    
    test_queries = [
        ("What's the best backtesting framework for trading strategies?", "Should route to Profession Expert"),
        ("How do I optimize my algorithm execution?", "Should route to Profession Expert"),
        ("Write a Python function to calculate moving average", "Should route to Code Agent"),
        ("Research the latest trends in machine learning", "Should route to Research Agent"),
        ("Draft an email to my manager about the project", "Should route to Writer Agent"),
        ("What's the weather like today?", "Should route to Generalist"),
        ("Explain quantitative trading risk management", "Should route to Profession Expert"),
        ("Deploy this app to AWS", "Should route to DevOps domain expert"),
    ]
    
    table = Table(title="Routing Test Results")
    table.add_column("Query", style="cyan", width=50)
    table.add_column("Expected", style="yellow", width=25)
    table.add_column("Routed To", style="green", width=30)
    table.add_column("Confidence", style="magenta", width=10)
    
    for query, expected in test_queries:
        personas, analysis = router.route_question(query)
        
        if personas:
            routed_to = personas[0].get('role', 'Unknown')
            agent_type = personas[0].get('agent_type', 'domain_expert')
            if agent_type == 'profession_expert':
                routed_to = f"✅ {routed_to}"
        else:
            routed_to = "None"
        
        confidence = f"{analysis.confidence:.0%}"
        
        table.add_row(
            query[:47] + "..." if len(query) > 50 else query,
            expected,
            routed_to,
            confidence
        )
    
    console.print(table)
    console.print()


def test_agent_capabilities():
    """Test agent capability detection"""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST 2: Agent Capabilities - can_handle_task() Scoring[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Load profile and LLM
    profile_manager = ProfileManager("data")
    cognitive_profile = profile_manager.load_profile()
    llm = get_llm_provider()
    
    # Create agents
    research = PersonalizedResearchAgent(
        "research_agent",
        "Research Expert",
        "Research and analysis specialist",
        cognitive_profile,
        llm
    )
    
    code = PersonalizedCodeAgent(
        "code_agent",
        "Code Expert",
        "Programming and development specialist",
        cognitive_profile,
        llm
    )
    
    writer = PersonalizedWriterAgent(
        "writer_agent",
        "Writing Expert",
        "Professional writing specialist",
        cognitive_profile,
        llm
    )
    
    generalist = PersonalizedGeneralistAgent(
        "generalist_agent",
        "General Assistant",
        "General purpose assistant",
        cognitive_profile,
        llm
    )
    
    # Load profession expert if exists
    profession_expert = None
    try:
        upus = UniversalProfessionSystem(llm, Path("data"))
        schema = upus.load_profession_schema(cognitive_profile.user_id)
        
        profession_expert = PersonalizedProfessionAgent(
            "profession_expert",
            f"{schema.profession_name} Expert",
            f"Expert in {schema.profession_name}",
            cognitive_profile,
            llm,
            schema
        )
    except:
        console.print("[yellow]⚠ No profession expert found (onboard with: python metapersona.py onboard-profession)[/yellow]\n")
    
    agents = [research, code, writer, generalist]
    if profession_expert:
        agents.insert(0, profession_expert)
    
    test_tasks = [
        "Research machine learning frameworks",
        "Write a Python function for data processing",
        "Draft an email to the team",
        "What's the capital of France?",
        "Analyze trading strategy performance",
        "Backtest my quantitative model",
    ]
    
    for task in test_tasks:
        console.print(f"[bold]Task:[/bold] {task}\n")
        
        scores_table = Table()
        scores_table.add_column("Agent", style="cyan")
        scores_table.add_column("Confidence Score", style="green")
        scores_table.add_column("Assessment", style="yellow")
        
        scores = []
        for agent in agents:
            score = agent.can_handle_task(task)
            scores.append((agent.role, score))
            
            if score >= 0.8:
                assessment = "✅ High confidence"
            elif score >= 0.5:
                assessment = "⚠ Medium confidence"
            else:
                assessment = "❌ Low confidence"
            
            scores_table.add_row(
                agent.role,
                f"{score:.0%}",
                assessment
            )
        
        # Highlight best agent
        best_agent = max(scores, key=lambda x: x[1])
        console.print(scores_table)
        console.print(f"[bold green]→ Best agent: {best_agent[0]} ({best_agent[1]:.0%})[/bold green]\n")


def test_profession_expert_live():
    """Test profession expert with actual query execution"""
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST 3: Profession Expert - Live Query Execution[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Load profile and LLM
    profile_manager = ProfileManager("data")
    cognitive_profile = profile_manager.load_profile()
    llm = get_llm_provider()
    
    try:
        # Load profession expert
        upus = UniversalProfessionSystem(llm, Path("data"))
        schema = upus.load_profession_schema(cognitive_profile.user_id)
        
        profession_expert = PersonalizedProfessionAgent(
            "profession_expert",
            f"{schema.profession_name} Expert",
            f"Expert in {schema.profession_name}",
            cognitive_profile,
            llm,
            schema
        )
        
        console.print(f"[green]✓ Loaded profession expert: {profession_expert.role}[/green]")
        console.print(f"[dim]  Industry: {schema.industry}[/dim]")
        console.print(f"[dim]  Tools: {', '.join(schema.tools_equipment.software[:3])}...[/dim]\n")
        
        # Test query
        test_query = "What are the key risk management practices I should follow?"
        
        console.print(f"[bold]Query:[/bold] {test_query}\n")
        console.print("[yellow]Processing query through profession expert...[/yellow]\n")
        
        result = profession_expert.handle_task(test_query)
        
        if result.success:
            console.print(Panel(
                result.result,
                title=f"Response from {profession_expert.role}",
                border_style="green"
            ))
            
            # Show metadata
            if result.metadata:
                console.print("\n[bold]Metadata:[/bold]")
                for key, value in result.metadata.items():
                    if key not in ['agent_id', 'agent_role']:
                        console.print(f"  • {key}: {value}")
        else:
            console.print(f"[red]❌ Query failed: {result.error}[/red]")
            
    except FileNotFoundError:
        console.print("[red]❌ No profession found. Run: python metapersona.py onboard-profession[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")


if __name__ == "__main__":
    console.print("\n[bold magenta]MetaPersona Agent Testing Suite[/bold magenta]")
    console.print("[dim]Testing QuestionRouter and all agent types[/dim]\n")
    
    # Run tests
    test_router_only()
    
    console.print("\n" + "─" * 80 + "\n")
    
    test_agent_capabilities()
    
    console.print("\n" + "─" * 80 + "\n")
    
    test_profession_expert_live()
    
    console.print("\n[bold green]✅ All tests complete![/bold green]\n")
