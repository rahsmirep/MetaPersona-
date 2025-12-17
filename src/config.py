"""
MetaPersona Configuration
Central configuration management for the system.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(default="openai", description="LLM provider name")
    api_key: Optional[str] = Field(default=None, description="API key")
    model: str = Field(default="gpt-4o-mini", description="Model name")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Generation temperature")
    max_tokens: int = Field(default=4096, description="Maximum tokens")


class StorageConfig(BaseModel):
    """Storage configuration."""
    data_dir: Path = Field(default=Path("./data"), description="Data directory")
    encryption_enabled: bool = Field(default=True, description="Enable profile encryption")
    backup_enabled: bool = Field(default=False, description="Enable automatic backups")
    backup_dir: Optional[Path] = Field(default=None, description="Backup directory")


class AgentConfig(BaseModel):
    """Agent behavior configuration."""
    conversation_history_limit: int = Field(default=10, description="Max conversation history")
    auto_save: bool = Field(default=True, description="Auto-save after interactions")
    learning_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Learning rate")
    feedback_prompt: bool = Field(default=True, description="Prompt for feedback")


class MetaPersonaConfig(BaseModel):
    """Main configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)
    
    @classmethod
    def from_env(cls) -> 'MetaPersonaConfig':
        """Load configuration from environment variables."""
        
        # LLM Config
        llm_provider = os.getenv("LLM_PROVIDER", "openai")
        api_key = None
        model = None
        
        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        elif llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        elif llm_provider == "ollama":
            model = os.getenv("OLLAMA_MODEL", "llama3")
        
        llm_config = LLMConfig(
            provider=llm_provider,
            api_key=api_key,
            model=model
        )
        
        # Storage Config
        data_dir = Path(os.getenv("DATA_DIR", "./data"))
        encryption = os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true"
        
        storage_config = StorageConfig(
            data_dir=data_dir,
            encryption_enabled=encryption
        )
        
        # Agent Config
        agent_config = AgentConfig()
        
        return cls(
            llm=llm_config,
            storage=storage_config,
            agent=agent_config
        )
    
    def save_to_file(self, filepath: str = "config.yaml"):
        """Save configuration to file."""
        import yaml
        with open(filepath, 'w') as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False)
    
    @classmethod
    def load_from_file(cls, filepath: str = "config.yaml") -> 'MetaPersonaConfig':
        """Load configuration from file."""
        import yaml
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        return cls(**data)


# Global config instance
_config: Optional[MetaPersonaConfig] = None


def get_config() -> MetaPersonaConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = MetaPersonaConfig.from_env()
    return _config


def reload_config():
    """Reload configuration from environment."""
    global _config
    _config = MetaPersonaConfig.from_env()
