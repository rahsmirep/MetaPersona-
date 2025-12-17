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
        assert loaded.accuracy_score == 4.5


class TestMemoryLoop:
    """Test memory loop and learning functionality."""
    
    def test_record_interaction(self, tmp_path):
        """Test interaction recording."""
        memory = MemoryLoop(str(tmp_path))
        
        interaction = memory.record_interaction(
            task="Test task",
            response="Test response",
            tags=["test", "demo"]
        )
        
        assert interaction.task == "Test task"
        assert interaction.response == "Test response"
        assert "test" in interaction.tags
    
    def test_load_interactions(self, tmp_path):
        """Test loading interactions."""
        memory = MemoryLoop(str(tmp_path))
        
        # Record multiple interactions
        memory.record_interaction("Task 1", "Response 1")
        memory.record_interaction("Task 2", "Response 2")
        memory.record_interaction("Task 3", "Response 3")
        
        # Load and verify
        interactions = memory.load_all_interactions()
        assert len(interactions) == 3
        assert interactions[0].task == "Task 1"
        assert interactions[2].task == "Task 3"
    
    def test_add_feedback(self, tmp_path):
        """Test feedback addition."""
        memory = MemoryLoop(str(tmp_path))
        
        memory.record_interaction("Task 1", "Response 1")
        success = memory.add_feedback(0, 4.5, "Great response")
        
        assert success
        
        interactions = memory.load_all_interactions()
        assert interactions[0].feedback_score == 4.5
        assert interactions[0].feedback_text == "Great response"
    
    def test_feedback_summary(self, tmp_path):
        """Test feedback summary generation."""
        memory = MemoryLoop(str(tmp_path))
        
        # Record interactions with feedback
        memory.record_interaction("Task 1", "Response 1")
        memory.add_feedback(0, 5.0)
        
        memory.record_interaction("Task 2", "Response 2")
        memory.add_feedback(1, 4.0)
        
        memory.record_interaction("Task 3", "Response 3")
        # No feedback for this one
        
        summary = memory.get_feedback_summary()
        
        assert summary['total_interactions'] == 3
        assert summary['feedback_count'] == 2
        assert summary['average_score'] == 4.5
        assert summary['feedback_rate'] == 2/3
    
    def test_learning_progress(self, tmp_path):
        """Test learning progress analysis."""
        memory = MemoryLoop(str(tmp_path))
        
        # Early interactions (lower scores)
        for i in range(5):
            memory.record_interaction(f"Task {i}", f"Response {i}")
            memory.add_feedback(i, 3.0)
        
        # Later interactions (higher scores)
        for i in range(5, 10):
            memory.record_interaction(f"Task {i}", f"Response {i}")
            memory.add_feedback(i, 4.5)
        
        progress = memory.analyze_learning_progress()
        
        assert progress['status'] == 'analyzed'
        assert progress['improvement'] > 0
        assert progress['trend'] == 'improving'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
