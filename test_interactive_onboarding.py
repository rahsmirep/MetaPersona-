"""
Test Interactive Onboarding - Demo Mode
Shows what interactive onboarding can do
"""
from src.profession import UniversalProfessionSystem
from src.llm_provider import get_llm_provider
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def demo_interactive_features():
    """
    Demonstrate interactive onboarding features.
    For actual interactive use, run with: interactive=True
    """
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]Interactive Onboarding System - Feature Demo[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Initialize
    llm = get_llm_provider()
    profession_system = UniversalProfessionSystem(llm, "./data")
    
    # Example profession
    user_input = "I'm a Machine Learning Engineer at a tech startup focused on NLP applications"
    
    console.print(Panel(
        f"[bold]User Input:[/bold]\n{user_input}",
        title="Step 1: Initial Input",
        border_style="blue"
    ))
    
    console.print("\n[yellow]Running non-interactive onboarding for demo...[/yellow]\n")
    
    # Run without interactive mode for demo
    schema = profession_system.onboard_profession(
        user_input,
        "ml_engineer_demo",
        interactive=False
    )
    
    # Show what was detected
    console.print("\n" + "═" * 70)
    console.print("[bold cyan]Detected Information (What Interactive Mode Shows You)[/bold cyan]")
    console.print("═" * 70 + "\n")
    
    # Basic Info Table
    basic_info = Table(title="Basic Information", show_header=True)
    basic_info.add_column("Field", style="cyan", width=20)
    basic_info.add_column("Detected Value", style="yellow")
    basic_info.add_column("Interactive Action", style="green")
    
    basic_info.add_row("Profession", schema.profession_name, "✓ Confirm or edit")
    basic_info.add_row("Industry", schema.industry, "✓ Confirm or edit")
    basic_info.add_row("Work Setting", schema.environment.work_setting.value, "✓ Confirm")
    basic_info.add_row("Team Structure", schema.environment.team_structure.value, "✓ Confirm")
    
    console.print(basic_info)
    console.print()
    
    # Responsibilities
    console.print("[bold]Primary Responsibilities Detected:[/bold]")
    for i, resp in enumerate(schema.role_definition.primary_responsibilities[:5], 1):
        console.print(f"  {i}. {resp}")
    console.print("  [green]→ Interactive: Add more responsibilities[/green]\n")
    
    # Tools
    console.print("[bold]Tools & Technologies Detected:[/bold]")
    for i, tool in enumerate(schema.tools_equipment.software[:5], 1):
        console.print(f"  {i}. {tool}")
    console.print("  [green]→ Interactive: Add missing tools[/green]\n")
    
    # Safety Rules
    console.print("[bold]Critical Safety Rules Generated:[/bold]")
    for i, rule in enumerate(schema.safety_rules.critical[:3], 1):
        console.print(f"  {i}. {rule}")
    if len(schema.safety_rules.critical) > 3:
        console.print(f"  ... and {len(schema.safety_rules.critical) - 3} more")
    console.print("  [green]→ Interactive: Review all & add profession-specific rules[/green]\n")
    
    # Interactive Features
    console.print("\n" + "═" * 70)
    console.print("[bold cyan]Interactive Mode Features[/bold cyan]")
    console.print("═" * 70 + "\n")
    
    features = Table(show_header=True)
    features.add_column("Step", style="cyan", width=8)
    features.add_column("Feature", style="yellow", width=30)
    features.add_column("Benefit", style="green")
    
    features.add_row(
        "1",
        "Confirm Basic Info",
        "Correct any misinterpretations immediately"
    )
    features.add_row(
        "2",
        "Refine Responsibilities",
        "Add specific duties unique to your role"
    )
    features.add_row(
        "3",
        "Update Tools List",
        "Ensure all critical tools are captured"
    )
    features.add_row(
        "4",
        "Review Safety Rules",
        "Add profession-specific compliance requirements"
    )
    features.add_row(
        "5",
        "Add Edge Cases",
        "Document unusual scenarios you encounter"
    )
    features.add_row(
        "6",
        "Specify Constraints",
        "Add industry regulations (GDPR, HIPAA, etc.)"
    )
    
    console.print(features)
    
    console.print("\n[bold yellow]To use interactive mode:[/bold yellow]")
    console.print("  [dim]profession_system.onboard_profession(input, user_id, interactive=True)[/dim]\n")
    
    console.print("[bold green]✅ Demo Complete![/bold green]")
    console.print(f"[green]Generated schema with {len(schema.safety_rules.critical)} safety rules[/green]\n")
    
    console.print("[bold cyan]Try it yourself:[/bold cyan]")
    console.print("  [dim]Run this test manually in your terminal to experience full interactivity[/dim]\n")

if __name__ == "__main__":
    demo_interactive_features()
