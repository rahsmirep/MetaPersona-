"""
Profession Reasoning Layer
Applies profession-aware reasoning to user queries
"""
from typing import Dict, Any, List, Optional
from .schema import ProfessionSchema
from ..cognitive_profile import CognitiveProfile


class ProfessionReasoningLayer:
    """Injects profession context into reasoning and decision-making."""
    
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def enhance_prompt(
        self,
        user_query: str,
        profession_schema: ProfessionSchema,
        cognitive_profile: CognitiveProfile,
        conversation_history: List[Dict] = None
    ) -> str:
        """
        Enhance user query with profession context for better reasoning.
        
        Args:
            user_query: The user's question or task
            profession_schema: User's profession schema
            cognitive_profile: User's cognitive profile
            conversation_history: Recent conversation context
            
        Returns:
            Enhanced prompt with profession context
        """
        # Build profession context
        profession_context = self._build_profession_context(profession_schema, user_query)
        
        # Build decision context
        decision_context = self._build_decision_context(profession_schema, user_query)
        
        # Build safety context
        safety_context = self._build_safety_context(profession_schema)
        
        # Build personal style context
        personal_context = self._build_personal_context(cognitive_profile)
        
        # Combine all contexts
        enhanced_prompt = f"""{user_query}

**Your Professional Context ({profession_schema.profession_name}):**
{profession_context}

**Decision Framework:**
{decision_context}

{safety_context}

**Your Personal Style:**
{personal_context}

Consider the above context when responding. Provide advice that:
1. Aligns with professional best practices in {profession_schema.profession_name}
2. Matches your decision-making patterns and risk tolerance
3. Adheres to all safety rules and constraints
4. Reflects your communication style and preferences
"""
        
        return enhanced_prompt
    
    def _build_profession_context(self, schema: ProfessionSchema, query: str) -> str:
        """Build relevant profession context for the query."""
        context_parts = []
        
        # Add relevant responsibilities if query relates to duties
        if any(word in query.lower() for word in ['should', 'do', 'handle', 'approach', 'deal']):
            if schema.role_definition.primary_responsibilities:
                context_parts.append(f"Your key responsibilities include:\n" + 
                    "\n".join(f"- {r}" for r in schema.role_definition.primary_responsibilities[:3]))
        
        # Add relevant tools
        if any(word in query.lower() for word in ['tool', 'software', 'use', 'platform']):
            tools = schema.tools_equipment.software + schema.tools_equipment.platforms
            if tools:
                context_parts.append(f"\nYour typical tools: {', '.join(tools[:5])}")
        
        # Add relevant terminology if query contains technical terms
        query_words = set(query.lower().split())
        relevant_terms = {term: defn for term, defn in schema.terminology.jargon.items() 
                         if term.lower() in query_words}
        if relevant_terms:
            context_parts.append(f"\nRelevant terminology:")
            for term, defn in list(relevant_terms.items())[:3]:
                context_parts.append(f"- {term}: {defn}")
        
        # Add environment context for work-related queries
        if any(word in query.lower() for word in ['team', 'work', 'collaborate', 'time']):
            env = schema.environment
            context_parts.append(f"\nYour work environment: {env.work_setting.value}, " +
                                f"{env.team_structure.value}, {env.pace.value} pace")
        
        return "\n".join(context_parts) if context_parts else "Standard professional context applies."
    
    def _build_decision_context(self, schema: ProfessionSchema, query: str) -> str:
        """Build decision-making context."""
        context_parts = []
        
        # Add decision frameworks
        if schema.decision_patterns.decision_frameworks:
            context_parts.append("Your typical decision frameworks:")
            for framework in schema.decision_patterns.decision_frameworks[:3]:
                context_parts.append(f"- {framework}")
        
        # Add risk tolerance
        context_parts.append(f"\nYour risk tolerance: {schema.decision_patterns.risk_tolerance.value}")
        
        # Add information sources
        if schema.decision_patterns.information_sources:
            sources = ", ".join(schema.decision_patterns.information_sources[:3])
            context_parts.append(f"You typically consult: {sources}")
        
        return "\n".join(context_parts) if context_parts else "Use standard decision-making approaches."
    
    def _build_safety_context(self, schema: ProfessionSchema) -> str:
        """Build safety rules and constraints context."""
        if not schema.safety_rules.critical and not schema.safety_rules.important:
            return ""
        
        context_parts = ["**Critical Safety Rules:**"]
        
        # Critical rules (must never violate)
        if schema.safety_rules.critical:
            context_parts.append("NEVER:")
            for rule in schema.safety_rules.critical[:5]:
                context_parts.append(f"- {rule}")
        
        # Important rules (should avoid)
        if schema.safety_rules.important:
            context_parts.append("\nAVOID:")
            for rule in schema.safety_rules.important[:3]:
                context_parts.append(f"- {rule}")
        
        # Regulatory constraints
        if schema.constraints.regulatory:
            context_parts.append("\nCompliance Requirements:")
            for constraint in schema.constraints.regulatory[:3]:
                context_parts.append(f"- {constraint}")
        
        return "\n".join(context_parts)
    
    def _build_personal_context(self, cognitive_profile: CognitiveProfile) -> str:
        """Build personal style and preferences context."""
        context_parts = []
        
        # Writing style
        style = cognitive_profile.writing_style
        context_parts.append(f"Communication: {style.tone} tone, {style.vocabulary_level} vocabulary")
        
        # Decision pattern
        decision = cognitive_profile.decision_pattern
        context_parts.append(f"Decision approach: {decision.approach}, {decision.risk_tolerance} risk tolerance")
        
        # Thinking style
        if hasattr(cognitive_profile, 'thinking_style'):
            context_parts.append(f"Thinking: {cognitive_profile.thinking_style}")
        
        return "\n".join(context_parts)
    
    def validate_response(
        self,
        response: str,
        profession_schema: ProfessionSchema
    ) -> tuple[bool, List[str]]:
        """
        Validate response against profession safety rules and constraints.
        
        Args:
            response: Generated response to validate
            profession_schema: User's profession schema
            
        Returns:
            (is_safe, violations_found)
        """
        violations = []
        
        # Check critical safety rules
        for rule in profession_schema.safety_rules.critical:
            # Simple keyword-based check (could be enhanced with LLM)
            rule_keywords = rule.lower().split()[:3]  # First 3 words
            if any(keyword in response.lower() for keyword in rule_keywords):
                violations.append(f"Potential violation of critical rule: {rule}")
        
        # Check regulatory constraints
        for constraint in profession_schema.constraints.regulatory:
            constraint_keywords = constraint.lower().split()[:3]
            if any(keyword in response.lower() for keyword in constraint_keywords):
                # This might not be a violation, but flag for review
                violations.append(f"Response mentions regulated area: {constraint}")
        
        is_safe = len(violations) == 0
        return is_safe, violations
    
    def extract_decision_factors(
        self,
        query: str,
        profession_schema: ProfessionSchema
    ) -> Dict[str, Any]:
        """
        Extract decision factors from query using profession context.
        
        Returns structured decision factors to help with reasoning.
        """
        factors_prompt = f"""Analyze this query from a {profession_schema.profession_name} perspective:
"{query}"

Extract decision factors in JSON format:
{{
  "decision_type": "technical/business/ethical/operational",
  "urgency": "immediate/soon/routine",
  "risk_level": "high/medium/low",
  "stakeholders": ["who is affected"],
  "constraints": ["what limits the options"],
  "key_considerations": ["main factors to consider"]
}}

Context: This person works as a {profession_schema.profession_name} in {profession_schema.industry}.
Their typical decision frameworks: {', '.join(profession_schema.decision_patterns.decision_frameworks[:2])}

Return ONLY valid JSON."""
        
        try:
            messages = [
                {"role": "system", "content": "You are an expert at analyzing professional decisions."},
                {"role": "user", "content": factors_prompt}
            ]
            
            response = self.llm.generate(messages, temperature=0.3)
            
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                factors = json.loads(json_match.group(0))
                return factors
        except Exception as e:
            print(f"Failed to extract decision factors: {e}")
        
        # Fallback
        return {
            "decision_type": "general",
            "urgency": "routine",
            "risk_level": "medium",
            "stakeholders": [],
            "constraints": [],
            "key_considerations": []
        }


