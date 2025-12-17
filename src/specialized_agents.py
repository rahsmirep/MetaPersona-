"""
Specialized agent implementations for common roles.
These serve as examples of how to build agents using the BaseAgent class.
"""
from typing import Dict, List, Any, Optional
import re

from .agent_base import BaseAgent, AgentCapability, TaskResult
from .llm_provider import LLMProvider
from .skills.manager import SkillManager


class ResearchAgent(BaseAgent):
    """
    Agent specialized in research, information gathering, and analysis.
    """
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="web_research",
                description="Search and analyze information from the web",
                confidence=0.9,
                examples=["search for", "find information about", "research", "look up"]
            ),
            AgentCapability(
                name="data_analysis",
                description="Analyze and summarize data or information",
                confidence=0.85,
                examples=["analyze", "summarize", "explain", "compare"]
            ),
            AgentCapability(
                name="fact_checking",
                description="Verify facts and provide evidence",
                confidence=0.8,
                examples=["verify", "check if", "is it true", "fact check"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this is a research task."""
        task_lower = task.lower()
        
        # Exclude if it's clearly writing or coding
        if "write code" in task_lower or "write a function" in task_lower:
            return 0.2
        if "write email" in task_lower or "write letter" in task_lower or "draft" in task_lower:
            return 0.2
        
        # Very high confidence - explicit research requests
        very_high_keywords = ["research", "search for", "find information", "look up", 
                             "investigate", "explore", "gather information"]
        if any(keyword in task_lower for keyword in very_high_keywords):
            return 0.9
        
        # High confidence - analysis and information tasks
        high_keywords = ["analyze", "compare", "what is", "tell me about", "explain",
                        "summarize", "how does", "why does", "learn about"]
        if any(keyword in task_lower for keyword in high_keywords):
            return 0.75
        
        # Medium - information seeking
        medium_keywords = ["information", "data", "facts", "details", "history of",
                          "definition", "meaning of"]
        if any(keyword in task_lower for keyword in medium_keywords):
            return 0.6
        
        return 0.2
    
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute research task."""
        try:
            # Check if web_search skill is available
            web_search_available = use_skills and "web_search" in self.skills_manager.registry.list_skills()
            
            # Build prompt
            system_prompt = self.get_system_prompt()
            if web_search_available:
                system_prompt += "\n\nYou have access to web search. Use it when needed."
            
            # Get LLM response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
            response = self.llm_provider.generate(messages)
            
            # Record interaction
            self.update_memory({
                "task": task,
                "response": response[:200],
                "skills_used": ["web_search"] if web_search_available else []
            })
            
            return TaskResult(
                success=True,
                result=response,
                metadata={
                    "agent_id": self.agent_id,
                    "role": self.role,
                    "skills_used": web_search_available
                }
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=str(e)
            )


class CodeAgent(BaseAgent):
    """
    Agent specialized in coding, debugging, and technical tasks.
    """
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="code_writing",
                description="Write code in various programming languages",
                confidence=0.95,
                examples=["write code", "implement", "create function", "build"]
            ),
            AgentCapability(
                name="code_review",
                description="Review and improve existing code",
                confidence=0.9,
                examples=["review", "debug", "fix", "optimize", "refactor"]
            ),
            AgentCapability(
                name="technical_explanation",
                description="Explain technical concepts and code",
                confidence=0.85,
                examples=["explain how", "what does this code", "how does"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this is a coding task."""
        task_lower = task.lower()
        
        # Exclude non-coding writing tasks
        writing_indicators = ["email", "letter", "article", "blog", "essay", "report", 
                             "story", "document", "memo", "note", "message", "paragraph",
                             "write about", "write to", "write for", "draft a", "compose a"]
        if any(indicator in task_lower for indicator in writing_indicators):
            return 0.15  # Very low confidence for writing tasks
        
        # Very high confidence - explicit code writing
        very_high_code = ["write code", "write a function", "write a program", "write a script",
                         "create a function", "build a program", "implement code"]
        if any(phrase in task_lower for phrase in very_high_code):
            return 0.95
        
        # High confidence - programming languages mentioned
        languages = ["python", "javascript", "java", "c++", "rust", "go", "typescript", 
                    "c#", "php", "ruby", "swift", "kotlin", "html", "css", "sql"]
        if any(lang in task_lower for lang in languages):
            return 0.9
        
        # High confidence - clear coding keywords
        code_keywords = ["code", "function", "class", "method", "algorithm", "script",
                        "debug", "fix bug", "implement", "refactor", "optimize",
                        "api", "database", "variable", "loop", "array", "object"]
        if any(keyword in task_lower for keyword in code_keywords):
            return 0.85
        
        # Medium - programming actions with context
        programming_contexts = ["program", "app", "application", "software", "system", "tool"]
        if ("write" in task_lower or "create" in task_lower or "build" in task_lower) and \
           any(ctx in task_lower for ctx in programming_contexts):
            return 0.75
        
        return 0.3
    
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute coding task."""
        try:
            # Build prompt
            system_prompt = self.get_system_prompt()
            system_prompt += "\n\nProvide clean, well-documented code. Include explanations and best practices."
            
            # Check for file operations
            file_ops_available = use_skills and "file_operations" in self.skills_manager.registry.list_skills()
            if file_ops_available:
                system_prompt += "\n\nYou can read/write files if needed."
            
            # Get LLM response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
            response = self.llm_provider.generate(messages)
            
            # Record interaction
            self.update_memory({
                "task": task,
                "response": response[:200],
                "skills_used": ["file_operations"] if file_ops_available else []
            })
            
            return TaskResult(
                success=True,
                result=response,
                metadata={
                    "agent_id": self.agent_id,
                    "role": self.role
                }
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=str(e)
            )


class WriterAgent(BaseAgent):
    """
    Agent specialized in writing, content creation, and communication.
    """
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="creative_writing",
                description="Write creative content, stories, and narratives",
                confidence=0.9,
                examples=["write a story", "create content", "draft"]
            ),
            AgentCapability(
                name="professional_writing",
                description="Write professional documents, emails, reports",
                confidence=0.9,
                examples=["write email", "draft report", "compose", "write letter"]
            ),
            AgentCapability(
                name="editing",
                description="Edit and improve written content",
                confidence=0.85,
                examples=["edit", "improve", "rewrite", "polish"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Determine if this is a writing task."""
        task_lower = task.lower()
        
        # Exclude coding tasks - if it mentions code/programming, not a writing task
        code_indicators = ["code", "function", "class", "method", "program", "script", 
                          "python", "javascript", "java ", "algorithm", "debug", "implement",
                          "write code", "write a function", "write a program", "write a script"]
        if any(indicator in task_lower for indicator in code_indicators):
            return 0.2  # Very low confidence for coding tasks
        
        # Very high confidence - explicit writing documents
        very_high_keywords = ["email", "letter", "memo", "note", "message", "correspondence"]
        if any(keyword in task_lower for keyword in very_high_keywords):
            return 0.95
        
        # High confidence - content creation
        high_keywords = ["article", "blog", "post", "essay", "report", "story", 
                        "content", "document", "paper", "summary", "description",
                        "paragraph", "text", "copy", "announcement"]
        if any(keyword in task_lower for keyword in high_keywords):
            return 0.9
        
        # Medium-high - writing action words with context
        writing_actions = ["draft", "compose", "write about", "write a letter", 
                          "write an email", "write an article", "write something",
                          "help me write", "write to", "write for"]
        if any(action in task_lower for action in writing_actions):
            return 0.85
        
        # Medium - editing and improving text
        editing_keywords = ["edit", "improve", "rewrite", "polish", "proofread", 
                           "revise", "rephrase", "reword", "fix grammar", "make better"]
        if any(keyword in task_lower for keyword in editing_keywords):
            return 0.8
        
        # Low-medium - generic "write" without clear code context
        if "write" in task_lower and "code" not in task_lower:
            return 0.6
        
        return 0.3
    
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute writing task."""
        try:
            # Build prompt
            system_prompt = self.get_system_prompt()
            system_prompt += "\n\nWrite clearly, engagingly, and appropriately for the context."
            
            # Get LLM response
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
            response = self.llm_provider.generate(messages)
            
            # Record interaction
            self.update_memory({
                "task": task,
                "response": response[:200]
            })
            
            return TaskResult(
                success=True,
                result=response,
                metadata={
                    "agent_id": self.agent_id,
                    "role": self.role
                }
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=str(e)
            )


class GeneralistAgent(BaseAgent):
    """
    Agent that can handle general tasks that don't fit specific specializations.
    Serves as a fallback for unmatched tasks.
    """
    
    def _define_capabilities(self) -> List[AgentCapability]:
        return [
            AgentCapability(
                name="general_assistance",
                description="Handle general questions and tasks",
                confidence=0.6,
                examples=["help with", "assist", "answer", "explain"]
            ),
            AgentCapability(
                name="conversation",
                description="Engage in natural conversation",
                confidence=0.7,
                examples=["chat", "talk", "discuss", "tell me"]
            )
        ]
    
    def can_handle_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Generalist can handle anything with low confidence as fallback."""
        task_lower = task.lower()
        
        # If it's clearly a specialized task, return very low confidence
        specialized_keywords = ["code", "function", "research", "search", "email", 
                               "letter", "article", "python", "write code", "find information"]
        if any(keyword in task_lower for keyword in specialized_keywords):
            return 0.3  # Let specialized agents handle it
        
        # For truly general questions/tasks, return moderate confidence
        return 0.5
    
    def handle_task(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        use_skills: bool = True
    ) -> TaskResult:
        """Execute general task."""
        try:
            system_prompt = self.get_system_prompt()
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task}
            ]
            response = self.llm_provider.generate(messages)
            
            self.update_memory({
                "task": task,
                "response": response[:200]
            })
            
            return TaskResult(
                success=True,
                result=response,
                metadata={
                    "agent_id": self.agent_id,
                    "role": self.role
                }
            )
            
        except Exception as e:
            return TaskResult(
                success=False,
                result=None,
                error=str(e)
            )
