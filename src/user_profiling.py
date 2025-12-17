"""
User Profiling & Adaptive System
Learn about users and adapt capabilities, skills, and tone dynamically.
"""
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Structured user profile from onboarding."""
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Professional Information
    profession: str = ""
    industry: List[str] = Field(default_factory=list)  # Can work in multiple industries
    job_level: str = ""  # entry, mid, senior, executive
    technical_level: str = ""  # beginner, intermediate, advanced, expert
    
    # Personal Information
    hobbies: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    learning_goals: List[str] = Field(default_factory=list)
    
    # Daily Work Context
    daily_tasks: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    
    # Skill Preferences
    needed_skills: List[str] = Field(default_factory=list)
    preferred_communication_style: str = "professional"  # casual, professional, technical
    help_frequency: str = "moderate"  # occasional, moderate, frequent
    
    # Adaptive Settings
    loaded_skill_packs: List[str] = Field(default_factory=list)
    agent_routing_preferences: Dict[str, float] = Field(default_factory=dict)
    custom_agents: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OnboardingQuestion(BaseModel):
    """Single onboarding question."""
    id: str
    question: str
    question_type: str  # text, choice, multi_choice, tags
    options: Optional[List[str]] = None
    category: str
    required: bool = True
    follow_up: Optional[str] = None


class SkillPack(BaseModel):
    """A package of related skills for a specific profession/context."""
    pack_id: str
    name: str
    description: str
    target_professions: List[str]
    target_industries: List[str]
    skills: List[str]
    agent_weights: Dict[str, float] = Field(default_factory=dict)
    custom_prompt_additions: Optional[str] = None


class UserProfilingSystem:
    """
    Main system for user profiling and adaptive loading.
    Handles onboarding, profile management, and dynamic adaptation.
    """
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.profiles_dir = self.data_dir / "user_profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        self.onboarding_questions = self._define_onboarding_questions()
        self.skill_packs = self._define_skill_packs()
    
    def _define_onboarding_questions(self) -> List[OnboardingQuestion]:
        """Define the onboarding questionnaire."""
        return [
            OnboardingQuestion(
                id="profession",
                question="What is your profession or primary role?",
                question_type="text",
                category="professional",
                required=True
            ),
            OnboardingQuestion(
                id="industry",
                question="Which industry do you work in? (Select all that apply)",
                question_type="multi_choice",
                options=[
                    "Technology/Software",
                    "Healthcare/Medical",
                    "Finance/Banking",
                    "Education",
                    "Retail/Sales",
                    "Manufacturing",
                    "Creative/Arts",
                    "Legal",
                    "Marketing",
                    "Other"
                ],
                category="professional",
                required=True
            ),
            OnboardingQuestion(
                id="job_level",
                question="What is your experience level?",
                question_type="choice",
                options=["Entry Level", "Mid-Level", "Senior", "Executive/Leadership"],
                category="professional",
                required=True
            ),
            OnboardingQuestion(
                id="technical_level",
                question="How would you rate your technical proficiency?",
                question_type="choice",
                options=["Beginner", "Intermediate", "Advanced", "Expert"],
                category="professional",
                required=True
            ),
            OnboardingQuestion(
                id="daily_tasks",
                question="What are your top 3-5 daily tasks? (comma-separated)",
                question_type="tags",
                category="work_context",
                required=True
            ),
            OnboardingQuestion(
                id="tools_used",
                question="What tools/software do you use regularly? (comma-separated)",
                question_type="tags",
                category="work_context",
                required=True
            ),
            OnboardingQuestion(
                id="programming_languages",
                question="Do you code? If yes, which languages? (comma-separated, or 'none')",
                question_type="tags",
                category="technical",
                required=False
            ),
            OnboardingQuestion(
                id="hobbies",
                question="What are your hobbies or interests? (comma-separated)",
                question_type="tags",
                category="personal",
                required=False
            ),
            OnboardingQuestion(
                id="needed_skills",
                question="What areas would YOU like me to help you with?",
                question_type="multi_choice",
                options=[
                    "Research & Information Gathering",
                    "Writing & Documentation",
                    "Coding & Development",
                    "Data Analysis",
                    "Project Management",
                    "Creative Content",
                    "Problem Solving",
                    "Learning New Topics",
                    "Task Automation",
                    "Communication"
                ],
                category="preferences",
                required=True
            ),
            OnboardingQuestion(
                id="communication_style",
                question="How do YOU prefer to communicate? (I'll match your style)",
                question_type="choice",
                options=["Casual & Friendly", "Professional & Formal", "Technical & Precise"],
                category="preferences",
                required=True
            ),
            OnboardingQuestion(
                id="help_frequency",
                question="How often do YOU plan to use me as your assistant?",
                question_type="choice",
                options=["Occasionally", "Regularly", "Daily"],
                category="preferences",
                required=False
            )
        ]
    
    def _define_skill_packs(self) -> List[SkillPack]:
        """Define skill packs for different professions/contexts."""
        return [
            SkillPack(
                pack_id="developer",
                name="Software Developer Pack",
                description="Skills for programming, debugging, and development",
                target_professions=["developer", "programmer", "engineer", "software"],
                target_industries=["Technology/Software"],
                skills=["code_generation", "debugging", "api_docs", "git_ops", "testing"],
                agent_weights={"coder": 1.2, "researcher": 1.1},
                custom_prompt_additions="Focus on code quality, best practices, and technical accuracy."
            ),
            SkillPack(
                pack_id="healthcare",
                name="Healthcare Professional Pack",
                description="Medical research, patient documentation, clinical support",
                target_professions=["doctor", "nurse", "physician", "medical", "healthcare"],
                target_industries=["Healthcare/Medical"],
                skills=["medical_research", "documentation", "data_analysis", "terminology"],
                agent_weights={"researcher": 1.3, "writer": 1.1},
                custom_prompt_additions="Use precise medical terminology. Prioritize accuracy and evidence-based information."
            ),
            SkillPack(
                pack_id="business",
                name="Business Professional Pack",
                description="Business analysis, reporting, communication",
                target_professions=["manager", "analyst", "consultant", "executive"],
                target_industries=["Finance/Banking", "Marketing"],
                skills=["data_analysis", "reporting", "presentation", "email_drafting"],
                agent_weights={"writer": 1.2, "researcher": 1.1},
                custom_prompt_additions="Focus on business outcomes, ROI, and professional communication."
            ),
            SkillPack(
                pack_id="creative",
                name="Creative Professional Pack",
                description="Content creation, writing, design support",
                target_professions=["writer", "designer", "artist", "content creator"],
                target_industries=["Creative/Arts", "Marketing"],
                skills=["content_creation", "brainstorming", "editing", "research"],
                agent_weights={"writer": 1.3, "researcher": 1.0},
                custom_prompt_additions="Encourage creativity and original thinking. Focus on engaging content."
            ),
            SkillPack(
                pack_id="education",
                name="Educator Pack",
                description="Teaching support, curriculum development, research",
                target_professions=["teacher", "professor", "educator", "instructor"],
                target_industries=["Education"],
                skills=["research", "content_creation", "explanation", "assessment"],
                agent_weights={"researcher": 1.2, "writer": 1.2},
                custom_prompt_additions="Explain concepts clearly. Focus on pedagogical effectiveness."
            ),
            SkillPack(
                pack_id="retail",
                name="Retail & Sales Pack",
                description="Customer service, inventory, sales support",
                target_professions=["cashier", "retail", "sales", "customer service"],
                target_industries=["Retail/Sales"],
                skills=["communication", "problem_solving", "documentation"],
                agent_weights={"generalist": 1.2, "writer": 1.1},
                custom_prompt_additions="Focus on customer satisfaction and clear communication."
            ),
            SkillPack(
                pack_id="researcher",
                name="Research Professional Pack",
                description="Academic research, literature review, data analysis",
                target_professions=["researcher", "scientist", "analyst"],
                target_industries=["Education", "Healthcare/Medical", "Technology/Software"],
                skills=["research", "data_analysis", "documentation", "citation"],
                agent_weights={"researcher": 1.3, "writer": 1.1},
                custom_prompt_additions="Prioritize accuracy, evidence, and proper citations."
            ),
            SkillPack(
                pack_id="general",
                name="General Purpose Pack",
                description="Balanced skills for general use",
                target_professions=["*"],
                target_industries=["*"],
                skills=["web_search", "calculator", "file_ops"],
                agent_weights={"generalist": 1.0},
                custom_prompt_additions=""
            )
        ]
    
    def conduct_onboarding(self, user_id: str, interactive: bool = True) -> UserProfile:
        """
        Conduct onboarding questionnaire for a new user.
        
        Args:
            user_id: Unique user identifier
            interactive: Whether to prompt interactively or return questions
            
        Returns:
            Completed UserProfile
        """
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        
        console = Console()
        
        console.print("\n[bold cyan]🎭 Welcome to MetaPersona![/bold cyan]\n")
        console.print("[bold]I'm here to learn about YOU so I can adapt to your needs.[/bold]\n")
        console.print("I'll ask you some questions about:")
        console.print("  • Your profession and work")
        console.print("  • Your daily tasks and tools")
        console.print("  • Your technical skills and interests")
        console.print("  • How you prefer to communicate\n")
        console.print("[dim]Your answers will help me:[/dim]")
        console.print("[dim]  ✓ Load relevant skills for your profession[/dim]")
        console.print("[dim]  ✓ Adapt my communication style to match yours[/dim]")
        console.print("[dim]  ✓ Prioritize the right agents for your needs[/dim]")
        console.print("[dim]  ✓ Understand your daily workflow and context[/dim]\n")
        console.print("[yellow]Let's get started! I want to learn about you.[/yellow]\n")
        
        profile = UserProfile(user_id=user_id)
        responses = {}
        
        for question in self.onboarding_questions:
            if not interactive:
                # Return questions for non-interactive mode
                continue
            
            console.print(f"[bold]{question.question}[/bold]")
            
            if question.question_type == "text":
                answer = Prompt.ask("  ")
                responses[question.id] = answer
                
            elif question.question_type == "choice":
                console.print("[dim]Options:[/dim]")
                for i, opt in enumerate(question.options, 1):
                    console.print(f"  {i}. {opt}")
                choice = Prompt.ask("  Select", choices=[str(i) for i in range(1, len(question.options) + 1)])
                answer = question.options[int(choice) - 1]
                responses[question.id] = answer
                
            elif question.question_type == "multi_choice":
                console.print("[dim]Select all that apply (comma-separated numbers):[/dim]")
                for i, opt in enumerate(question.options, 1):
                    console.print(f"  {i}. {opt}")
                choices = Prompt.ask("  Select").split(",")
                answers = [question.options[int(c.strip()) - 1] for c in choices if c.strip().isdigit()]
                responses[question.id] = answers
                
            elif question.question_type == "tags":
                answer = Prompt.ask("  ")
                tags = [t.strip() for t in answer.split(",") if t.strip()]
                responses[question.id] = tags
            
            console.print()
        
        # Map responses to profile
        profile.profession = responses.get("profession", "").lower()
        profile.industry = responses.get("industry", "")
        profile.job_level = responses.get("job_level", "").lower().replace(" ", "_").replace("/", "_")
        profile.technical_level = responses.get("technical_level", "").lower()
        profile.daily_tasks = responses.get("daily_tasks", [])
        profile.tools_used = responses.get("tools_used", [])
        
        prog_langs = responses.get("programming_languages", [])
        if prog_langs and prog_langs[0].lower() != "none":
            profile.programming_languages = prog_langs
        
        profile.hobbies = responses.get("hobbies", [])
        profile.needed_skills = responses.get("needed_skills", [])
        
        comm_style = responses.get("communication_style", "Professional & Formal")
        if "casual" in comm_style.lower():
            profile.preferred_communication_style = "casual"
        elif "technical" in comm_style.lower():
            profile.preferred_communication_style = "technical"
        else:
            profile.preferred_communication_style = "professional"
        
        freq = responses.get("help_frequency", "Regularly")
        profile.help_frequency = freq.lower()
        
        # Auto-load appropriate skill packs
        profile.loaded_skill_packs = self._determine_skill_packs(profile)
        profile.agent_routing_preferences = self._calculate_agent_weights(profile)
        
        # Save profile
        self.save_profile(profile)
        
        console.print("\n[bold green]✓ Got it! I've learned about you and created your profile.[/bold green]\n")
        console.print("[cyan]Here's what I now know about YOU:[/cyan]")
        console.print(f"  • Your profession: {profile.profession}")
        console.print(f"  • Your industry: {', '.join(profile.industry) if profile.industry else 'Not specified'}")
        console.print(f"  • Your technical level: {profile.technical_level}")
        console.print(f"  • Your preferred style: {profile.preferred_communication_style}\n")
        console.print("[bold cyan]I've adapted myself for you:[/bold cyan]")
        console.print(f"  • Loaded {len(profile.loaded_skill_packs)} skill pack(s) for your profession")
        console.print(f"  • Adjusted agent routing to prioritize your needs")
        console.print(f"  • Set communication style to match yours\n")
        console.print("[yellow]I'm now ready to assist YOU based on what I learned![/yellow]\n")
        
        return profile
    
    def _determine_skill_packs(self, profile: UserProfile) -> List[str]:
        """Determine which skill packs to load based on profile."""
        loaded_packs = ["general"]  # Always load general
        
        profession_lower = profile.profession.lower()
        
        for pack in self.skill_packs:
            if pack.pack_id == "general":
                continue
            
            # Check profession match
            profession_match = any(
                prof in profession_lower 
                for prof in pack.target_professions
            )
            
            # Check industry match (user can have multiple industries)
            industry_match = (
                any(ind in pack.target_industries for ind in profile.industry) or
                "*" in pack.target_industries
            )
            
            if profession_match or industry_match:
                loaded_packs.append(pack.pack_id)
        
        return loaded_packs
    
    def _calculate_agent_weights(self, profile: UserProfile) -> Dict[str, float]:
        """Calculate agent routing weight adjustments based on profile."""
        weights = {
            "researcher": 1.0,
            "coder": 1.0,
            "writer": 1.0,
            "generalist": 1.0
        }
        
        # Apply skill pack weights
        for pack_id in profile.loaded_skill_packs:
            pack = self.get_skill_pack(pack_id)
            if pack:
                for agent_id, weight in pack.agent_weights.items():
                    weights[agent_id] = max(weights.get(agent_id, 1.0), weight)
        
        # Adjust based on technical level
        if profile.technical_level in ["advanced", "expert"]:
            weights["coder"] *= 1.1
            weights["researcher"] *= 1.1
        elif profile.technical_level == "beginner":
            weights["generalist"] *= 1.1
        
        # Adjust based on programming languages
        if profile.programming_languages:
            weights["coder"] *= 1.15
        
        return weights
    
    def get_skill_pack(self, pack_id: str) -> Optional[SkillPack]:
        """Get skill pack by ID."""
        for pack in self.skill_packs:
            if pack.pack_id == pack_id:
                return pack
        return None
    
    def save_profile(self, profile: UserProfile):
        """Save user profile to disk."""
        profile.updated_at = datetime.now()
        profile_path = self.profiles_dir / f"{profile.user_id}.json"
        with open(profile_path, 'w') as f:
            json.dump(profile.model_dump(), f, indent=2, default=str)
    
    def load_profile(self, user_id: str) -> Optional[UserProfile]:
        """Load user profile from disk."""
        profile_path = self.profiles_dir / f"{user_id}.json"
        if not profile_path.exists():
            return None
        
        with open(profile_path, 'r') as f:
            data = json.load(f)
            
            # Migrate old profiles: convert industry string to list
            if 'industry' in data and isinstance(data['industry'], str):
                data['industry'] = [data['industry']] if data['industry'] else []
            
            return UserProfile(**data)
    
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update specific fields in user profile."""
        profile = self.load_profile(user_id)
        if not profile:
            return None
        
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        # Recalculate adaptive settings
        profile.loaded_skill_packs = self._determine_skill_packs(profile)
        profile.agent_routing_preferences = self._calculate_agent_weights(profile)
        
        self.save_profile(profile)
        return profile
    
    def get_adaptive_system_prompt(self, profile: UserProfile) -> str:
        """Generate adaptive system prompt based on user profile."""
        industries = ', '.join(profile.industry) if profile.industry else 'Not specified'
        prompt = f"""You are an AI assistant helping {profile.user_id}. Your role is to ASSIST them, not act as them.

**Your User's Background (so you can help them better):**
- Profession: {profile.profession} ({profile.job_level} level)
- Industry: {industries}
- Technical skill: {profile.technical_level}
- Communication preference: {profile.preferred_communication_style}

**What They Do Daily:**
- Tasks: {', '.join(profile.daily_tasks[:5])}
- Tools: {', '.join(profile.tools_used[:5])}
"""
        
        if profile.programming_languages:
            prompt += f"- Programming: {', '.join(profile.programming_languages)}\n"
        
        prompt += f"""
**Areas They Want Your Support:**
{chr(10).join(['- ' + skill for skill in profile.needed_skills])}

**Your Role:**
You are their AI ASSISTANT and EXPERT ADVISOR. Use your knowledge to:
- Provide insights and expertise in their field ({profile.profession})
- Offer solutions and guidance for their daily tasks
- Share best practices and advanced techniques
- Answer questions with domain expertise
- Act as a knowledgeable colleague or mentor, NOT as them

**Communication Style:**
"""
        
        if profile.preferred_communication_style == "casual":
            prompt += "- Use friendly, approachable tone\n- Explain complex topics clearly\n- Be conversational but informative\n"
        elif profile.preferred_communication_style == "technical":
            prompt += "- Use precise technical language\n- Provide in-depth technical details\n- Include relevant technical specifications\n"
        else:
            prompt += "- Maintain professional, clear communication\n- Balance expertise with accessibility\n- Be direct and solution-focused\n"
        
        # Add skill pack specific prompts
        for pack_id in profile.loaded_skill_packs:
            pack = self.get_skill_pack(pack_id)
            if pack and pack.custom_prompt_additions:
                prompt += f"\n**{pack.name} Expertise:**\n{pack.custom_prompt_additions}\n"
        
        prompt += f"\n**Remember:** You are an EXPERT ASSISTANT helping {profile.user_id} excel in their work. Provide knowledge, guidance, and solutions - don't roleplay as them."
        
        return prompt
