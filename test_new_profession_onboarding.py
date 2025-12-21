"""
Test: Onboard a completely new profession from scratch
Demonstrates UPUS automatically understanding and creating profession expert
"""
from src.profession import UniversalProfessionSystem
from src.cognitive_profile import CognitiveProfile
from src.llm_provider import get_llm_provider
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import json

console = Console()

def test_new_profession_onboarding():
    """Test onboarding a Data Scientist in Healthcare"""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST: Onboard New Profession - Data Scientist (Healthcare)[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Initialize system
    llm = get_llm_provider()
    
    # Create a new user profile for a Data Scientist
    console.print("[yellow]Creating user profile...[/yellow]")
    data_scientist_profile = CognitiveProfile(
        user_id="sarah_chen",
        writing_style_data={
            "tone": "analytical",
            "vocabulary_level": "technical",
            "sentence_structure": "structured",
            "formatting_preferences": "bullet points with data"
        },
        decision_making_data={
            "decision_speed": "methodical",
            "risk_tolerance": "data-driven",
            "information_gathering": "comprehensive",
            "prioritization_style": "impact-based"
        }
    )
    console.print("[green]✓ Profile created for sarah_chen[/green]\n")
    
    # Initialize profession system
    profession_system = UniversalProfessionSystem(llm, "./data")
    
    # Simulate user saying their profession
    user_input = "I'm a Senior Data Scientist working in the healthcare industry at a mid-sized biotech company"
    
    console.print(Panel(
        f"[bold]User Input:[/bold]\n\"{user_input}\"",
        title="Onboarding",
        border_style="blue"
    ))
    
    # Onboard the profession
    console.print("\n[yellow]🔄 Interpreting profession...[/yellow]")
    schema = profession_system.onboard_profession(user_input, "sarah_chen")
    
    # Display what was understood
    console.print(f"\n[green]✓ Successfully interpreted profession![/green]\n")
    
    # Show extracted information
    info_table = Table(title="Extracted Profession Information", show_header=True)
    info_table.add_column("Attribute", style="cyan", width=25)
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Profession", schema.profession_name)
    info_table.add_row("Industry", schema.industry)
    info_table.add_row("Work Setting", schema.environment.work_setting.value)
    info_table.add_row("Team Structure", schema.environment.team_structure.value)
    info_table.add_row("Primary Responsibilities", f"{len(schema.role_definition.primary_responsibilities)} identified")
    info_table.add_row("Tools/Software", f"{len(schema.tools_equipment.software)} tools")
    info_table.add_row("Terminology", f"{len(schema.terminology.jargon)} jargon terms, {len(schema.terminology.acronyms)} acronyms")
    info_table.add_row("Decision Frameworks", f"{len(schema.decision_patterns.decision_frameworks)} frameworks")
    info_table.add_row("Safety Rules", f"{len(schema.safety_rules.critical)} critical rules")
    
    console.print(info_table)
    
    # Show some specific examples
    console.print("\n[bold cyan]Sample Knowledge Generated:[/bold cyan]\n")
    
    console.print(f"[bold]Top 5 Tools:[/bold]")
    for tool in schema.tools_equipment.software[:5]:
        console.print(f"  • {tool}")
    
    console.print(f"\n[bold]Sample Jargon Terms:[/bold]")
    for term, definition in list(schema.terminology.jargon.items())[:3]:
        console.print(f"  • {term}: {definition}")
    
    console.print(f"\n[bold]Decision Frameworks:[/bold]")
    for framework in schema.decision_patterns.decision_frameworks[:3]:
        console.print(f"  • {framework}")
    
    console.print(f"\n[bold]Critical Safety Rules:[/bold]")
    for rule in schema.safety_rules.critical[:3]:
        console.print(f"  • {rule}")
    
    # Now test if the profession expert can answer questions
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]TEST: Query the Profession Expert[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Load the profession expert
    from src.personalized_agents import PersonalizedProfessionAgent
    
    data_scientist_expert = PersonalizedProfessionAgent(
        agent_id="data_scientist_expert",
        role=f"{schema.profession_name} Expert",
        description=f"Expert {schema.profession_name} in {schema.industry}",
        cognitive_profile=data_scientist_profile,
        llm_provider=llm,
        profession_schema=schema
    )
    
    # Ask a profession-specific question
    query = "What statistical methods should I use to validate our new patient outcome prediction model?"
    
    console.print(Panel(
        f"[bold]Query:[/bold]\n{query}",
        title="Testing Profession Expert",
        border_style="blue"
    ))
    
    console.print("\n[yellow]Processing...[/yellow]\n")
    
    result = data_scientist_expert.handle_task(query)
    
    # Display response
    console.print(Panel(
        result.result,
        title=f"Response from {schema.profession_name} Expert",
        border_style="green"
    ))
    
    # Show metadata
    console.print("\n[bold]Metadata:[/bold]")
    for key, value in result.metadata.items():
        if key == "knowledge_gaps":
            console.print(f"  • {key}: {len(value)} gaps identified")
        elif key == "decision_factors":
            console.print(f"  • {key}: {value.get('decision_type', 'N/A')}, risk={value.get('risk_level', 'N/A')}")
        else:
            console.print(f"  • {key}: {value}")
    
    console.print("\n[bold green]✅ Test Complete![/bold green]")
    console.print("[green]System successfully onboarded new profession and created working expert![/green]\n")

if __name__ == "__main__":
    test_new_profession_onboarding()
