"""
Specialized agent implementations for common roles.
These serve as examples of how to build agents using the BaseAgent class.
"""
from typing import Dict, List, Any, Optional
import re

from .agent_base import BaseAgent, AgentCapability
from .task_result import TaskResult

# All specialized agents now route cognition through SingleUseAgent
from src.single_use_agent import SingleUseAgent
from src.agent_messaging import AgentMessage

class ResearchAgent:
    def __init__(self, agent_id: str, initial_mode: str = 'greeting'):
        self.agent_id = agent_id
        self._single_use_agent = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        result = self._single_use_agent.process_turn(message.payload.get('user_message', ''))
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            intent='response',
            payload={'result': result},
            metadata={}
        )



class CodeAgent:
    def __init__(self, agent_id: str, initial_mode: str = 'greeting'):
        self.agent_id = agent_id
        self._single_use_agent = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        result = self._single_use_agent.process_turn(message.payload.get('user_message', ''))
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            intent='response',
            payload={'result': result},
            metadata={}
        )



class WriterAgent:
    def __init__(self, agent_id: str, initial_mode: str = 'greeting'):
        self.agent_id = agent_id
        self._single_use_agent = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        result = self._single_use_agent.process_turn(message.payload.get('user_message', ''))
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            intent='response',
            payload={'result': result},
            metadata={}
        )



class GeneralistAgent:
    def __init__(self, agent_id: str, initial_mode: str = 'greeting'):
        self.agent_id = agent_id
        self._single_use_agent = SingleUseAgent(agent_id, initial_mode=initial_mode)

    def handle_message(self, message: AgentMessage) -> AgentMessage:
        result = self._single_use_agent.process_turn(message.payload.get('user_message', ''))
        return AgentMessage(
            sender=self.agent_id,
            receiver=message.sender,
            intent='response',
            payload={'result': result},
            metadata={}
        )
