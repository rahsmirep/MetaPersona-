"""
MetaPersona - Persona Agent
The main autonomous agent that acts in the user's style.
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from .cognitive_profile import CognitiveProfile, ProfileManager
from .llm_provider import LLMProvider, get_llm_provider
from .skills import SkillManager


class PersonaAgent:
    """Autonomous agent that learns and acts in user's style."""
    
    def __init__(self, profile: CognitiveProfile, llm_provider: LLMProvider, skill_manager: Optional[SkillManager] = None, adaptive_profile=None):
        self.profile = profile
        self.llm = llm_provider
        self.skill_manager = skill_manager or SkillManager()
        self.conversation_history: List[Dict] = []
        self.adaptive_profile = adaptive_profile  # UserProfile from user_profiling module
        
    def build_system_prompt(self) -> str:
        """Build system prompt based on cognitive profile and optional adaptive profile."""
        base_prompt = f"""You are an AI agent trained to act as {self.profile.user_id}. Your goal is to respond to tasks and questions exactly as they would.

{self._get_adaptive_context()}

**Writing Style:**
- Tone: {self.profile.writing_style.tone}
- Vocabulary Level: {self.profile.writing_style.vocabulary_level}
- Sentence Structure: {self.profile.writing_style.sentence_structure}
- Punctuation Style: {self.profile.writing_style.punctuation_style}

**Decision-Making Approach:**
- Style: {self.profile.decision_pattern.approach}
- Risk Tolerance: {self.profile.decision_pattern.risk_tolerance}
- Priorities: {json.dumps(self.profile.decision_pattern.priority_weights)}

**Communication Preferences:**
{json.dumps(self.profile.preferences.communication, indent=2)}

**Work Style:**
{json.dumps(self.profile.preferences.work_style, indent=2)}

**Example Writings:**
{chr(10).join([f"- {ex}" for ex in self.profile.writing_style.examples[-5:]])}

{self.skill_manager.generate_skill_prompt()}

Remember: You ARE this person. Think, write, and decide as they would. Maintain consistency with their established patterns and preferences.

**When to use skills:**
- ONLY use skills for concrete actions like file operations, calculations, or web searches
- DO NOT use skills for conversational questions, explanations, or philosophical discussions
- For questions about yourself or conceptual topics, respond naturally in conversation

**How to use skills:**
When you need to perform a concrete action, respond with JSON:
{{"action": "use_skill", "skill": "skill_name", "parameters": {{"param": "value"}}}}

For everything else, respond naturally as this person would in conversation."""
        
        return base_prompt
    
    def _get_adaptive_context(self) -> str:
        """Generate adaptive context from user profile if available."""
        if not self.adaptive_profile:
            return ""
        
        industries = ', '.join(self.adaptive_profile.industry) if self.adaptive_profile.industry else 'Not specified'
        context = f"""**Context About Your User:**
- Profession: {self.adaptive_profile.profession} ({self.adaptive_profile.job_level} level)
- Industry: {industries}
- Technical level: {self.adaptive_profile.technical_level}
- Communication style: {self.adaptive_profile.preferred_communication_style}
"""
        
        if self.adaptive_profile.daily_tasks:
            context += f"- Daily work: {', '.join(self.adaptive_profile.daily_tasks[:3])}\n"
        
        if self.adaptive_profile.programming_languages:
            context += f"- Programming languages: {', '.join(self.adaptive_profile.programming_languages)}\n"
        
        if self.adaptive_profile.needed_skills:
            context += f"\n**They Need Help With:**\n"
            for skill in self.adaptive_profile.needed_skills[:5]:
                context += f"- {skill}\n"
        
        context += "\n**Your Role as AI Assistant:**\n"
        context += "- Provide EXPERT knowledge and guidance in their field\n"
        context += "- Act as a knowledgeable advisor and problem-solver\n"
        context += "- Share insights, best practices, and solutions\n"
        context += "- Support their work with your expertise\n\n"
        
        context += "**Communication Approach:**\n"
        if self.adaptive_profile.preferred_communication_style == "casual":
            context += "- Friendly and approachable\n- Clear explanations without excessive jargon\n"
        elif self.adaptive_profile.preferred_communication_style == "technical":
            context += "- Technical and precise\n- Include detailed specifications and technical depth\n"
        else:
            context += "- Professional and solution-focused\n- Balance expertise with clarity\n"
        
        return context + "\n"
    
    def process_task(self, task: str, context: Optional[str] = None) -> str:
        """Process a task and generate response in user's style."""
        print(f"\n🤖 Processing task: {task[:50]}...")
        
        # Build messages
        messages = [
            {"role": "system", "content": self.build_system_prompt()}
        ]
        
        # Add conversation history (last 5 interactions)
        messages.extend(self.conversation_history[-10:])
        
        # Add current task
        user_message = task
        if context:
            user_message = f"Context: {context}\n\nTask: {task}"
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        try:
            response = self.llm.generate(messages, temperature=0.7)
            
            # Check if response is a skill request
            response = self._handle_skill_request(response)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": task})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            return f"Error processing task: {str(e)}"
    
    def _handle_skill_request(self, response: str) -> str:
        """Check if response contains a skill request and execute it."""
        try:
            # Try to parse as JSON
            if response.strip().startswith("{") and "use_skill" in response:
                import json
                request = json.loads(response)
                
                if request.get("action") == "use_skill":
                    skill_name = request.get("skill")
                    parameters = request.get("parameters", {})
                    
                    # Execute skill
                    result = self.skill_manager.execute_skill(skill_name, **parameters)
                    
                    if result.success:
                        return f"✓ Skill executed successfully:\n{result.data}"
                    else:
                        # If skill fails, return normal response without skill
                        # This prevents disrupting the conversation
                        return response.split('\n')[0] if '\n' in response else response
        except:
            pass  # Not a skill request, return original response
        
        return response
    
    def make_decision(self, decision_prompt: str, options: List[str]) -> Dict:
        """Make a decision based on user's decision patterns."""
        print(f"\n🎯 Making decision: {decision_prompt[:50]}...")
        
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        task = f"""Decision Required: {decision_prompt}

Options:
{options_text}

Based on my decision-making style and priorities, which option should I choose? Explain your reasoning and provide the choice number."""
        
        response = self.process_task(task)
        
        return {
            "prompt": decision_prompt,
            "options": options,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def learn_from_example(self, example_text: str, example_type: str = "writing"):
        """Learn from a new example of user behavior."""
        print(f"📚 Learning from {example_type} example...")
        
        if example_type == "writing":
            self.profile.writing_style.examples.append(example_text)
            self.profile.writing_style.examples = self.profile.writing_style.examples[-50:]
    
    def update_preferences(self, category: str, preferences: Dict):
        """Update preferences in the profile."""
        if category == "communication":
            self.profile.preferences.communication.update(preferences)
        elif category == "work_style":
            self.profile.preferences.work_style.update(preferences)
        elif category == "interaction_style":
            self.profile.preferences.interaction_style.update(preferences)
        else:
            self.profile.preferences.custom.update(preferences)
    
    def get_agent_status(self) -> Dict:
        """Get current agent status and metrics."""
        return {
            "user_id": self.profile.user_id,
            "total_interactions": self.profile.interaction_count,
            "feedback_received": self.profile.feedback_received,
            "accuracy_score": f"{self.profile.accuracy_score:.2%}",
            "writing_examples": len(self.profile.writing_style.examples),
            "decision_history": len(self.profile.decision_pattern.past_decisions),
            "last_updated": self.profile.updated_at
        }
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []


class AgentManager:
    """Manages the persona agent lifecycle."""
    
    def __init__(self, data_dir: str = "./data", encryption_key: str = None):
        self.profile_manager = ProfileManager(data_dir, encryption_key)
        self.data_dir = data_dir
        
    def initialize_agent(self, user_id: str = None, provider_name: str = None, use_adaptive_profile: bool = False) -> PersonaAgent:
        """Initialize or load persona agent with optional adaptive profile."""
        # Load or create profile
        profile = self.profile_manager.load_profile()
        if not profile:
            if not user_id:
                user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            profile = self.profile_manager.create_profile(user_id)
        
        # Initialize LLM provider
        llm = get_llm_provider(provider_name)
        
        # Initialize skill manager and load built-in skills
        from .skills.builtin import CalculatorSkill, FileOpsSkill, WebSearchSkill
        skill_manager = SkillManager()
        skill_manager.registry.register(CalculatorSkill())
        skill_manager.registry.register(FileOpsSkill())
        skill_manager.registry.register(WebSearchSkill())
        
        # Load adaptive profile if requested
        adaptive_profile = None
        if use_adaptive_profile:
            from .user_profiling import UserProfilingSystem
            profiling_system = UserProfilingSystem(self.data_dir)
            adaptive_profile = profiling_system.load_profile(profile.user_id)
            
            if adaptive_profile:
                print(f"✓ Loaded adaptive profile: {adaptive_profile.profession} ({adaptive_profile.preferred_communication_style})")
        
        # Create agent
        agent = PersonaAgent(profile, llm, skill_manager, adaptive_profile)
        print(f"✓ Persona Agent initialized for: {profile.user_id}")
        print(f"✓ Loaded {len(skill_manager.list_available_skills())} skills")
        
        return agent
    
    def save_agent_state(self, agent: PersonaAgent):
        """Save agent's profile state."""
        self.profile_manager.save_profile(agent.profile)
