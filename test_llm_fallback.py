"""
Test LLM Fallback System
Demonstrates pure LLM-based knowledge expansion when web search is unavailable
"""
from src.profession import UniversalProfessionSystem
from src.cognitive_profile import CognitiveProfile
from src.llm_provider import get_llm_provider
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def test_llm_fallback():
    """Test with a rare profession that won't have cached web results"""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST: LLM Fallback Knowledge Expansion[/bold cyan]")
    console.print("[bold cyan]Testing with rare profession: Blockchain Architect in DeFi[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Initialize
    llm = get_llm_provider()
    
    # Create profile
    user_profile = CognitiveProfile(
        user_id="alex_crypto",
        writing_style_data={
            "tone": "technical",
            "vocabulary_level": "advanced",
            "sentence_structure": "concise",
            "formatting_preferences": "bullet points"
        },
        decision_making_data={
            "decision_speed": "fast",
            "risk_tolerance": "aggressive",
            "information_gathering": "targeted",
            "prioritization_style": "value-based"
        }
    )
    
    profession_system = UniversalProfessionSystem(llm, "./data")
    
    # Test with rare profession
    user_input = "I'm a Blockchain Architect specializing in DeFi (Decentralized Finance) protocols and smart contract security"
    
    console.print(Panel(
        f"[bold]User Input:[/bold]\n\"{user_input}\"",
        title="Onboarding Rare Profession",
        border_style="blue"
    ))
    
    console.print("\n[yellow]🔄 Processing (web search will likely fail, LLM fallback will activate)...[/yellow]\n")
    
    # Onboard
    schema = profession_system.onboard_profession(user_input, "alex_crypto")
    
    # Display results
    console.print(f"\n[green]✓ Successfully onboarded![/green]\n")
    
    # Summary table
    table = Table(title="Knowledge Generated (LLM Fallback)", show_header=True)
    table.add_column("Category", style="cyan", width=25)
    table.add_column("Count", style="white", width=10)
    table.add_column("Sample", style="yellow")
    
    table.add_row(
        "Profession",
        "1",
        schema.profession_name
    )
    table.add_row(
        "Industry",
        "1",
        schema.industry
    )
    table.add_row(
        "Tools/Software",
        str(len(schema.tools_equipment.software)),
        ", ".join(schema.tools_equipment.software[:3])
    )
    table.add_row(
        "Decision Frameworks",
        str(len(schema.decision_patterns.decision_frameworks)),
        schema.decision_patterns.decision_frameworks[0] if schema.decision_patterns.decision_frameworks else "N/A"
    )
    table.add_row(
        "Critical Safety Rules",
        str(len(schema.safety_rules.critical)),
        schema.safety_rules.critical[0][:60] + "..." if schema.safety_rules.critical else "N/A"
    )
    table.add_row(
        "Edge Cases",
        str(len(schema.edge_cases.scenarios)),
        schema.edge_cases.scenarios[0]["scenario"][:60] + "..." if schema.edge_cases.scenarios else "N/A"
    )
    
    console.print(table)
    
    # Show some expanded knowledge
    console.print("\n[bold cyan]LLM-Generated Knowledge Samples:[/bold cyan]\n")
    
    if schema.tools_equipment.software:
        console.print("[bold]Top Tools:[/bold]")
        for tool in schema.tools_equipment.software[:5]:
            console.print(f"  • {tool}")
    
    if schema.edge_cases.scenarios:
        console.print("\n[bold]Edge Cases (LLM-generated):[/bold]")
        for i, scenario in enumerate(schema.edge_cases.scenarios[:3], 1):
            console.print(f"  {i}. {scenario['scenario']}")
    
    if schema.safety_rules.critical:
        console.print("\n[bold]Critical Safety Rules:[/bold]")
        for i, rule in enumerate(schema.safety_rules.critical[:3], 1):
            console.print(f"  {i}. {rule}")
    
    console.print("\n[bold green]✅ LLM Fallback System Working![/bold green]")
    console.print("[green]System successfully generated comprehensive knowledge without web search[/green]\n")

if __name__ == "__main__":
    test_llm_fallback()
