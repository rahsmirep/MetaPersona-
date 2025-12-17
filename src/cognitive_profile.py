"""
MetaPersona - Cognitive Profile
Captures and stores user's writing style, decision patterns, and preferences.
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class WritingStyle(BaseModel):
    """Captures writing tone and patterns."""
    tone: str = Field(default="neutral", description="Overall tone (formal, casual, technical, etc.)")
    vocabulary_level: str = Field(default="intermediate", description="Vocabulary complexity")
    sentence_structure: str = Field(default="varied", description="Sentence structure patterns")
    punctuation_style: str = Field(default="standard", description="Punctuation preferences")
    common_phrases: List[str] = Field(default_factory=list, description="Frequently used phrases")
    examples: List[str] = Field(default_factory=list, description="Example writings")


class DecisionPattern(BaseModel):
    """Captures decision-making style."""
    approach: str = Field(default="analytical", description="Decision approach (analytical, intuitive, cautious, etc.)")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    priority_weights: Dict[str, float] = Field(default_factory=dict, description="What matters most")
    past_decisions: List[Dict] = Field(default_factory=list, description="Historical decision examples")


class Preferences(BaseModel):
    """User preferences across different domains."""
    communication: Dict[str, Any] = Field(default_factory=dict, description="Communication preferences")
    work_style: Dict[str, Any] = Field(default_factory=dict, description="Work style preferences")
    interaction_style: Dict[str, Any] = Field(default_factory=dict, description="How to interact with users")
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom preferences")


class CognitiveProfile(BaseModel):
    """Complete cognitive profile of the user."""
    user_id: str
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"
    
    writing_style: WritingStyle = Field(default_factory=WritingStyle)
    decision_pattern: DecisionPattern = Field(default_factory=DecisionPattern)
    preferences: Preferences = Field(default_factory=Preferences)
    
    # Learning metrics
    interaction_count: int = 0
    feedback_received: int = 0
    accuracy_score: float = 0.0


class ProfileManager:
    """Manages cognitive profile storage and updates."""
    
    def __init__(self, data_dir: str = "./data", encryption_key: str = None):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.profile_path = self.data_dir / "cognitive_profile.json"
        self.encrypted_path = self.data_dir / "cognitive_profile.enc"
        self.encryption_key = encryption_key
        
    def create_profile(self, user_id: str) -> CognitiveProfile:
        """Create a new cognitive profile."""
        profile = CognitiveProfile(user_id=user_id)
        self.save_profile(profile)
        print(f"✓ Created cognitive profile for user: {user_id}")
        return profile
    
    def load_profile(self, from_encrypted: bool = False) -> Optional[CognitiveProfile]:
        """Load existing profile."""
        profile_file = self.encrypted_path if from_encrypted else self.profile_path
        
        if not profile_file.exists():
            return None
        
        if from_encrypted and self.encryption_key:
            from .identity import IdentityLayer
            identity = IdentityLayer(str(self.data_dir))
            encrypted_data = profile_file.read_bytes()
            decrypted_json = identity.decrypt_data(encrypted_data, self.encryption_key)
            return CognitiveProfile.model_validate_json(decrypted_json)
        else:
            return CognitiveProfile.model_validate_json(profile_file.read_text())
    
    def save_profile(self, profile: CognitiveProfile, encrypt: bool = False):
        """Save profile to storage."""
        profile.updated_at = datetime.now().isoformat()
        profile_json = profile.model_dump_json(indent=2)
        
        if encrypt and self.encryption_key:
            from .identity import IdentityLayer
            identity = IdentityLayer(str(self.data_dir))
            encrypted_data = identity.encrypt_data(profile_json, self.encryption_key)
            self.encrypted_path.write_bytes(encrypted_data)
        else:
            self.profile_path.write_text(profile_json)
    
    def update_writing_style(self, profile: CognitiveProfile, example: str):
        """Update writing style based on new example."""
        profile.writing_style.examples.append(example)
        # Keep only last 50 examples
        profile.writing_style.examples = profile.writing_style.examples[-50:]
        self.save_profile(profile)
    
    def update_decision_pattern(self, profile: CognitiveProfile, decision: Dict):
        """Record a decision for pattern learning."""
        decision['timestamp'] = datetime.now().isoformat()
        profile.decision_pattern.past_decisions.append(decision)
        # Keep only last 100 decisions
        profile.decision_pattern.past_decisions = profile.decision_pattern.past_decisions[-100:]
        self.save_profile(profile)
    
    def update_preferences(self, profile: CognitiveProfile, category: str, key: str, value: Any):
        """Update a specific preference."""
        if category == "communication":
            profile.preferences.communication[key] = value
        elif category == "work_style":
            profile.preferences.work_style[key] = value
        elif category == "interaction_style":
            profile.preferences.interaction_style[key] = value
        else:
            profile.preferences.custom[key] = value
        self.save_profile(profile)
    
    def record_interaction(self, profile: CognitiveProfile, feedback_score: Optional[float] = None):
        """Record an interaction and optional feedback."""
        profile.interaction_count += 1
        if feedback_score is not None:
            profile.feedback_received += 1
            # Running average of accuracy
            profile.accuracy_score = (
                (profile.accuracy_score * (profile.feedback_received - 1) + feedback_score) 
                / profile.feedback_received
            )
        self.save_profile(profile)
    
    def get_profile_summary(self, profile: CognitiveProfile) -> str:
        """Generate a summary of the profile for the agent."""
        summary = f"""
**User Cognitive Profile**

**Writing Style:**
- Tone: {profile.writing_style.tone}
- Vocabulary: {profile.writing_style.vocabulary_level}
- Structure: {profile.writing_style.sentence_structure}

**Decision Making:**
- Approach: {profile.decision_pattern.approach}
- Risk Tolerance: {profile.decision_pattern.risk_tolerance}

**Preferences:**
{json.dumps(profile.preferences.model_dump(), indent=2)}

**Learning Progress:**
- Interactions: {profile.interaction_count}
- Feedback received: {profile.feedback_received}
- Accuracy score: {profile.accuracy_score:.2%}
"""
        return summary
