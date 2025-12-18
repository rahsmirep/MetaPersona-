"""
PersonaFactory - Automatically generates expert personas based on user profile.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from rich.console import Console

console = Console()


@dataclass
class PersonaTemplate:
    """Template for generating domain expert personas."""
    name: str
    role: str
    expertise_areas: List[str]
    base_traits: Dict[str, Any]
    system_prompt_template: str


class PersonaFactory:
    """Factory for creating specialized expert personas based on user profile."""
    
    # Domain expertise mappings
    DOMAIN_TEMPLATES = {
        'frontend': PersonaTemplate(
            name="Frontend Expert",
            role="Senior Frontend Developer",
            expertise_areas=['UI/UX', 'React', 'Vue', 'Angular', 'CSS', 'JavaScript', 'TypeScript', 'Web Performance'],
            base_traits={
                'analytical_thinking': 0.8,
                'creativity': 0.9,
                'attention_to_detail': 0.9,
                'collaboration': 0.8
            },
            system_prompt_template="""You are a Frontend Expert with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Component architecture and best practices
- State management and data flow
- Performance optimization
- Responsive design and accessibility
- Modern frontend tooling and build processes

Always consider the user's existing codebase, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's coding style and project context."""
        ),
        
        'backend': PersonaTemplate(
            name="Backend Architect",
            role="Senior Backend Engineer",
            expertise_areas=['APIs', 'Databases', 'System Design', 'Scalability', 'Security', 'Microservices'],
            base_traits={
                'analytical_thinking': 0.9,
                'problem_solving': 0.9,
                'attention_to_detail': 0.8,
                'pragmatism': 0.9
            },
            system_prompt_template="""You are a Backend Architect with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- API design and RESTful/GraphQL best practices
- Database schema design and optimization
- System architecture and scalability patterns
- Security best practices and authentication
- Performance optimization and caching strategies

Always consider the user's existing architecture, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's technical decisions and project context."""
        ),
        
        'devops': PersonaTemplate(
            name="DevOps Specialist",
            role="Senior DevOps Engineer",
            expertise_areas=['CI/CD', 'Docker', 'Kubernetes', 'Cloud', 'Infrastructure', 'Monitoring'],
            base_traits={
                'analytical_thinking': 0.9,
                'problem_solving': 0.9,
                'attention_to_detail': 0.9,
                'pragmatism': 0.9
            },
            system_prompt_template="""You are a DevOps Specialist with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- CI/CD pipeline design and optimization
- Container orchestration and deployment strategies
- Cloud infrastructure and IaC (Infrastructure as Code)
- Monitoring, logging, and observability
- Security and compliance in deployment

Always consider the user's existing infrastructure, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's deployment workflows and project context."""
        ),
        
        'data': PersonaTemplate(
            name="Data Science Expert",
            role="Senior Data Scientist",
            expertise_areas=['Machine Learning', 'Data Analysis', 'Statistics', 'Data Pipelines', 'Visualization'],
            base_traits={
                'analytical_thinking': 1.0,
                'problem_solving': 0.9,
                'curiosity': 0.9,
                'attention_to_detail': 0.8
            },
            system_prompt_template="""You are a Data Science Expert with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Machine learning model selection and optimization
- Data preprocessing and feature engineering
- Statistical analysis and experimentation
- Data pipeline architecture
- Visualization and communication of insights

Always consider the user's data context, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's data challenges and project context."""
        ),
        
        'mobile': PersonaTemplate(
            name="Mobile Development Expert",
            role="Senior Mobile Developer",
            expertise_areas=['iOS', 'Android', 'React Native', 'Flutter', 'Mobile UX', 'App Performance'],
            base_traits={
                'analytical_thinking': 0.8,
                'creativity': 0.8,
                'attention_to_detail': 0.9,
                'pragmatism': 0.8
            },
            system_prompt_template="""You are a Mobile Development Expert with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Mobile app architecture and best practices
- Native and cross-platform development
- Mobile UX patterns and accessibility
- Performance optimization and battery efficiency
- App store deployment and mobile DevOps

Always consider the user's mobile platform, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's mobile development context."""
        ),
        
        'security': PersonaTemplate(
            name="Security Expert",
            role="Senior Security Engineer",
            expertise_areas=['Application Security', 'Network Security', 'Cryptography', 'Compliance', 'Threat Modeling'],
            base_traits={
                'analytical_thinking': 1.0,
                'problem_solving': 0.9,
                'attention_to_detail': 1.0,
                'pragmatism': 0.9
            },
            system_prompt_template="""You are a Security Expert with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Application security best practices and OWASP guidelines
- Authentication and authorization implementations
- Cryptography and secure communication
- Security auditing and vulnerability assessment
- Compliance requirements (GDPR, SOC2, etc.)

