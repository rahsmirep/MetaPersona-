"""
Task Router for intelligent task distribution across multiple agents.
Routes tasks to the most suitable agent based on capabilities and confidence scores.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json

from .agent_base import BaseAgent, TaskResult
from .agent_registry import AgentRegistry
from .llm_provider import LLMProvider


class RoutingDecision(BaseModel):
    """Information about a routing decision."""
    task: str
    selected_agent_id: str
    confidence: float
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TaskRouter:
    """
    Intelligent task router that selects the best agent for each task.
    
    Features:
    - Automatic agent selection based on capabilities
    - Fallback handling for unroutable tasks
    - Routing history and analytics
    - Support for manual agent selection
    """
    
    def __init__(
        self,
        registry: AgentRegistry,
        default_agent_id: Optional[str] = None,
        min_confidence: float = 0.5,
        llm_provider: Optional[LLMProvider] = None,
        use_llm_routing: bool = True
    ):
        """
        Initialize the task router.
        
        Args:
            registry: Agent registry to route from
            default_agent_id: Optional default agent for fallback
            min_confidence: Minimum confidence threshold for routing
            llm_provider: Optional LLM provider for intelligent routing
            use_llm_routing: Whether to use LLM-based routing analysis
        """
        self.registry = registry
        self.default_agent_id = default_agent_id
        self.min_confidence = min_confidence
        self.llm_provider = llm_provider
        self.use_llm_routing = use_llm_routing and llm_provider is not None
        self.routing_history: List[RoutingDecision] = []
    
    def route_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        preferred_role: Optional[str] = None,
        agent_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[BaseAgent]:
        """
        Route a task to the most suitable agent.
        
        Args:
            task: Task description
            context: Optional task context
            preferred_role: Optional preferred agent role
            agent_id: Optional specific agent ID to use
            
        Returns:
            Selected agent or None if no suitable agent found
        """
        # Direct agent selection
        if agent_id:
            agent = self.registry.get(agent_id)
            if agent:
                self._record_routing(task, agent, 1.0, [])
                return agent
            print(f"Warning: Agent {agent_id} not found")
        
        # Filter by role if specified
        candidates = self.registry.list_all()
        if preferred_role:
            candidates = self.registry.get_by_role(preferred_role)
            if not candidates:
                print(f"Warning: No agents found with role '{preferred_role}'")
                candidates = self.registry.list_all()
        
        # Merge conversation history into context if provided
        context_with_history = dict(context) if context else {}
        if conversation_history:
            context_with_history["conversation_history"] = conversation_history

        # Get confidence scores
        scored_agents = []
        for agent in candidates:
            confidence = agent.can_handle_task(task, context_with_history)
            if confidence >= self.min_confidence:
                scored_agents.append((agent, confidence))
        
        # Use LLM-based routing if enabled and we have multiple candidates
        if self.use_llm_routing and len(scored_agents) > 1:
            scored_agents = self._enhance_routing_with_llm(task, scored_agents, context_with_history)
        
        if not scored_agents:
            # Try default agent
            if self.default_agent_id:
                default_agent = self.registry.get(self.default_agent_id)
                if default_agent:
                    print(f"No suitable agent found. Using default: {self.default_agent_id}")
                    self._record_routing(task, default_agent, 0.0, [])
                    return default_agent
            
            print(f"No agent available to handle task: {task[:50]}...")
            return None
        
        # Sort by confidence (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        # Select best agent
        best_agent, best_confidence = scored_agents[0]
        
        # Record alternatives
        alternatives = [
            {
                "agent_id": agent.agent_id,
                "role": agent.role,
                "confidence": confidence
            }
            for agent, confidence in scored_agents[1:6]  # Top 5 alternatives
        ]
        
        self._record_routing(task, best_agent, best_confidence, alternatives)
        return best_agent
    
    def execute_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        preferred_role: Optional[str] = None,
        agent_id: Optional[str] = None,
        use_skills: bool = True,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> TaskResult:
        """
        Route and execute a task.
        
        Args:
            task: Task to execute
            context: Optional task context
            preferred_role: Optional preferred agent role
            agent_id: Optional specific agent ID
            use_skills: Whether agent should use skills
            
        Returns:
            TaskResult from the selected agent
        """
        agent = self.route_task(task, context, preferred_role, agent_id, conversation_history)
        
        if not agent:
            return TaskResult(
                success=False,
                result=None,
                error="No suitable agent found for task"
            )
        
        try:
            # Pass conversation_history in context for agent continuity
            context_with_history = dict(context) if context else {}
            if conversation_history:
                context_with_history["conversation_history"] = conversation_history
            result = agent.handle_task(task, context_with_history, use_skills)
            return result
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=f"Agent execution failed: {str(e)}"
            )
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """
        Get statistics about routing decisions.
        
        Returns:
            Dictionary with routing analytics
        """
        if not self.routing_history:
            return {
                "total_routes": 0,
                "agent_usage": {},
                "average_confidence": 0.0,
                "most_used_agent": None
            }
        
        agent_usage = {}
        total_confidence = 0.0
        
        for decision in self.routing_history:
            agent_id = decision.selected_agent_id
            agent_usage[agent_id] = agent_usage.get(agent_id, 0) + 1
            total_confidence += decision.confidence
        
        return {
            "total_routes": len(self.routing_history),
            "agent_usage": agent_usage,
            "average_confidence": total_confidence / len(self.routing_history),
            "most_used_agent": max(agent_usage, key=agent_usage.get) if agent_usage else None
        }
    
    def get_recent_routes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent routing decisions.
        
        Args:
            limit: Maximum number of routes to return
            
        Returns:
            List of recent routing decisions
        """
        recent = self.routing_history[-limit:]
        return [decision.model_dump() for decision in recent]
    
    def explain_routing(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Explain routing decision without actually routing.
        Useful for debugging and transparency.
        
        Args:
            task: Task to analyze
            context: Optional task context
            
        Returns:
            Detailed explanation of routing decision
        """
        candidates = self.registry.list_all()
        
        if not candidates:
            return {
                "task": task,
                "decision": "No agents available",
                "candidates": []
            }
        
        scored_agents = []
        for agent in candidates:
            confidence = agent.can_handle_task(task, context)
            scored_agents.append({
                "agent_id": agent.agent_id,
                "role": agent.role,
                "description": agent.description,
                "confidence": confidence,
                "meets_threshold": confidence >= self.min_confidence,
                "capabilities": [cap.model_dump() for cap in agent.capabilities]
            })
        
        # Sort by confidence
        scored_agents.sort(key=lambda x: x["confidence"], reverse=True)
        
        best = scored_agents[0] if scored_agents else None
        
        return {
            "task": task,
            "min_confidence": self.min_confidence,
            "recommended_agent": best["agent_id"] if best and best["meets_threshold"] else None,
            "recommended_confidence": best["confidence"] if best else 0.0,
            "all_candidates": scored_agents
        }
    
    def _enhance_routing_with_llm(
        self,
        task: str,
        scored_agents: List[tuple],
        context: Optional[Dict[str, Any]] = None
    ) -> List[tuple]:
        """
        Use LLM to analyze task intent and refine agent selection.
        
        Args:
            task: Task description
            scored_agents: List of (agent, confidence) tuples
            context: Optional task context
            
        Returns:
            Refined list of (agent, confidence) tuples
        """
        # Build agent descriptions for LLM
        agent_descriptions = []
        for agent, confidence in scored_agents:
            agent_descriptions.append({
                "id": agent.agent_id,
                "role": agent.role,
                "description": agent.description,
                "initial_confidence": confidence
            })
        
        # Create LLM prompt for routing analysis
        prompt = f"""Analyze this task and determine which agent is most suitable:

Task: {task}

Available agents:
{json.dumps(agent_descriptions, indent=2)}

Consider:
1. The actual intent behind the task (not just keywords)
2. What type of output the user expects
3. Whether the task is asking to DO something vs just mentioning it
4. Context clues about the complexity and nature of the work

Respond with JSON in this format:
{{
    "analysis": "Brief explanation of task intent",
    "recommended_agent_id": "agent_id",
    "confidence_adjustment": 0.1 (adjustment to add/subtract from initial confidence, between -0.3 and +0.3),
    "reasoning": "Why this agent is best suited"
}}"""

        try:
            messages = [
                {"role": "system", "content": "You are a task routing expert. Analyze tasks and recommend the best agent."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.llm_provider.generate(messages)
            
            # Try to extract JSON from response
            response_text = response.strip()
            
            # Handle markdown code blocks
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            analysis = json.loads(response_text)
            
            # Apply confidence adjustment
            recommended_id = analysis.get("recommended_agent_id")
            adjustment = float(analysis.get("confidence_adjustment", 0.0))
            adjustment = max(-0.3, min(0.3, adjustment))  # Clamp to [-0.3, 0.3]
            
            # Adjust confidences
            adjusted_agents = []
            for agent, confidence in scored_agents:
                if agent.agent_id == recommended_id:
                    new_confidence = min(1.0, confidence + adjustment)
                else:
                    new_confidence = max(0.0, confidence - abs(adjustment) * 0.5)
                adjusted_agents.append((agent, new_confidence))
            
            return adjusted_agents
            
        except Exception as e:
            print(f"LLM routing enhancement failed: {e}")
            return scored_agents  # Fallback to original scores
    
    def _record_routing(
        self,
        task: str,
        agent: BaseAgent,
        confidence: float,
        alternatives: List[Dict[str, Any]]
    ):
        """Record a routing decision."""
        decision = RoutingDecision(
            task=task[:200],  # Truncate long tasks
            selected_agent_id=agent.agent_id,
            confidence=confidence,
            alternatives=alternatives
        )
        self.routing_history.append(decision)
        
        # Keep history manageable (last 1000 routes)
        if len(self.routing_history) > 1000:
            self.routing_history = self.routing_history[-1000:]
    
    def __str__(self) -> str:
        return f"TaskRouter(agents={len(self.registry)}, routes={len(self.routing_history)})"
