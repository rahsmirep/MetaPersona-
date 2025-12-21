"""
Interactive Onboarding Module
Provides conversational refinement of profession schemas with user feedback
"""
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from .schema import ProfessionSchema, SafetyRules

console = Console()


class InteractiveOnboarding:
    """Handles interactive refinement of profession schemas."""
    
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def refine_schema(self, schema: ProfessionSchema) -> ProfessionSchema:
        """
        Interactive refinement of schema with user input.
        
        Args:
            schema: Initial schema to refine
            
        Returns:
            Refined schema with user confirmations/edits
        """
        console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]")
        console.print("[bold cyan]Interactive Onboarding - Let's refine your profile[/bold cyan]")
        console.print("[bold cyan]═══════════════════════════════════════════════════════════════[/bold cyan]\n")
        
        # Step 1: Confirm basic info
        schema = self._confirm_basic_info(schema)
        
        # Step 2: Review and refine responsibilities
        schema = self._refine_responsibilities(schema)
        
        # Step 3: Review tools and add missing ones
        schema = self._refine_tools(schema)
        
        # Step 4: Review safety rules (CRITICAL)
        schema = self._refine_safety_rules(schema)
        
        # Step 5: Add any missing context
        schema = self._gather_additional_context(schema)
        
        console.print("\n[bold green]✅ Interactive onboarding complete![/bold green]\n")
        
        return schema
    
    def _confirm_basic_info(self, schema: ProfessionSchema) -> ProfessionSchema:
        """Confirm and refine basic profession information."""
        console.print("[bold]Step 1: Basic Information[/bold]\n")
        
        # Show what was detected
        info_table = Table(show_header=False, box=None)
        info_table.add_column("Field", style="cyan")
        info_table.add_column("Value", style="yellow")
        
        info_table.add_row("Profession", schema.profession_name)
        info_table.add_row("Industry", schema.industry)
        info_table.add_row("Work Setting", schema.environment.work_setting.value)
        info_table.add_row("Team Structure", schema.environment.team_structure.value)
        
        console.print(info_table)
        console.print()
        
        # Ask for confirmation
        if not Confirm.ask("Is this information correct?", default=True):
            # Allow corrections
            new_profession = Prompt.ask("Profession name", default=schema.profession_name)
            new_industry = Prompt.ask("Industry", default=schema.industry)
            
            schema.profession_name = new_profession
            schema.industry = new_industry
            
            console.print("[green]✓ Updated[/green]\n")
        else:
            console.print("[green]✓ Confirmed[/green]\n")
        
        return schema
    
    def _refine_responsibilities(self, schema: ProfessionSchema) -> ProfessionSchema:
        """Review and refine primary responsibilities."""
        console.print("[bold]Step 2: Primary Responsibilities[/bold]\n")
        
        if schema.role_definition.primary_responsibilities:
            console.print("We identified these responsibilities:\n")
            for i, resp in enumerate(schema.role_definition.primary_responsibilities, 1):
                console.print(f"  {i}. {resp}")
            console.print()
        
        # Ask if anything is missing
        if Confirm.ask("Would you like to add any responsibilities?", default=False):
            while True:
                new_resp = Prompt.ask("Add a responsibility (or press Enter to finish)", default="")
                if not new_resp:
                    break
                schema.role_definition.primary_responsibilities.append(new_resp)
                console.print("[green]✓ Added[/green]")
            console.print()
        
        return schema
    
    def _refine_tools(self, schema: ProfessionSchema) -> ProfessionSchema:
        """Review and refine tools/software."""
        console.print("[bold]Step 3: Tools & Technologies[/bold]\n")
        
        if schema.tools_equipment.software:
            console.print("Tools you use:\n")
            for i, tool in enumerate(schema.tools_equipment.software[:10], 1):
                console.print(f"  {i}. {tool}")
            console.print()
        
        # Ask for missing tools
        if Confirm.ask("Any important tools missing?", default=False):
            console.print("[dim]Examples: programming languages, frameworks, platforms, software[/dim]")
            while True:
                new_tool = Prompt.ask("Add a tool (or press Enter to finish)", default="")
                if not new_tool:
                    break
                schema.tools_equipment.software.append(new_tool)
                console.print("[green]✓ Added[/green]")
            console.print()
        
        return schema
    
    def _refine_safety_rules(self, schema: ProfessionSchema) -> ProfessionSchema:
        """Review and refine critical safety rules."""
        console.print("[bold]Step 4: Safety & Compliance Rules (IMPORTANT)[/bold]\n")
        
        console.print("[yellow]These are critical rules to prevent legal/ethical violations.[/yellow]\n")
        
        if schema.safety_rules.critical:
            console.print("[bold]Critical Rules:[/bold]\n")
            for i, rule in enumerate(schema.safety_rules.critical[:5], 1):
                console.print(f"  {i}. {rule}")
            
            if len(schema.safety_rules.critical) > 5:
                console.print(f"  ... and {len(schema.safety_rules.critical) - 5} more")
            console.print()
        
        # Ask if they want to review all
        if len(schema.safety_rules.critical) > 5:
            if Confirm.ask("Review all safety rules?", default=False):
                console.print()
                for i, rule in enumerate(schema.safety_rules.critical, 1):
                    console.print(f"  {i}. {rule}")
                console.print()
        
        # Ask if they want to add profession-specific rules
        if Confirm.ask("Add any profession-specific safety rules?", default=False):
            console.print("[dim]Examples: regulatory requirements, ethical guidelines, legal constraints[/dim]")
            while True:
                new_rule = Prompt.ask("Add a critical rule (or press Enter to finish)", default="")
                if not new_rule:
                    break
                if not new_rule.startswith("NEVER") and not new_rule.startswith("ALWAYS"):
                    new_rule = f"ALWAYS {new_rule}"
                schema.safety_rules.critical.append(new_rule)
                console.print("[green]✓ Added[/green]")
            console.print()
        
        return schema
    
    def _gather_additional_context(self, schema: ProfessionSchema) -> ProfessionSchema:
        """Gather any additional context the user wants to provide."""
        console.print("[bold]Step 5: Additional Context[/bold]\n")
        
        # Ask about edge cases
        if Confirm.ask("Any unusual scenarios or edge cases you often encounter?", default=False):
            console.print("[dim]Describe situations that are rare but important to handle correctly[/dim]")
            while True:
                scenario = Prompt.ask("Describe a scenario (or press Enter to finish)", default="")
                if not scenario:
                    break
                schema.edge_cases.scenarios.append({
                    "scenario": scenario,
                    "response": "Requires careful analysis and appropriate action"
                })
                console.print("[green]✓ Added[/green]")
            console.print()
        
        # Ask about industry-specific constraints
        if Confirm.ask("Any industry-specific regulations or constraints we should know about?", default=False):
            console.print("[dim]Examples: GDPR, HIPAA, SOX, industry certifications[/dim]")
            while True:
                constraint = Prompt.ask("Add a constraint (or press Enter to finish)", default="")
                if not constraint:
                    break
                schema.constraints.regulatory.append(constraint)
                console.print("[green]✓ Added[/green]")
            console.print()
        
        return schema
    
    def generate_clarifying_questions(self, schema: ProfessionSchema) -> List[str]:
        """
        Use LLM to generate smart follow-up questions based on schema.
        
        Args:
            schema: Current schema state
            
        Returns:
            List of clarifying questions
        """
        prompt = f"""You are onboarding a {schema.profession_name} in the {schema.industry} industry.

Based on what we know so far, generate 3-5 clarifying questions that would help us better understand:
1. Their daily workflow and responsibilities
2. Critical tools or technologies they use
3. Important safety rules or compliance requirements for their role
4. Common challenges or edge cases they face

Current knowledge:
- Responsibilities: {len(schema.role_definition.primary_responsibilities)} identified
- Tools: {len(schema.tools_equipment.software)} tools
- Safety rules: {len(schema.safety_rules.critical)} critical rules

Generate questions in JSON format:
{{
  "questions": [
    "Question 1?",
    "Question 2?",
    ...
  ]
}}

Focus on gaps in our understanding. Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": "You are an expert at understanding professions and identifying gaps in knowledge."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            import re
            import json
            
            response = self.llm.generate(messages, temperature=0.5)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                return data.get("questions", [])
        except Exception as e:
            console.print(f"[dim]Could not generate questions: {e}[/dim]")
        
        return []