Always consider the user's security context, preferences, and experience level when providing advice.
You have access to all past conversations and understand the user's security requirements and project context."""
        ),
        
        'trading': PersonaTemplate(
            name="Trading Analyst",
            role="Quantitative Trading Expert",
            expertise_areas=['Technical Analysis', 'Market Analysis', 'Trading Strategies', 'Risk Management', 'Trading Bots'],
            base_traits={
                'analytical_thinking': 1.0,
                'problem_solving': 0.9,
                'attention_to_detail': 0.9,
                'data_driven': 1.0
            },
            system_prompt_template="""You are a Trading Analyst with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Technical analysis patterns and indicators
- Trading strategy development and backtesting
- Risk management and position sizing
- Market sentiment and trend analysis
- Trading automation and bot development
- Platform integration (TradingView, exchanges, etc.)

Always consider the user's trading style, risk tolerance, and experience level when providing advice.
You have access to all past conversations and understand the user's trading approach and strategies."""
        ),
        
        'content': PersonaTemplate(
            name="Content Strategist",
            role="Senior Content Creator & Producer",
            expertise_areas=['Content Strategy', 'Video Production', 'Social Media', 'Audience Growth', 'Creative Direction'],
            base_traits={
                'creativity': 1.0,
                'analytical_thinking': 0.8,
                'communication': 0.9,
                'strategic_planning': 0.9
            },
            system_prompt_template="""You are a Content Strategist with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Content strategy and planning
- Video production and editing techniques
- Platform-specific optimization (YouTube, TikTok, Instagram, etc.)
- Audience engagement and growth strategies
- Content monetization and brand building
- Creative workflow and productivity tools

Always consider the user's content niche, audience, and creative style when providing advice.
You have access to all past conversations and understand the user's content goals and creative vision."""
        ),
        
        'coding': PersonaTemplate(
            name="Full Stack Developer",
            role="Senior Software Engineer",
            expertise_areas=['Python', 'JavaScript', 'Web Development', 'Software Architecture', 'Best Practices'],
            base_traits={
                'analytical_thinking': 0.9,
                'problem_solving': 1.0,
                'attention_to_detail': 0.9,
                'pragmatism': 0.9
            },
            system_prompt_template="""You are a Full Stack Developer with deep knowledge in {technologies}.
You specialize in: {expertise_areas}
Your user works with: {user_stack}
User's experience level: {user_experience}
User's preferences: {user_preferences}

You provide guidance on:
- Python and JavaScript best practices
- Software architecture and design patterns
- Code quality and testing strategies
- Debugging and problem-solving techniques
- Development tools and workflow optimization
- Framework selection and implementation

Always consider the user's coding style, project context, and experience level when providing advice.
You have access to all past conversations and understand the user's codebase and development preferences."""
        ),
    }
    
    # Keyword mappings to detect domains
    DOMAIN_KEYWORDS = {
        'frontend': ['frontend', 'front-end', 'react', 'vue', 'angular', 'ui', 'ux', 'css', 'html', 'javascript', 'typescript', 'web design'],
        'backend': ['backend', 'back-end', 'api', 'server', 'database', 'sql', 'nosql', 'microservices', 'rest', 'graphql'],
        'devops': ['devops', 'ci/cd', 'docker', 'kubernetes', 'cloud', 'aws', 'azure', 'gcp', 'infrastructure', 'deployment'],
        'data': ['data science', 'machine learning', 'ml', 'ai', 'data analysis', 'analytics', 'statistics', 'pandas', 'tensorflow', 'pytorch'],
        'mobile': ['mobile', 'ios', 'android', 'react native', 'flutter', 'app development', 'swift', 'kotlin'],
        'security': ['security', 'cybersecurity', 'infosec', 'authentication', 'authorization', 'encryption', 'compliance'],
        'trading': ['trading', 'day trading', 'stocks', 'crypto', 'finance', 'market', 'technical analysis', 'tradingview', 'trading bot'],
        'content': ['content', 'creator', 'video', 'youtube', 'social media', 'editing', 'production', 'creative'],
        'coding': ['python', 'javascript', 'js', 'coding', 'programming', 'development', 'software', 'vs code'],
    }
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.personas_dir = data_dir / "personas"
        self.personas_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_personas_from_profile(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate expert personas based on user profile using hybrid approach."""
        console.print("\n[bold cyan]🤖 Generating Expert Personas...[/bold cyan]\n")
        
        generated_personas = []
        profession = user_profile.get('profession', '')
        
        # Extract core professions intelligently
        core_professions = []
        if ',' in profession:
            # Comma-separated list
            core_professions = [p.strip() for p in profession.split(',')[:3] if p.strip()]
        elif '.' in profession:
            # Get first sentence
            first_sentence = profession.split('.')[0].strip()
            core_professions = [first_sentence]
        else:
            # Single profession statement - extract key profession words
            # Look for "I am a X" or "I'm a X" patterns
            import re
            match = re.search(r"(?:I am a|I'm a|I am an|I'm an)\s+([^,\.]+)", profession, re.IGNORECASE)
            if match:
                core_professions = [match.group(1).strip()]
            else:
                # Fallback: use first 3-5 words
                words = profession.split()[:5]
                core_professions = [' '.join(words)]
        
        # Step 1: Try template-based generation for known tech domains
        detected_domains = self._detect_domains(user_profile)
        
        # Only use templates if they're relevant (limit to 1-2)
        for domain in detected_domains[:2]:
            persona = self._create_persona(domain, user_profile)
            if persona:
                generated_personas.append(persona)
                self._save_persona(persona)
                console.print(f"[green]✓[/green] Created: {persona['name']} ({persona['role']})")
        
        # Step 2: Always use AI for the user's stated professions
        from .ai_persona_generator import AIPersonaGenerator
        ai_generator = AIPersonaGenerator(self.data_dir)
        
        for prof in core_professions:
            if prof and prof.lower() not in ['general work', 'work', 'general']:
                console.print(f"[cyan]Generating AI persona for: {prof}...[/cyan]")
                ai_persona = ai_generator.generate_persona_for_profession(prof, user_profile)
                if ai_persona:
                    # Convert AI persona to our format
                    persona_data = {
                        'name': ai_persona['name'],
                        'role': ai_persona['role'],
                        'expertise': ai_persona['expertise'],
                        'system_prompt': ai_persona['system_prompt'],
                        'generated_by': 'ai',
                        'profession': prof
                    }
                    generated_personas.append(persona_data)
                    
                    # Save it
                    filename = f"{prof.lower().replace(' ', '_').replace('/', '_')}_expert.json"
                    ai_generator.save_persona(persona_data, filename)
        
        console.print(f"\n[green]Generated {len(generated_personas)} expert personas![/green]\n")
        return generated_personas
    
    def _detect_domains(self, user_profile: Dict[str, Any]) -> List[str]:
        """Detect relevant domains from user profile."""
        detected = set()
        
        # Check profession and daily tasks
        profession = user_profile.get('profession', '')
        daily_tasks = user_profile.get('daily_tasks', [])
        needed_skills = user_profile.get('needed_skills', [])
        hobbies = user_profile.get('hobbies', [])
        
        all_activities = ' '.join([profession, *daily_tasks, *needed_skills, *hobbies]).lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in all_activities for keyword in keywords):
                detected.add(domain)
        
        # Check languages and tools
        languages = user_profile.get('programming_languages', [])
        tools = user_profile.get('tools_used', [])
        
        all_tech = ' '.join([*languages, *tools]).lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in all_tech for keyword in keywords):
                detected.add(domain)
        
        # Check industry
        industries = user_profile.get('industry', [])
        all_industries = ' '.join(industries).lower()
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(keyword in all_industries for keyword in keywords):
                detected.add(domain)
        
        return list(detected)
    
    def _create_persona(self, domain: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create a persona for a specific domain."""
        template = self.DOMAIN_TEMPLATES.get(domain)
        if not template:
            return None
        
        # Build user context
        user_stack = ', '.join([
            *user_profile.get('languages', []),
            *user_profile.get('frameworks', [])
        ])
        
        # Format system prompt with user context
        system_prompt = template.system_prompt_template.format(
            technologies=user_stack,
            expertise_areas=', '.join(template.expertise_areas),
            user_stack=user_stack,
            user_experience=user_profile.get('experience_level', 'intermediate'),
            user_preferences=f"Communication: {user_profile.get('communication_style', 'conversational')}, "
                           f"Code help: {user_profile.get('code_style', 'step-by-step')}"
        )
        
        # Create persona config
        persona = {
            'name': template.name,
            'role': template.role,
            'domain': domain,
            'expertise_areas': template.expertise_areas,
            'cognitive_profile': {
                'traits': template.base_traits,
                'communication_style': user_profile.get('communication_style', 'conversational'),
                'thinking_style': 'systematic',
                'response_depth': user_profile.get('code_style', 'step-by-step')
            },
            'system_prompt': system_prompt,
            'user_context': {
                'profession': user_profile.get('profession'),
                'experience_level': user_profile.get('experience_level'),
                'work_areas': user_profile.get('work_areas', []),
                'languages': user_profile.get('languages', []),
                'frameworks': user_profile.get('frameworks', []),
                'tools': user_profile.get('tools', []),
                'challenges': user_profile.get('challenges', []),
                'projects': user_profile.get('projects', [])
            },
            'auto_generated': True,
            'created_from_profile': True
        }
        
        return persona
    
    def _save_persona(self, persona: Dict[str, Any]):
        """Save persona to disk."""
        persona_file = self.personas_dir / f"{persona['name'].lower().replace(' ', '_')}.json"
        with open(persona_file, 'w') as f:
            json.dump(persona, f, indent=2)
    
    def load_generated_personas(self) -> List[Dict[str, Any]]:
        """Load all auto-generated personas."""
        personas = []
        for persona_file in self.personas_dir.glob("*.json"):
            with open(persona_file, 'r') as f:
                persona_data = json.load(f)
                if persona_data.get('auto_generated'):
                    personas.append(persona_data)
        return personas
