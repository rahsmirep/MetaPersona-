"""
Web Search Skill
Search the web for information.
"""
import json
from typing import Optional, Dict, Any, List
from ..base import Skill, SkillMetadata, SkillParameter, SkillResult

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class WebSearchSkill(Skill):
    """Web search skill using DuckDuckGo Instant Answer API."""
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="web_search",
            description="Search the web for information using DuckDuckGo",
            category="Information",
            parameters=[
                SkillParameter(
                    name="query",
                    type="str",
                    description="Search query",
                    required=True
                ),
                SkillParameter(
                    name="max_results",
                    type="int",
                    description="Maximum number of results to return",
                    required=False,
                    default=3
                )
            ],
            returns="Search results with snippets and URLs"
        )
    
    def execute(self, query: str, max_results: int = 3) -> SkillResult:
        """Search the web."""
        if not REQUESTS_AVAILABLE:
            return SkillResult(
                success=False,
                error="requests library not available. Install with: pip install requests"
            )
        
        try:
            # Use DuckDuckGo Instant Answer API (no key required)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": 1,
                "skip_disambig": 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse results
            results: List[Dict[str, Any]] = []
            
            # Abstract (main answer)
            if data.get("Abstract"):
                results.append({
                    "title": data.get("Heading", ""),
                    "snippet": data.get("Abstract", ""),
                    "url": data.get("AbstractURL", "")
                })
            
            # Related topics
            for topic in data.get("RelatedTopics", [])[:max_results]:
                if isinstance(topic, dict) and "Text" in topic:
                    results.append({
                        "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                        "snippet": topic.get("Text", ""),
                        "url": topic.get("FirstURL", "")
                    })
            
            if not results:
                return SkillResult(
                    success=True,
                    data=[],
                    metadata={"query": query, "message": "No results found"}
                )
            
            return SkillResult(
                success=True,
                data=results[:max_results],
                metadata={"query": query, "count": len(results)}
            )
        
        except requests.RequestException as e:
            return SkillResult(
                success=False,
                error=f"Web search failed: {str(e)}"
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )
