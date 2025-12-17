"""
Base Agent class for multi-agent system.
Provides common interface for all agents in the MetaPersona ecosystem.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import json
from pathlib import Path

from .skills.manager import SkillManager
from .llm_provider import LLMProvider


class AgentCapability(BaseModel):
    """Represents a capability that an agent has."""
    name: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)
    examples: List[str] = Field(default_factory=list)


class AgentMemory(BaseModel):
    """Agent's memory of interactions and learnings."""
    agent_id: str
    interactions: List[Dict[str, Any]] = Field(default_factory=list)
    learnings: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskResult(BaseModel):
    """Result of a task execution."""
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BaseAgent(ABC):
    """
    Base class for all agents in the multi-agent system.
    
    All agents must:
    - Have a unique role and description
    - Define their capabilities
    - Handle tasks appropriately
    - Maintain memory of interactions
    - Support skill integration
    """
    
    def __init__(
        self,
        agent_id: str,
        role: str,
        description: str,
        llm_provider: LLMProvider,
        skills_manager: Optional[SkillManager] = None,
        data_dir: Path = Path("./data/agents")
    ):
        """
        Initialize a base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            role: Agent's role (e.g., "researcher", "coder", "writer")
            description: What the agent specializes in
            llm_provider: LLM provider for generating responses
            skills_manager: Optional skills manager for tool use
            data_dir: Directory to store agent data
        """
        self.agent_id = agent_id
        self.role = role
        self.description = description
        self.llm_provider = llm_provider
        self.skills_manager = skills_manager or SkillManager()
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize memory
        self.memory = self._load_memory()
        
        # Define capabilities (subclasses should override)
        self.capabilities = self._define_capabilities()
    
    @abstractmethod
    def _define_capabilities(self) -> List[AgentCapability]:
        """
        Define what this agent is capable of doing.
        Must be implemented by subclasses.
        
        Returns:
            List of AgentCapability objects
        """
        pass
    
    @abstractmethod
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """
        Determine if this agent can handle the given task.
        
        Args:
            task: Task description
            context: Optional context information
            
        Returns:
            Confidence score (0.0 to 1.0) indicating ability to handle task
        """
        pass
    
    @abstractmethod
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """
        Execute the given task.
        
        Args:
            task: Task to execute
            context: Optional context information
            use_skills: Whether to use available skills
            
        Returns:
            TaskResult with outcome
        """
        pass
    
    def get_system_prompt(self) -> str:
        """
        Generate the system prompt for this agent.
        Can be overridden by subclasses for customization.
        
        Returns:
            System prompt string
        """
        capabilities_str = "\n".join([
            f"- {cap.name}: {cap.description}"
            for cap in self.capabilities
        ])
        
        skills_str = ""
        if self.skills_manager and self.skills_manager.registry.list_skills():
            skills_list = "\n".join([
                f"- {skill.metadata.name}: {skill.metadata.description}"
                for skill in self.skills_manager.registry.get_all().values()
            ])
            skills_str = f"\n\nAvailable Skills:\n{skills_list}"
        
        return f"""You are {self.agent_id}, a specialized AI agent.

Role: {self.role}
Description: {self.description}

Your Capabilities:
{capabilities_str}{skills_str}

Always work within your role and capabilities. Be helpful, accurate, and efficient."""
    
    def update_memory(
        self,
        interaction: Dict[str, Any],
        learning: Optional[str] = None
    ):
        """
        Update agent's memory with new interaction or learning.
        
        Args:
            interaction: Dictionary containing interaction details
            learning: Optional learning to record
        """
        self.memory.interactions.append({
            **interaction,
            "timestamp": datetime.now().isoformat()
        })
        
        if learning:
            self.memory.learnings.append(learning)
        
        self.memory.updated_at = datetime.now()
        self._save_memory()
    
    def get_recent_context(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent interactions for context.
        
        Args:
            limit: Maximum number of interactions to return
            
        Returns:
            List of recent interactions
        """
        return self.memory.interactions[-limit:]
    
    def _load_memory(self) -> AgentMemory:
        """Load agent memory from disk."""
        memory_file = self.data_dir / f"{self.agent_id}_memory.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AgentMemory(**data)
            except Exception as e:
                print(f"Warning: Could not load memory for {self.agent_id}: {e}")
        
        return AgentMemory(agent_id=self.agent_id)
    
    def _save_memory(self):
        """Save agent memory to disk."""
        memory_file = self.data_dir / f"{self.agent_id}_memory.json"
        
        try:
            with open(memory_file, 'w', encoding='utf-8') as f:
                json.dump(
                    self.memory.model_dump(),
                    f,
                    indent=2,
                    default=str
                )
        except Exception as e:
            print(f"Warning: Could not save memory for {self.agent_id}: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the agent.
        
        Returns:
            Status dictionary
        """
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "description": self.description,
            "capabilities": [cap.model_dump() for cap in self.capabilities],
            "skills_count": len(self.skills_manager.registry.list_skills()),
            "interactions_count": len(self.memory.interactions),
            "learnings_count": len(self.memory.learnings),
            "created_at": self.memory.created_at.isoformat(),
            "updated_at": self.memory.updated_at.isoformat()
        }
    
    def __str__(self) -> str:
        return f"Agent({self.agent_id}, role={self.role})"
    
    def __repr__(self) -> str:
        return self.__str__()
