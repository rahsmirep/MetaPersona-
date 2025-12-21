"""
Universal Profession Understanding System (UPUS)
Main coordinator for profession-aware AI interactions
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
from .schema import ProfessionSchema
from .onboarding_interpreter import OnboardingInterpreter
from .knowledge_expansion import KnowledgeExpansionLayer
from .reasoning import ProfessionReasoningLayer, ParallelSelfAlignment
from .interactive_onboarding import InteractiveOnboarding
from ..cognitive_profile import CognitiveProfile, ProfileManager
from ..llm_provider import LLMProvider


class UniversalProfessionSystem:
    """Main system coordinating all profession understanding components."""
    
    def __init__(
        self,
        llm_provider: LLMProvider,
        data_dir: Path,
        google_api_key: str = None,
        google_cse_id: str = None
    ):
        self.llm = llm_provider
        self.data_dir = Path(data_dir)
        self.profession_dir = self.data_dir / "professions"
        self.profession_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.onboarding = OnboardingInterpreter(llm_provider)
        self.knowledge_expansion = KnowledgeExpansionLayer(
            llm_provider,
            google_api_key or "",
            google_cse_id or "",
            self.data_dir / "knowledge_cache"
        )
        self.reasoning = ProfessionReasoningLayer(llm_provider)
        self.alignment = ParallelSelfAlignment()
        self.interactive = InteractiveOnboarding(llm_provider)
        
        # Cache
        self.loaded_schemas: Dict[str, ProfessionSchema] = {}
    
    def onboard_profession(
        self,
        user_input: str,
        user_id: str,
        interactive: bool = False
    ) -> ProfessionSchema:
        """
        Onboard a new profession from user description.
        
        Args:
            user_input: Natural language profession description
            user_id: User identifier
            interactive: Whether to ask follow-up questions
            
        Returns:
            ProfessionSchema populated from input
        """
        print("🔍 Analyzing your profession...")
        
        # Step 1: Interpret input
        schema = self.onboarding.interpret(user_input, user_id)
        
        # Step 2: Interactive refinement if requested
        if interactive:
            schema = self.interactive.refine_schema(schema)
        
        # Step 3: Expand high-priority gaps
        print("🌐 Expanding knowledge from web sources...")
        priority_gaps = schema.knowledge_confidence.needs_expansion[:3]
        if priority_gaps:
            schema = self.knowledge_expansion.expand_schema(schema, priority_gaps)
        
        # Step 4: Generate comprehensive safety rules (CRITICAL)
        print("🔒 Generating safety and compliance rules...")
        if len(schema.safety_rules.critical) < 5:  # If insufficient safety rules
            # Try loading from template first
            template_safety = self.knowledge_expansion.load_safety_template(
                schema.profession_name,
                schema.industry
            )
            
            if template_safety:
                print(f"   ✓ Loaded from template library")
                schema.safety_rules = template_safety
            else:
                # Generate using LLM
                print(f"   🤖 Generating with LLM (6-question framework)...")
                enhanced_safety = self.knowledge_expansion.generate_comprehensive_safety_rules(schema)
                schema.safety_rules = enhanced_safety
                
                # Save as template for future use
                self.knowledge_expansion.save_safety_template(
                    schema.profession_name,
                    schema.industry,
                    enhanced_safety
                )
        
        # Step 5: Save schema
        self.save_profession_schema(schema)
        
        print(f"✅ Profession schema created: {schema.profession_name}")
        print(f"   - {len(schema.role_definition.primary_responsibilities)} responsibilities")
        print(f"   - {len(schema.tools_equipment.software)} tools")
        print(f"   - {len(schema.safety_rules.critical)} critical rules")
        
        return schema
    
    def load_profession_schema(self, user_id: str) -> Optional[ProfessionSchema]:
        """Load profession schema for a user."""
        # Check cache
        if user_id in self.loaded_schemas:
            return self.loaded_schemas[user_id]
        
        # Find schema file
        schema_files = list(self.profession_dir.glob(f"{user_id}_*.json"))
        if not schema_files:
            return None
        
        # Load most recent
        schema_file = max(schema_files, key=lambda p: p.stat().st_mtime)
        schema = ProfessionSchema.load(schema_file)
        
        # Cache
        self.loaded_schemas[user_id] = schema
        
        return schema
    
    def save_profession_schema(self, schema: ProfessionSchema):
        """Save profession schema to disk."""
        filepath = self.profession_dir / f"{schema.profession_id}.json"
        schema.save(filepath)
        
        # Update cache
        user_id = schema.profession_id.split('_')[0]
        self.loaded_schemas[user_id] = schema
    
    def process_query(
        self,
        query: str,
        user_id: str,
        cognitive_profile: CognitiveProfile,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Process a user query with full profession-aware reasoning.
        
        Args:
            query: User's question or task
            user_id: User identifier
            cognitive_profile: User's cognitive profile
            conversation_history: Recent conversation
            
        Returns:
            Dict with enhanced_query, response, sources, etc.
        """
        # Load profession schema
        profession_schema = self.load_profession_schema(user_id)
        
        if not profession_schema:
            # No profession schema - use basic mode
            return {
                "enhanced_query": query,
                "profession_context": None,
                "needs_onboarding": True
            }
        
        # Check for knowledge gaps
        gaps = profession_schema.identify_knowledge_gaps(query)
        sources = []
        
        if gaps:
            print(f"🔍 Expanding knowledge for: {', '.join(gaps[:2])}")
            profession_schema, sources = self.knowledge_expansion.expand_for_query(
                profession_schema, query
            )
            self.save_profession_schema(profession_schema)
        
        # Enhance query with profession context
        enhanced_query = self.reasoning.enhance_prompt(
            query,
            profession_schema,
            cognitive_profile,
            conversation_history
        )
        
        # Extract decision factors
        decision_factors = self.reasoning.extract_decision_factors(
            query, profession_schema
        )
        
        return {
            "enhanced_query": enhanced_query,
            "profession_context": profession_schema.get_context_summary(),
            "decision_factors": decision_factors,
            "sources": sources,
            "needs_onboarding": False
        }
    
    def validate_response(
        self,
        response: str,
        user_id: str
    ) -> tuple[bool, List[str]]:
        """Validate response against profession safety rules."""
        profession_schema = self.load_profession_schema(user_id)
        
        if not profession_schema:
            return True, []
        
        return self.reasoning.validate_response(response, profession_schema)
    
    def create_aligned_persona(
        self,
        user_id: str,
        cognitive_profile: CognitiveProfile
    ) -> Dict[str, Any]:
        """Create parallel-self aligned persona."""
        profession_schema = self.load_profession_schema(user_id)
        
        if not profession_schema:
            return None
        
        return self.alignment.create_aligned_persona(
            profession_schema, cognitive_profile
        )
    
    def get_profession_summary(self, user_id: str) -> Optional[str]:
        """Get a summary of user's profession for display."""
        profession_schema = self.load_profession_schema(user_id)
        
        if not profession_schema:
            return None
        
        # Helper to safely join list items
        def safe_join(items, max_items=3):
            if not items:
                return "None specified"
            # Convert items to strings and handle dicts
            str_items = []
            for item in items[:max_items]:
                if isinstance(item, dict):
                    str_items.append(str(item.get('name', item)))
                else:
                    str_items.append(str(item))
            return ', '.join(str_items)
        
        summary = f"""**Profession: {profession_schema.profession_name}**
Industry: {profession_schema.industry}
Environment: {profession_schema.environment.work_setting.value}, {profession_schema.environment.team_structure.value}

**Key Responsibilities:**
{chr(10).join(f"• {r}" for r in profession_schema.role_definition.primary_responsibilities[:5])}

**Tools & Platforms:**
{safe_join(profession_schema.tools_equipment.software[:5] + profession_schema.tools_equipment.platforms[:3])}

**Decision Style:**
{profession_schema.decision_patterns.risk_tolerance.value} risk tolerance
Frameworks: {safe_join(profession_schema.decision_patterns.decision_frameworks)}

**Knowledge Confidence:**
✓ High confidence: {len(profession_schema.knowledge_confidence.high_confidence_areas)} areas
⚠ Medium confidence: {len(profession_schema.knowledge_confidence.medium_confidence_areas)} areas
🔍 Needs expansion: {len(profession_schema.knowledge_confidence.needs_expansion)} areas

Last updated: {profession_schema.last_updated.strftime('%Y-%m-%d %H:%M')}
Data sources: {len(profession_schema.data_sources)} sources
"""
        return summary
    
    def list_professions(self) -> List[Dict[str, str]]:
        """List all available profession schemas."""
        professions = []
        
        for schema_file in self.profession_dir.glob("*.json"):
            try:
                schema = ProfessionSchema.load(schema_file)
                professions.append({
                    "profession_id": schema.profession_id,
                    "profession_name": schema.profession_name,
                    "industry": schema.industry,
                    "last_updated": schema.last_updated.isoformat()
                })
            except Exception as e:
                print(f"Failed to load {schema_file}: {e}")
        
        return professions
