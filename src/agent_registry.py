"""
Agent Registry for managing multiple agents in the system.
Handles registration, discovery, and lifecycle management of agents.
"""
from typing import Dict, List, Optional, Type
from pathlib import Path
import json

from .agent_base import BaseAgent



# All agent registration and lookup is now unified through SingleUseAgent
from src.single_use_agent import SingleUseAgent

class AgentRegistry:
    def __init__(self):
        self._agents: dict = {}

    def register(self, agent_id: str, initial_mode: str = 'greeting'):
        self._agents[agent_id] = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def get(self, agent_id: str) -> SingleUseAgent:
        return self._agents.get(agent_id)

    def list_all(self) -> list:
        return list(self._agents.values())
