"""
Knowledge Expansion Layer
Fills gaps in profession schema using web search and LLM-based reasoning
"""
from typing import List, Dict, Any, Optional
import requests
import json
import re
from datetime import datetime
from pathlib import Path
from .schema import ProfessionSchema, SafetyRules


class KnowledgeExpansionLayer:
    """Expands profession knowledge using web search when gaps are detected."""
    
    def __init__(self, llm_provider, google_api_key: str, google_cse_id: str, cache_dir: Path = None):
        self.llm = llm_provider
        self.google_api_key = google_api_key
        self.google_cse_id = google_cse_id
        self.cache_dir = cache_dir or Path("data/knowledge_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Template directory for pre-generated safety rules
        self.template_dir = Path("data/safety_templates")
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def expand_schema(self, schema: ProfessionSchema, priority_areas: List[str] = None) -> ProfessionSchema:
        """
        Expand schema knowledge in areas marked as needing expansion.
        
        Args:
            schema: ProfessionSchema to expand
            priority_areas: Specific areas to focus on (optional)
            
        Returns:
            Updated schema with expanded knowledge
        """
        # Determine what to expand
        areas_to_expand = priority_areas or schema.knowledge_confidence.needs_expansion
        
        if not areas_to_expand:
            return schema
        
        expansion_log = {
            "timestamp": datetime.now().isoformat(),
            "areas_expanded": []
        }
        
        for area in areas_to_expand[:3]:  # Limit to 3 at a time to avoid rate limits
            try:
                expanded_data = self._expand_area(schema, area)
                if expanded_data:
                    schema = self._merge_expansion(schema, area, expanded_data)
                    expansion_log["areas_expanded"].append(area)
            except Exception as e:
                print(f"Failed to expand {area}: {e}")
                expansion_log[area] = f"error: {str(e)}"
        
        # Update schema metadata
        schema.expansion_history.append(expansion_log)
        schema.last_updated = datetime.now()
        
        # Update confidence levels
        for area in expansion_log["areas_expanded"]:
            if area in schema.knowledge_confidence.needs_expansion:
                schema.knowledge_confidence.needs_expansion.remove(area)
                schema.knowledge_confidence.medium_confidence_areas.append(area)
        
        return schema
    
    def expand_for_query(self, schema: ProfessionSchema, user_query: str) -> tuple[ProfessionSchema, List[str]]:
        """
        Expand schema based on specific user query gaps.
        
        Args:
            schema: Current profession schema
            user_query: User's question that triggered expansion
            
        Returns:
            (Updated schema, list of sources used)
        """
        # Detect what the query is asking about
        gaps = self._detect_query_gaps(schema, user_query)
        
        if not gaps:
            return schema, []
        
        sources = []
        for gap in gaps:
            # Generate search queries
            queries = self._generate_search_queries(schema, gap, user_query)
            
            # Search and extract
            for query in queries[:2]:  # Limit searches
                results = self._web_search(query)
                if results:
                    cleaned_data = self._clean_search_results(results, gap)
                    schema = self._merge_expansion(schema, gap, cleaned_data)
                    sources.extend([r['link'] for r in results[:3]])
        
        return schema, sources
    
    def _expand_area(self, schema: ProfessionSchema, area: str) -> Optional[Dict[str, Any]]:
        """Expand a specific area of the schema."""
        # Generate targeted search queries
        queries = self._generate_search_queries(schema, area)
        
        if not queries:
            return None
        
        # Search for each query
        all_results = []
        for query in queries[:2]:  # Limit to 2 queries per area
            results = self._web_search(query)
            if results:
                all_results.extend(results[:3])  # Top 3 results per query
        
        if not all_results:
            return None
        
        # Clean and extract relevant information
        cleaned_data = self._clean_search_results(all_results, area)
        
        return cleaned_data
    
    def _generate_search_queries(self, schema: ProfessionSchema, gap_area: str, context: str = None) -> List[str]:
        """Generate optimized search queries for a knowledge gap."""
        profession = schema.profession_name
        industry = schema.industry
        
        # Base queries by gap type
        query_templates = {
            "primary_responsibilities": [
                f"{profession} main responsibilities duties",
                f"{profession} job description key tasks"
            ],
            "software_tools": [
                f"{profession} software tools commonly used",
                f"best tools for {profession} {industry}"
            ],
            "daily_tasks": [
                f"{profession} typical day workflow",
                f"{profession} daily routine tasks"
            ],
            "decision_frameworks": [
                f"{profession} decision making framework",
                f"how {profession} make decisions {industry}"
            ],
            "safety_rules": [
                f"{profession} safety protocols best practices",
                f"{profession} compliance requirements {industry}"
            ],
            "best_practices": [
                f"{profession} industry best practices",
                f"{profession} standards guidelines {industry}"
            ],
            "edge_cases": [
                f"{profession} unusual scenarios edge cases",
                f"{profession} rare situations how to handle"
            ],
            "industry_best_practices": [
                f"{industry} {profession} best practices",
                f"{profession} {industry} standards"
            ]
        }
        
        # Get queries for this gap area
        queries = query_templates.get(gap_area, [f"{profession} {gap_area} {industry}"])
        
        # If context provided, add context-specific query
        if context:
            queries.insert(0, f"{profession} {context}")
        
        return queries
    
    def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """
        Perform web search using Google Custom Search API.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results
        """
        # Check cache first
        cache_key = self._get_cache_key(query)
        cached = self._load_from_cache(cache_key)
        if cached:
            return cached
        
        try:
            # Google Custom Search API endpoint
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cse_id,
                "q": query,
                "num": 5  # Number of results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if "items" in data:
                for item in data["items"]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "displayLink": item.get("displayLink", "")
                    })
            
            # Cache results
            self._save_to_cache(cache_key, results)
            
            return results
            
        except Exception as e:
            print(f"Web search failed for query '{query}': {e}")
            return []
    
    def _clean_search_results(self, results: List[Dict[str, Any]], gap_area: str) -> Dict[str, Any]:
        """
        Clean and extract relevant information from search results using LLM.
        
        Args:
            results: Raw search results
            gap_area: The area being expanded
            
        Returns:
            Cleaned and structured data
        """
        # Prepare results text for LLM
        results_text = ""
        for i, result in enumerate(results[:5], 1):
            results_text += f"\n{i}. {result['title']}\n"
            results_text += f"   Source: {result['displayLink']}\n"
            results_text += f"   {result['snippet']}\n"
        
        # Use LLM to extract relevant information
        extraction_prompt = f"""Extract relevant information about "{gap_area}" from these search results.

Search Results:
{results_text}

Extract the following in JSON format:
{{
  "key_points": ["list of important points found"],
  "facts": ["factual information"],
  "best_practices": ["best practices if mentioned"],
  "sources": ["list of authoritative sources"],
  "confidence": "high/medium/low"
}}

Focus on factual, authoritative information. Ignore ads and promotional content.
Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": "You are an expert at extracting accurate information from web search results."},
            {"role": "user", "content": extraction_prompt}
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.2)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                cleaned_data = json.loads(json_match.group(0))
                return cleaned_data
        except Exception as e:
            print(f"Failed to clean results: {e}")
        
        # Fallback: return raw snippets
        return {
            "key_points": [r["snippet"] for r in results[:3]],
            "facts": [],
            "best_practices": [],
            "sources": [r["link"] for r in results],
            "confidence": "low"
        }
    
    def _merge_expansion(self, schema: ProfessionSchema, area: str, data: Dict[str, Any]) -> ProfessionSchema:
        """Merge expanded knowledge into schema."""
        
        # Map area to schema field
        if area == "primary_responsibilities":
            existing = set(schema.role_definition.primary_responsibilities)
            new_items = [item for item in data.get("key_points", []) if item not in existing]
            schema.role_definition.primary_responsibilities.extend(new_items[:5])
        
        elif area == "software_tools":
            existing = set(schema.tools_equipment.software)
            new_items = [item for item in data.get("key_points", []) if item not in existing]
            schema.tools_equipment.software.extend(new_items[:5])
        
        elif area == "daily_tasks":
            existing = set(schema.daily_tasks.routine)
            new_items = [item for item in data.get("key_points", []) if item not in existing]
            schema.daily_tasks.routine.extend(new_items[:5])
        
        elif area == "decision_frameworks":
            existing = set(schema.decision_patterns.decision_frameworks)
            new_items = [item for item in data.get("key_points", []) if item not in existing]
            schema.decision_patterns.decision_frameworks.extend(new_items[:3])
        
        elif area == "safety_rules":
            existing = set(schema.safety_rules.best_practices)
            new_items = [item for item in data.get("best_practices", []) if item not in existing]
            schema.safety_rules.best_practices.extend(new_items[:5])
        
        elif area in ["best_practices", "industry_best_practices"]:
            existing = set(schema.safety_rules.best_practices)
            new_items = [item for item in data.get("best_practices", []) if item not in existing]
            schema.safety_rules.best_practices.extend(new_items[:5])
        
        elif area == "edge_cases":
            for point in data.get("key_points", [])[:3]:
                schema.edge_cases.scenarios.append({"scenario": point, "response": "Requires further analysis"})
        
        # Add sources to data sources
        for source in data.get("sources", []):
            if source not in schema.data_sources:
                schema.data_sources.append(source)
        
        return schema
    
    def _detect_query_gaps(self, schema: ProfessionSchema, query: str) -> List[str]:
        """Detect what knowledge gaps are revealed by user query."""
        gaps = schema.identify_knowledge_gaps(query)
        return gaps
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for a query."""
        import hashlib
        return hashlib.md5(query.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Load cached search results."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                # Check if cache is less than 7 days old
                cache_age = datetime.now() - datetime.fromisoformat(cached_data["timestamp"])
                if cache_age.days < 7:
                    return cached_data["results"]
            except Exception:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, results: List[Dict[str, Any]]):
        """Save search results to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "results": results
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to cache results: {e}")
    
    def generate_comprehensive_safety_rules(self, schema: ProfessionSchema) -> SafetyRules:
        """
        Generate comprehensive safety rules using LLM-based reasoning.
        Uses 6-question framework for legal and ethical compliance.
        
        Args:
            schema: ProfessionSchema to generate safety rules for
            
        Returns:
            SafetyRules object with critical rules, warnings, and best practices
        """
        profession = schema.profession_name
        industry = schema.industry
        
        safety_prompt = f"""You are a legal and compliance expert. Generate comprehensive safety rules for a {profession} working in {industry}.

