"""
Smart routing system for directing questions to appropriate expert personas.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re


@dataclass
class QuestionAnalysis:
    """Analysis of a user's question to determine routing."""
    question: str
    primary_domain: Optional[str]
    secondary_domains: List[str]
    complexity: str  # 'simple', 'moderate', 'complex'
    requires_collaboration: bool
    keywords: List[str]
    confidence: float


class QuestionRouter:
    """Routes questions to appropriate expert personas based on content analysis."""
    
    # Domain detection patterns
    DOMAIN_PATTERNS = {
        'frontend': [
            r'\b(react|vue|angular|component|hook|state|props|jsx|tsx)\b',
            r'\b(css|html|styling|responsive|ui|ux|design|layout)\b',
            r'\b(frontend|front-end|client-side|browser|dom)\b',
        ],
        'backend': [
            r'\b(api|endpoint|route|controller|service|server)\b',
            r'\b(database|sql|query|schema|migration|orm)\b',
            r'\b(backend|back-end|server-side|microservice)\b',
            r'\b(authentication|authorization|jwt|session)\b',
        ],
        'devops': [
            r'\b(docker|container|kubernetes|k8s|pod|deployment)\b',
            r'\b(ci/cd|pipeline|jenkins|github actions|gitlab ci)\b',
            r'\b(aws|azure|gcp|cloud|infrastructure|terraform)\b',
            r'\b(deployment|deploy|release|build|monitoring)\b',
        ],
        'data': [
            r'\b(machine learning|ml|model|training|dataset)\b',
            r'\b(pandas|numpy|tensorflow|pytorch|scikit-learn)\b',
            r'\b(data analysis|analytics|statistics|visualization)\b',
            r'\b(feature engineering|preprocessing|pipeline)\b',
        ],
        'mobile': [
            r'\b(ios|android|mobile|app|swift|kotlin)\b',
            r'\b(react native|flutter|expo|native)\b',
            r'\b(app store|play store|mobile app)\b',
        ],
        'security': [
            r'\b(security|vulnerability|exploit|attack|breach)\b',
            r'\b(encryption|cryptography|hash|secure|ssl|tls)\b',
            r'\b(authentication|authorization|oauth|saml)\b',
            r'\b(compliance|gdpr|hipaa|pci)\b',
        ],
    }
    
    # Complexity indicators
    COMPLEXITY_HIGH = [
        'architecture', 'design pattern', 'scalability', 'optimization',
        'refactor', 'migrate', 'integrate', 'orchestrate'
    ]
    
    COMPLEXITY_MODERATE = [
        'implement', 'build', 'create', 'develop', 'configure', 'setup'
    ]
    
    # Collaboration indicators (needs multiple experts)
    COLLABORATION_KEYWORDS = [
        'full stack', 'end-to-end', 'entire system', 'complete solution',
        'frontend and backend', 'database to ui', 'deployment pipeline'
    ]
    
    def __init__(self, personas_dir: Path):
        self.personas_dir = personas_dir
        self.available_personas = self._load_available_personas()
        self.profession_experts = self._load_profession_experts()
    
    def _load_available_personas(self) -> Dict[str, Dict[str, Any]]:
        """Load all available expert personas."""
        personas = {}
        if not self.personas_dir.exists():
            return personas
        
        for persona_file in self.personas_dir.glob("*.json"):
            with open(persona_file, 'r') as f:
                persona_data = json.load(f)
                # Skip profession experts (handled separately)
                if persona_data.get('agent_type') == 'profession_expert':
                    continue
                domain = persona_data.get('domain')
                if domain:
                    personas[domain] = persona_data
        
        return personas
    
    def _load_profession_experts(self) -> List[Dict[str, Any]]:
        """Load profession expert agents."""
        experts = []
        if not self.personas_dir.exists():
            return experts
        
        for persona_file in self.personas_dir.glob("profession_expert_*.json"):
            with open(persona_file, 'r') as f:
                expert_data = json.load(f)
                experts.append(expert_data)
        
        return experts
    
    def analyze_question(self, question: str) -> QuestionAnalysis:
        """Analyze a question to determine routing."""
        question_lower = question.lower()
        
        # Detect domains
        domain_scores = {}
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, question_lower, re.IGNORECASE)
                score += len(matches)
            if score > 0:
                domain_scores[domain] = score
        
        # Sort by score
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_domain = sorted_domains[0][0] if sorted_domains else None
        secondary_domains = [d for d, _ in sorted_domains[1:3] if d != primary_domain]
        
        # Determine complexity
        complexity = 'simple'
        if any(keyword in question_lower for keyword in self.COMPLEXITY_HIGH):
            complexity = 'complex'
        elif any(keyword in question_lower for keyword in self.COMPLEXITY_MODERATE):
            complexity = 'moderate'
        
        # Check if collaboration needed
        requires_collaboration = (
            len(domain_scores) > 1 or
            any(keyword in question_lower for keyword in self.COLLABORATION_KEYWORDS) or
            complexity == 'complex'
        )
        
        # Extract keywords
        keywords = self._extract_keywords(question)
        
        # Calculate confidence
        confidence = min(1.0, (sorted_domains[0][1] / 3.0) if sorted_domains else 0.0)
        
        return QuestionAnalysis(
            question=question,
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            complexity=complexity,
            requires_collaboration=requires_collaboration,
            keywords=keywords,
            confidence=confidence
        )
    
    def route_question(self, question: str) -> Tuple[List[Dict[str, Any]], QuestionAnalysis]:
        """Route a question to appropriate expert persona(s)."""
        analysis = self.analyze_question(question)
        question_lower = question.lower()
        
        selected_personas = []
        
        # First, check profession experts (highest priority for professional questions)
        profession_match = None
        best_match_score = 0
        
        for expert in self.profession_experts:
            # Check if question matches profession keywords
            keywords = expert.get('keywords', [])
            match_score = 0
            
            for kw in keywords:
                kw_lower = kw.lower()
                # Exact match
                if kw_lower in question_lower:
                    match_score += 2
                # Partial word match (e.g., "trading" matches "quantitative trader")
                elif any(word in question_lower for word in kw_lower.split() if len(word) > 3):
                    match_score += 1
            
            if match_score > best_match_score:
                best_match_score = match_score
                profession_match = expert
        
        # If profession expert matched with reasonable confidence
        if profession_match and best_match_score >= 1:
            selected_personas.append(profession_match)
            # Update analysis with profession domain
            analysis.primary_domain = profession_match.get('profession_name', 'profession')
            analysis.confidence = min(1.0, best_match_score / 3.0)
            
            # Only add domain experts if collaboration is clearly needed
            if analysis.requires_collaboration and len(analysis.secondary_domains) > 0:
                for domain in analysis.secondary_domains[:1]:  # Max 1 additional expert
                    if domain in self.available_personas:
                        selected_personas.append(self.available_personas[domain])
        else:
            # Standard domain routing
            # Add primary expert
            if analysis.primary_domain and analysis.primary_domain in self.available_personas:
                selected_personas.append(self.available_personas[analysis.primary_domain])
            
            # Add secondary experts if collaboration needed
            if analysis.requires_collaboration:
                for domain in analysis.secondary_domains:
                    if domain in self.available_personas:
                        selected_personas.append(self.available_personas[domain])
            
            # If no specific domain detected, return all personas for general question
            if not selected_personas:
                selected_personas = list(self.available_personas.values())
        
        return selected_personas, analysis
    
    def _extract_keywords(self, question: str) -> List[str]:
        """Extract important keywords from question."""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
                     'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'can', 'may', 'might', 'how', 'what', 'when', 'where', 'why',
                     'i', 'you', 'we', 'they', 'my', 'your', 'our', 'their'}
        
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        return keywords[:10]  # Top 10 keywords
    
    def get_routing_explanation(self, analysis: QuestionAnalysis, personas: List[Dict[str, Any]]) -> str:
        """Generate human-readable explanation of routing decision."""
        if not personas:
            return "No specific expert found. Using general knowledge."
        
        explanation = f"**Routing Analysis:**\n"
        explanation += f"- Primary domain: {analysis.primary_domain or 'general'}\n"
        explanation += f"- Complexity: {analysis.complexity}\n"
        explanation += f"- Confidence: {analysis.confidence:.0%}\n\n"
        
        if len(personas) == 1:
            explanation += f"**Routing to:** {personas[0]['name']} ({personas[0]['role']})\n"
        else:
            explanation += f"**Collaborative response from {len(personas)} experts:**\n"
            for persona in personas:
                explanation += f"  - {persona['name']} ({persona['role']})\n"
        
        return explanation
