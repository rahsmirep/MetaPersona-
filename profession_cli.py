"""
Profession Management CLI for MetaPersona
Add, edit, remove, and list professions from the command line.
"""
import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from src.llm_provider import get_llm_provider
from src.profession.profession_system import UniversalProfessionSystem

console = Console()

@click.group()
def profession():
    """Profession management commands."""
    pass

@profession.command()
def list():
    """List all professions."""
    system = UniversalProfessionSystem(get_llm_provider(), Path("./data"))
    professions = system.list_professions()
    if not professions:
        console.print("[yellow]No professions found.[/yellow]")
        return
    table = Table(title="Available Professions")
    table.add_column("ID", style="cyan")
    table.add_column("Profession", style="green")
    table.add_column("Industry", style="magenta")
    table.add_column("Last Updated", style="yellow")
    for p in professions:
        table.add_row(p["profession_id"], p["profession_name"], p["industry"], p["last_updated"])
    console.print(table)

@profession.command()
@click.argument('profession_id')
def show(profession_id):
    """Show details for a profession."""
    system = UniversalProfessionSystem(get_llm_provider(), Path("./data"))
    summary = system.get_profession_summary(profession_id)
    if not summary:
        console.print(f"[red]Profession '{profession_id}' not found.[/red]")
        return
    console.print(summary)

@profession.command()
@click.argument('profession_id')
def remove(profession_id):
    """Remove a profession schema."""
    system = UniversalProfessionSystem(get_llm_provider(), Path("./data"))
    prof_dir = system.profession_dir
    matches = list(prof_dir.glob(f"{profession_id}*.json"))
    if not matches:
        console.print(f"[red]Profession '{profession_id}' not found.[/red]")
        return
    for f in matches:
        f.unlink()
        console.print(f"[green]Deleted:[/green] {f.name}")
    console.print(f"[bold]Profession '{profession_id}' removed.[/bold]")

@profession.command()
@click.argument('user_input')
@click.argument('user_id')
@click.option('--interactive', is_flag=True, help='Use interactive onboarding')
def add(user_input, user_id, interactive):
    """Add a new profession from description."""
    system = UniversalProfessionSystem(get_llm_provider(), Path("./data"))
    schema = system.onboard_profession(user_input, user_id, interactive=interactive)
    console.print(f"[green]Profession '{schema.profession_name}' added for user '{user_id}'.[/green]")

if __name__ == "__main__":
    profession()