Use this 6-question framework to ensure complete coverage:

**1. REGULATORY & COMPLIANCE**
- What government agencies regulate this profession? (FDA, SEC, FTC, HIPAA, etc.)
- What licenses or certifications are legally required?
- What actions require regulatory approval before execution?
- What reporting/documentation is legally mandated?

**2. DATA & PRIVACY**
- What types of data are legally protected? (PII, PHI, financial, classified)
- What are the data retention/destruction requirements?
- Who can legally access certain data?
- What consent is required before collecting/using data?

**3. PROFESSIONAL ETHICS & STANDARDS**
- What professional codes of conduct exist?
- What constitutes malpractice or professional negligence?
- What conflicts of interest must be disclosed/avoided?
- What fiduciary duties exist?

**4. SAFETY & RISK MANAGEMENT**
- What actions could cause physical harm?
- What validation/testing is required before deployment?
- What safety protocols are legally mandated?
- What insurance or bonding is required?

**5. LEGAL BOUNDARIES**
- What practices constitute fraud or misrepresentation?
- What confidentiality obligations exist?
- What anti-discrimination laws apply?
- What insider trading/market manipulation rules apply?

**6. SCOPE OF PRACTICE**
- What tasks require specific credentials to perform legally?
- What advice constitutes unauthorized practice?
- What delegations are prohibited?

