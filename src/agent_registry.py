"""
Agent Registry for managing multiple agents in the system.
Handles registration, discovery, and lifecycle management of agents.
"""
from typing import Dict, List, Optional, Type
from pathlib import Path
import json

from .agent_base import BaseAgent


class AgentRegistry:
    """
    Central registry for managing all agents in the system.
    
    Supports:
    - Agent registration and deregistration
    - Agent discovery by ID or role
    - Listing all available agents
    - Persisting registry state
    """
    
    def __init__(self, data_dir: Path = Path("./data")):
        """
        Initialize the agent registry.
        
        Args:
            data_dir: Directory to store registry data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.data_dir / "agent_registry.json"
        
        # Active agents in memory
        self._agents: Dict[str, BaseAgent] = {}
        
        # Registry metadata (persisted to disk)
        self._registry_data: Dict[str, Dict] = {}
        
        self._load_registry()
    
    def register(self, agent: BaseAgent) -> bool:
        """
        Register an agent in the registry.
        
        Args:
            agent: Agent instance to register
            
        Returns:
            True if registration successful, False if agent_id already exists
        """
        if agent.agent_id in self._agents:
            print(f"Warning: Agent {agent.agent_id} already registered. Overwriting.")
        
        self._agents[agent.agent_id] = agent
        
        # Store metadata
        self._registry_data[agent.agent_id] = {
            "agent_id": agent.agent_id,
            "role": agent.role,
            "description": agent.description,
            "capabilities": [cap.model_dump() for cap in agent.capabilities],
            "skills_count": len(agent.skills_manager.registry.list_skills()),
            "registered_at": agent.memory.created_at.isoformat()
        }
        
        self._save_registry()
        return True
    
    def deregister(self, agent_id: str) -> bool:
        """
        Remove an agent from the registry.
        
        Args:
            agent_id: ID of agent to remove
            
        Returns:
            True if agent was removed, False if not found
        """
        if agent_id in self._agents:
            del self._agents[agent_id]
            if agent_id in self._registry_data:
                del self._registry_data[agent_id]
            self._save_registry()
            return True
        return False
    
    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_by_role(self, role: str) -> List[BaseAgent]:
        """
        Get all agents with a specific role.
        
        Args:
            role: Role to search for (e.g., "researcher", "coder")
            
        Returns:
            List of agents with matching role
        """
        return [
            agent for agent in self._agents.values()
            if agent.role.lower() == role.lower()
        ]
    
    def list_all(self) -> List[BaseAgent]:
        """
        Get all registered agents.
        
        Returns:
            List of all agents
        """
        return list(self._agents.values())
    
    def list_roles(self) -> List[str]:
        """
        Get all unique roles in the registry.
        
        Returns:
            List of role names
        """
        return list(set(agent.role for agent in self._agents.values()))
    
    def get_agents_for_task(
        self,
        task: str,
        min_confidence: float = 0.5
    ) -> List[tuple[BaseAgent, float]]:
        """
        Find agents capable of handling a task.
        
        Args:
            task: Task description
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of (agent, confidence) tuples, sorted by confidence (highest first)
        """
        candidates = []
        
        for agent in self._agents.values():
            confidence = agent.can_handle_task(task)
            if confidence >= min_confidence:
                candidates.append((agent, confidence))
        
        # Sort by confidence (descending)
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates
    
    def get_status(self) -> Dict:
        """
        Get overall registry status.
        
        Returns:
            Status dictionary with registry information
        """
        return {
            "total_agents": len(self._agents),
            "roles": self.list_roles(),
            "agents": [
                {
                    "agent_id": agent.agent_id,
                    "role": agent.role,
                    "description": agent.description,
                    "capabilities_count": len(agent.capabilities),
                    "skills_count": len(agent.skills_manager.registry.list_skills()),
                    "interactions_count": len(agent.memory.interactions)
                }
                for agent in self._agents.values()
            ]
        }
    
    def _load_registry(self):
        """Load registry metadata from disk."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self._registry_data = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load agent registry: {e}")
                self._registry_data = {}
    
    def _save_registry(self):
        """Save registry metadata to disk."""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self._registry_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save agent registry: {e}")
    
    def __len__(self) -> int:
        """Return number of registered agents."""
        return len(self._agents)
    
    def __contains__(self, agent_id: str) -> bool:
        """Check if agent is registered."""
        return agent_id in self._agents
    
    def __str__(self) -> str:
        return f"AgentRegistry(agents={len(self._agents)}, roles={len(self.list_roles())})"
