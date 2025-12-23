"""
Test Suite for MetaPersona
Run with: pytest tests/
"""
import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.identity import IdentityLayer
from src.cognitive_profile import CognitiveProfile, ProfileManager
from src.memory_loop import MemoryLoop


class TestIdentityLayer:
    """Test identity and encryption functionality."""
    
    def test_keypair_generation(self, tmp_path):
        """Test keypair generation."""
        identity = IdentityLayer(str(tmp_path))
        result = identity.generate_keypair()
        
        assert 'public_key_fingerprint' in result
        assert (tmp_path / "private_key.pem").exists()
        assert (tmp_path / "public_key.pem").exists()
        assert (tmp_path / "identity.json").exists()
    
    def test_encryption_decryption(self, tmp_path):
        """Test data encryption and decryption."""
        identity = IdentityLayer(str(tmp_path))
        identity.generate_keypair()
        
        original_data = "This is sensitive profile data"
        passphrase = "test-passphrase-123"
        
        # Encrypt
        encrypted = identity.encrypt_data(original_data, passphrase)
        assert isinstance(encrypted, bytes)
        assert encrypted != original_data.encode()
        
        # Decrypt
        decrypted = identity.decrypt_data(encrypted, passphrase)
        assert decrypted == original_data
    
    def test_identity_exists(self, tmp_path):
        """Test identity existence check."""
        identity = IdentityLayer(str(tmp_path))
        assert not identity.identity_exists()
        
        identity.generate_keypair()
        assert identity.identity_exists()


class TestCognitiveProfile:
    """Test cognitive profile functionality."""
    
    def test_profile_creation(self, tmp_path):
        """Test profile creation."""
        pm = ProfileManager(str(tmp_path))
        profile = pm.create_profile("test_user")
        
        assert profile.user_id == "test_user"
        assert isinstance(profile.writing_style.tone, str)
        assert profile.interaction_count == 0
    
    def test_profile_save_load(self, tmp_path):
        """Test profile persistence."""
        pm = ProfileManager(str(tmp_path))
        
        # Create and modify profile
        profile = pm.create_profile("test_user")
        profile.writing_style.tone = "casual"
        profile.interaction_count = 5
        pm.save_profile(profile)
        
        # Load and verify
        loaded = pm.load_profile()
        assert loaded.user_id == "test_user"
        assert loaded.writing_style.tone == "casual"
        assert loaded.interaction_count == 5
    
    def test_update_writing_style(self, tmp_path):
        """Test writing style updates."""
        pm = ProfileManager(str(tmp_path))
        profile = pm.create_profile("test_user")
        
        example = "This is an example of my writing style."
        pm.update_writing_style(profile, example)
        
        loaded = pm.load_profile()
        assert example in loaded.writing_style.examples
    
    def test_record_interaction(self, tmp_path):
        """Test interaction recording."""
        pm = ProfileManager(str(tmp_path))
        profile = pm.create_profile("test_user")
        
        pm.record_interaction(profile, feedback_score=4.5)
        
        loaded = pm.load_profile()
        assert loaded.interaction_count == 1
        assert loaded.feedback_received == 1
from src.single_use_agent import SingleUseAgent

def test_memory_loop_feedback_and_analysis(tmp_path):
    """Test feedback addition and learning progress analysis in MemoryLoop."""
    memory = MemoryLoop(str(tmp_path))
    for i in range(3):
        memory.add_feedback(i, 4.5)
    agent = SingleUseAgent(agent_id='meta')
    result = agent.process_turn('What is MetaPersona?')
    assert result is not None

    progress = memory.analyze_learning_progress()

    assert progress['status'] == 'analyzed'
    assert progress['improvement'] > 0
    assert progress['trend'] == 'improving'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