Generate rules in JSON format:
{{
  "critical_rules": [
    "NEVER [action that could cause legal/ethical violations]",
    "ALWAYS [required compliance action]",
    ... (minimum 10 rules)
  ],
  "important_rules": [
    "Should avoid [risky situation]",
    "Should always [recommended practice]",
    ... (5-8 rules)
  ],
  "best_practices": [
    "Best practice statement",
    ... (8-12 practices)
  ],
  "regulatory_context": {{
    "primary_regulations": ["list of key regulations/laws"],
    "governing_bodies": ["agencies/organizations"],
    "required_certifications": ["licenses/certifications"]
  }}
}}

Be specific to {profession} in {industry}. Focus on rules that prevent legal violations, protect people from harm, and ensure ethical practice.

Return ONLY valid JSON."""

        messages = [
            {"role": "system", "content": "You are an expert in professional compliance, legal requirements, and ethical standards across industries."},
            {"role": "user", "content": safety_prompt}
        ]
        
        try:
            response = self.llm.generate(messages, temperature=0.3)
            
            # Parse JSON response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                safety_data = json.loads(json_match.group(0))
                
                # Create SafetyRules object
                safety_rules = SafetyRules(
                    critical=safety_data.get("critical_rules", [])[:15],  # Cap at 15
                    important=safety_data.get("important_rules", [])[:10],
                    best_practices=safety_data.get("best_practices", [])[:15]
                )
                
                # Store regulatory context in schema metadata if available
                if "regulatory_context" in safety_data:
                    schema.constraints.regulatory = safety_data["regulatory_context"].get("primary_regulations", [])
                
                return safety_rules
                
        except Exception as e:
            print(f"Failed to generate safety rules via LLM: {e}")
        
        # Fallback: basic safety rules
        return self._generate_fallback_safety_rules(profession, industry)
    
    def _generate_fallback_safety_rules(self, profession: str, industry: str) -> SafetyRules:
        """Generate basic fallback safety rules when LLM generation fails."""
        return SafetyRules(
            critical=[
                f"NEVER provide advice outside your scope of practice as a {profession}",
                f"ALWAYS comply with {industry} industry regulations and standards",
                "NEVER misrepresent credentials or qualifications",
                "ALWAYS protect confidential and sensitive information",
                "NEVER engage in discriminatory practices"
            ],
            important=[
                "Should verify compliance with current regulations before taking action",
                "Should consider ethical implications of decisions",
                "Should seek second opinions on high-risk decisions"
            ],
            best_practices=[
                "Document important decisions and their rationale",
                "Stay current with industry standards and regulations",
                f"Follow {industry} best practices and guidelines",
                "Handle sensitive data with appropriate security measures"
            ]
        )
    
    def load_safety_template(self, profession: str, industry: str) -> Optional[SafetyRules]:
        """
        Load pre-generated safety rules template if available.
        
        Args:
            profession: Profession name
            industry: Industry name
            
        Returns:
            SafetyRules if template exists, None otherwise
        """
        # Normalize names for filename
        profession_key = profession.lower().replace(" ", "_").replace("/", "_")
        industry_key = industry.lower().replace(" ", "_").replace("/", "_")
        
        template_path = self.template_dir / f"{profession_key}_{industry_key}.json"
        
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                return SafetyRules(
                    critical=template_data.get("critical", []),
                    important=template_data.get("important", []),
                    best_practices=template_data.get("best_practices", []),
                    emergency_protocols=template_data.get("emergency_protocols", [])
                )
            except Exception as e:
                print(f"Failed to load safety template: {e}")
        
        return None
    
    def save_safety_template(self, profession: str, industry: str, safety_rules: SafetyRules):
        """
        Save safety rules as a reusable template.
        
        Args:
            profession: Profession name
            industry: Industry name
            safety_rules: SafetyRules to save
        """
        # Normalize names for filename
        profession_key = profession.lower().replace(" ", "_").replace("/", "_")
        industry_key = industry.lower().replace(" ", "_").replace("/", "_")
        
        template_path = self.template_dir / f"{profession_key}_{industry_key}.json"
        
        try:
            template_data = {
                "profession": profession,
                "industry": industry,
                "generated_at": datetime.now().isoformat(),
                "critical": safety_rules.critical,
                "important": safety_rules.important,
                "best_practices": safety_rules.best_practices,
                "emergency_protocols": safety_rules.emergency_protocols
            }
            
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved safety template: {profession} ({industry})")
        except Exception as e:
            print(f"Failed to save safety template: {e}")
