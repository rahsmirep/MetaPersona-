"""
Onboarding Interpreter
Extracts profession schema from natural language user input
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import re
from .schema import (
    ProfessionSchema, RoleDefinition, DailyTasks, ToolsEquipment,
    Environment, Constraints, Terminology, DecisionPatterns, SafetyRules,
    SkillHierarchy, EdgeCases, KnowledgeConfidence,
    WorkSetting, TeamStructure, PaceLevel, AutonomyLevel, RiskTolerance
)


class OnboardingInterpreter:
    """Interprets natural language profession descriptions into structured schemas."""
    
    def __init__(self, llm_provider):
        self.llm = llm_provider
    
    def interpret(self, user_input: str, user_id: str) -> ProfessionSchema:
        """
        Main entry point: Convert natural language to ProfessionSchema.
        
        Args:
            user_input: Natural language description of profession
            user_id: Unique identifier for the user
            
        Returns:
            ProfessionSchema populated from user input
        """
        # Step 1: Extract structured data using LLM
        extraction_prompt = self._build_extraction_prompt(user_input)
        raw_data = self._call_llm_for_extraction(extraction_prompt)
        
        # Step 2: Parse and validate
        parsed_data = self._parse_llm_response(raw_data)
        
        # Step 3: Map to schema
        schema = self._map_to_schema(parsed_data, user_id)
        
        # Step 4: Identify confidence levels
        schema = self._assess_confidence(schema, user_input)
        
        return schema
    
    def _build_extraction_prompt(self, user_input: str) -> str:
        """Build prompt for LLM to extract structured profession data."""
        return f"""You are an expert at understanding professions and extracting structured information.

User's profession description:
\"\"\"{user_input}\"\"\"

Extract the following information in JSON format:

{{
  "profession_name": "The primary profession name",
  "industry": "The industry sector",
  "primary_responsibilities": ["list of main duties"],
  "secondary_responsibilities": ["list of supporting duties"],
  "daily_routine_tasks": ["tasks done daily"],
  "periodic_tasks": {{"weekly": [...], "monthly": [...], "yearly": [...]}},
  "software_tools": ["software used"],
  "hardware_tools": ["hardware/equipment used"],
  "platforms": ["platforms/systems worked with"],
  "methodologies": ["frameworks/methodologies followed"],
  "work_setting": "office/remote/hybrid/field/laboratory/clinical/mobile",
  "team_structure": "solo/small_team/large_team/matrix/cross_functional",
  "pace": "fast/moderate/methodical/variable",
  "autonomy_level": "high/medium/low/mixed",
  "regulatory_constraints": ["regulations/compliance requirements"],
  "time_constraints": ["time-sensitive aspects"],
  "ethical_considerations": ["ethical guidelines"],
  "common_jargon": {{"term": "definition"}},
  "acronyms": {{"ABC": "Full meaning"}},
  "decision_frameworks": ["how decisions are made"],
  "risk_tolerance": "conservative/moderate/aggressive/context_dependent",
  "safety_rules_critical": ["must never do"],
  "safety_rules_important": ["should avoid"],
  "best_practices": ["recommended practices"],
  "foundational_skills": ["basic skills needed"],
  "intermediate_skills": ["mid-level skills"],
  "advanced_skills": ["expert skills"],
  "success_metrics": ["how success is measured"],
  "common_challenges": ["typical problems faced"]
}}

