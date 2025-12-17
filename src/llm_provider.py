"""
MetaPersona - LLM Provider Interface
Supports multiple LLM backends (OpenAI, Anthropic, Ollama).
"""
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider."""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.api_key = os.getenv("OPENAI_API_KEY")
        
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate response using OpenAI API."""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "your_openai_key_here")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider."""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate response using Anthropic API."""
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            
            # Convert messages format
            system_msg = None
            converted_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_msg = msg["content"]
                else:
                    converted_messages.append(msg)
            
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_msg,
                messages=converted_messages,
                temperature=temperature
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key != "your_anthropic_key_here")


class OllamaProvider(LLMProvider):
    """Local Ollama provider."""
    
    def __init__(self, model: str = None):
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Generate response using Ollama."""
        try:
            import requests # type: ignore
            
            # Convert messages to Ollama format
            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if role == "system":
                    prompt += f"System: {content}\n\n"
                elif role == "user":
                    prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    prompt += f"Assistant: {content}\n\n"
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise Exception(f"Ollama error: {str(e)}")
    
    def is_available(self) -> bool:
        try:
            import requests # type: ignore
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Ollama availability check failed: {e}")
            return False


def get_llm_provider(provider_name: str = None) -> LLMProvider:
    """Get configured LLM provider."""
    provider_name = provider_name or os.getenv("LLM_PROVIDER", "openai")
    
    providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider
    }
    
    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}")
    
    provider = providers[provider_name]()
    
    if not provider.is_available():
        raise Exception(f"Provider {provider_name} is not properly configured or available")
    
    return provider