class ParallelSelfAlignment:
    """Aligns profession schema with user's personal cognitive profile."""
    
    def __init__(self):
        pass
    
    def create_aligned_persona(
        self,
        profession_schema: ProfessionSchema,
        cognitive_profile: CognitiveProfile
    ) -> Dict[str, Any]:
        """
        Create a persona that blends profession with personal style.
        
        Returns a configuration for how the AI should behave.
        """
        # Debug print statements to help trace issues
        print("profession_schema:", type(profession_schema), vars(profession_schema))
        print("cognitive_profile:", type(cognitive_profile), vars(cognitive_profile))
        persona = {
            "name": f"{cognitive_profile.user_id} (Professional Mode)",
            "profession": profession_schema.profession_name,


            "industry": profession_schema.industry,
            
            "communication_style": self._blend_communication_style(
                profession_schema, cognitive_profile
            ),
            
            "decision_making": self._blend_decision_patterns(
                profession_schema, cognitive_profile
            ),
            
            "knowledge_domains": self._identify_knowledge_domains(
                profession_schema
            ),
            
            "constraints": self._merge_constraints(
                profession_schema, cognitive_profile

            ),
            
            "behavioral_traits": self._define_behavioral_traits(
                profession_schema, cognitive_profile
            )
        }
        
        return persona
    
    def _blend_communication_style(
        self,
        profession: ProfessionSchema,
        profile: CognitiveProfile
    ) -> Dict[str, str]:
        """Blend professional and personal communication styles."""
        return {
            "tone": profile.writing_style.tone,  # Keep personal tone
            "vocabulary": profile.writing_style.vocabulary_level,  # Keep personal vocab
            "structure": profile.writing_style.sentence_structure,
            "professional_terminology": "use",  # But use profession terminology
            "jargon_level": "appropriate",  # Use jargon when relevant
        }
    
    def _blend_decision_patterns(
        self,
        profession: ProfessionSchema,
        profile: CognitiveProfile
    ) -> Dict[str, str]:
        """Blend professional and personal decision-making patterns."""
        # Profession frameworks take priority for work decisions
        # Personal patterns influence style and approach
        return {
            "frameworks": profession.decision_patterns.decision_frameworks,  # Professional
            "approach": profile.decision_pattern.approach,  # Personal
            "risk_tolerance": self._merge_risk_tolerance(
                profession.decision_patterns.risk_tolerance.value,
                profile.decision_pattern.risk_tolerance
            ),
            "analysis_depth": profile.decision_pattern.approach,  # Personal trait
        }
    
    def _merge_risk_tolerance(self, prof_risk: str, personal_risk: str) -> str:
        """Merge professional and personal risk tolerance."""
        # Professional risk tolerance takes precedence
        # But personal conservative nature can pull it down
        risk_levels = {"conservative": 1, "moderate": 2, "aggressive": 3, "context_dependent": 2}
        
        prof_level = risk_levels.get(prof_risk, 2)
        personal_level = risk_levels.get(personal_risk, 2)
        
        # Average them, but bias toward more conservative
        merged_level = min(prof_level, personal_level)
        
        level_names = {1: "conservative", 2: "moderate", 3: "aggressive"}
        return level_names.get(merged_level, "moderate")
    
    def _identify_knowledge_domains(self, profession: ProfessionSchema) -> List[str]:
        """Identify key knowledge domains for this profession."""
        domains = [profession.profession_name, profession.industry]
        
        # Add methodologies as domains
        domains.extend(profession.tools_equipment.methodologies[:3])
        
        # Add key skill areas
        domains.extend(profession.skill_hierarchy.advanced[:2])
        
        return list(set(domains))  # Remove duplicates
    
    def _merge_constraints(
        self,
        profession: ProfessionSchema,
        profile: CognitiveProfile
    ) -> Dict[str, List[str]]:
        """Merge professional and personal constraints."""
        return {
            "regulatory": profession.constraints.regulatory,  # Professional
            "ethical": profession.constraints.ethical_considerations,  # Professional
            "personal_boundaries": [],  # Could add from profile if available
            "time_constraints": profession.constraints.time_sensitive,
        }
    
    def _define_behavioral_traits(
        self,
        profession: ProfessionSchema,
        profile: CognitiveProfile
    ) -> Dict[str, str]:
        """Define how the aligned persona should behave."""
        return {
            "proactivity": "high" if profession.environment.autonomy_level.value == "high" else "medium",
            "detail_orientation": "high" if profile.decision_pattern.approach == "analytical" else "medium",
            "collaboration_style": profession.environment.team_structure.value,
            "work_pace": profession.environment.pace.value,
        }
    
    def generate_system_prompt(
        self,
        aligned_persona: Dict[str, Any]
    ) -> str:
        """Generate system prompt for the aligned parallel-self."""
        prompt = f"""You are {aligned_persona['name']}, working as a {aligned_persona['profession']} in the {aligned_persona['industry']} industry.

**Communication Style:**
- Tone: {aligned_persona['communication_style']['tone']}
- Vocabulary: {aligned_persona['communication_style']['vocabulary']}
- Use professional terminology appropriately

**Decision Making:**
- Approach: {aligned_persona['decision_making']['approach']}
- Risk tolerance: {aligned_persona['decision_making']['risk_tolerance']}
- Frameworks: {', '.join(aligned_persona['decision_making']['frameworks'][:2])}

**Knowledge Domains:**
{', '.join(aligned_persona['knowledge_domains'])}

**Behavioral Traits:**
- Proactivity: {aligned_persona['behavioral_traits']['proactivity']}
- Detail orientation: {aligned_persona['behavioral_traits']['detail_orientation']}
- Work pace: {aligned_persona['behavioral_traits']['work_pace']}

Respond as this person would - combining professional expertise with personal style.
"""
        return prompt
    