Extract as much information as possible from the description. For missing information, use empty arrays [] or empty objects {{}}.
Return ONLY valid JSON, no additional text.
"""
    
    def _call_llm_for_extraction(self, prompt: str) -> str:
        """Call LLM to extract structured data."""
        messages = [
            {"role": "system", "content": "You are a profession analysis expert. Extract structured data from profession descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.generate(messages, temperature=0.3)
        return response
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response and handle errors."""
        # Extract JSON from response (in case LLM added extra text)
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response: {e}")
            print(f"Response was: {response[:500]}")
            # Return minimal valid structure
            return {
                "profession_name": "Unknown",
                "industry": "Unknown"
            }
    
    def _map_to_schema(self, data: Dict[str, Any], user_id: str) -> ProfessionSchema:
        """Map extracted data to ProfessionSchema."""
        
        # Create profession ID
        profession_name = data.get("profession_name", "unknown")
        profession_id = f"{user_id}_{profession_name.lower().replace(' ', '_')}"
        
        # Map role definition
        role_def = RoleDefinition(
            primary_responsibilities=data.get("primary_responsibilities", []),
            secondary_responsibilities=data.get("secondary_responsibilities", []),
            success_metrics=data.get("success_metrics", []),
            common_challenges=data.get("common_challenges", [])
        )
        
        # Map daily tasks
        daily_tasks = DailyTasks(
            routine=data.get("daily_routine_tasks", []),
            periodic=data.get("periodic_tasks", {}),
            situational=[]
        )
        
        # Map tools and equipment
        tools = ToolsEquipment(
            software=data.get("software_tools", []),
            hardware=data.get("hardware_tools", []),
            platforms=data.get("platforms", []),
            methodologies=data.get("methodologies", []),
            certifications=[]
        )
        
        # Map environment
        work_setting_map = {
            "office": WorkSetting.OFFICE,
            "remote": WorkSetting.REMOTE,
            "hybrid": WorkSetting.HYBRID,
            "field": WorkSetting.FIELD,
            "laboratory": WorkSetting.LABORATORY,
            "clinical": WorkSetting.CLINICAL,
            "mobile": WorkSetting.MOBILE
        }
        
        team_structure_map = {
            "solo": TeamStructure.SOLO,
            "small_team": TeamStructure.SMALL_TEAM,
            "large_team": TeamStructure.LARGE_TEAM,
            "matrix": TeamStructure.MATRIX,
            "cross_functional": TeamStructure.CROSS_FUNCTIONAL
        }
        
        pace_map = {
            "fast": PaceLevel.FAST,
            "moderate": PaceLevel.MODERATE,
            "methodical": PaceLevel.METHODICAL,
            "variable": PaceLevel.VARIABLE
        }
        
        autonomy_map = {
            "high": AutonomyLevel.HIGH,
            "medium": AutonomyLevel.MEDIUM,
            "low": AutonomyLevel.LOW,
            "mixed": AutonomyLevel.MIXED
        }
        
        environment = Environment(
            work_setting=work_setting_map.get(data.get("work_setting", "office").lower(), WorkSetting.OFFICE),
            team_structure=team_structure_map.get(data.get("team_structure", "small_team").lower(), TeamStructure.SMALL_TEAM),
            pace=pace_map.get(data.get("pace", "moderate").lower(), PaceLevel.MODERATE),
            autonomy_level=autonomy_map.get(data.get("autonomy_level", "medium").lower(), AutonomyLevel.MEDIUM)
        )
        
        # Map constraints
        constraints = Constraints(
            regulatory=data.get("regulatory_constraints", []),
            time_sensitive=data.get("time_constraints", []),
            resource_limitations=[],
            ethical_considerations=data.get("ethical_considerations", []),
            legal_requirements=[]
        )
        
        # Map terminology
        terminology = Terminology(
            jargon=data.get("common_jargon", {}),
            acronyms=data.get("acronyms", {}),
            concepts={}
        )
        
        # Map decision patterns
        risk_tolerance_map = {
            "conservative": RiskTolerance.CONSERVATIVE,
            "moderate": RiskTolerance.MODERATE,
            "aggressive": RiskTolerance.AGGRESSIVE,
            "context_dependent": RiskTolerance.CONTEXT_DEPENDENT
        }
        
        decision_patterns = DecisionPatterns(
            common_decisions=[],
            decision_frameworks=data.get("decision_frameworks", []),
            risk_tolerance=risk_tolerance_map.get(data.get("risk_tolerance", "moderate").lower(), RiskTolerance.MODERATE),
            information_sources=[],
            escalation_criteria=[]
        )
        
        # Map safety rules
        safety_rules = SafetyRules(
            critical=data.get("safety_rules_critical", []),
            important=data.get("safety_rules_important", []),
            best_practices=data.get("best_practices", []),
            emergency_protocols=[]
        )
        
        # Map skill hierarchy
        skill_hierarchy = SkillHierarchy(
            foundational=data.get("foundational_skills", []),
            intermediate=data.get("intermediate_skills", []),
            advanced=data.get("advanced_skills", []),
            mastery=[],
            soft_skills=[]
        )
        
        # Create schema
        schema = ProfessionSchema(
            profession_id=profession_id,
            profession_name=profession_name,
            industry=data.get("industry", "Unknown"),
            role_definition=role_def,
            daily_tasks=daily_tasks,
            tools_equipment=tools,
            environment=environment,
            constraints=constraints,
            terminology=terminology,
            decision_patterns=decision_patterns,
            safety_rules=safety_rules,
            skill_hierarchy=skill_hierarchy,
            edge_cases=EdgeCases(),
            knowledge_confidence=KnowledgeConfidence(),
            data_sources=["user_onboarding"]
        )
        
        return schema
    
    def _assess_confidence(self, schema: ProfessionSchema, original_input: str) -> ProfessionSchema:
        """Assess confidence levels for different parts of the schema."""
        
        # High confidence: Explicitly mentioned in input
        high_confidence = []
        medium_confidence = []
        needs_expansion = []
        
        # Check what was well-populated
        if len(schema.role_definition.primary_responsibilities) >= 3:
            high_confidence.append("primary_responsibilities")
        elif len(schema.role_definition.primary_responsibilities) > 0:
            medium_confidence.append("primary_responsibilities")
        else:
            needs_expansion.append("primary_responsibilities")
        
        if len(schema.tools_equipment.software) >= 3:
            high_confidence.append("software_tools")
        elif len(schema.tools_equipment.software) > 0:
            medium_confidence.append("software_tools")
        else:
            needs_expansion.append("software_tools")
        
        if len(schema.daily_tasks.routine) >= 5:
            high_confidence.append("daily_tasks")
        elif len(schema.daily_tasks.routine) > 0:
            medium_confidence.append("daily_tasks")
        else:
            needs_expansion.append("daily_tasks")
        
        if len(schema.decision_patterns.decision_frameworks) >= 2:
            high_confidence.append("decision_frameworks")
        elif len(schema.decision_patterns.decision_frameworks) > 0:
            medium_confidence.append("decision_frameworks")
        else:
            needs_expansion.append("decision_frameworks")
        
        if len(schema.safety_rules.critical) >= 2:
            high_confidence.append("safety_rules")
        elif len(schema.safety_rules.critical) > 0:
            medium_confidence.append("safety_rules")
        else:
            needs_expansion.append("safety_rules")
        
        # Always need expansion for edge cases initially
        needs_expansion.append("edge_cases")
        needs_expansion.append("industry_best_practices")
        
        schema.knowledge_confidence = KnowledgeConfidence(
            high_confidence_areas=high_confidence,
            medium_confidence_areas=medium_confidence,
            needs_expansion=needs_expansion
        )
        
        return schema
    
    def refine_with_user(self, schema: ProfessionSchema, questions: List[str]) -> ProfessionSchema:
        """Iteratively refine schema by asking user clarifying questions."""
        # This would be used in interactive onboarding
        # For now, just return the schema
        # In full implementation, this would ask follow-up questions
        return schema
