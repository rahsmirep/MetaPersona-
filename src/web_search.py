"""
Web Search Tool for MetaPersona
Allows AI agents to search the web for real-time information and cite sources.
"""

import os
import json
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()


class WebSearchTool:
    """Web search capability for AI agents."""
    
    def __init__(self):
        # Check if Google API credentials exist, otherwise use SearXNG
        has_google = os.getenv("GOOGLE_API_KEY") and os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        default_provider = "google" if has_google else "searxng"
        self.search_provider = os.getenv("SEARCH_PROVIDER", default_provider)
        
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, url, snippet
        """
        console.print(f"[cyan]🔍 Searching web for: {query}[/cyan]")
        
        try:
            if self.search_provider == "searxng":
                return self._search_searxng(query, num_results)
            elif self.search_provider == "duckduckgo":
                return self._search_duckduckgo(query, num_results)
            elif self.search_provider == "google":
                return self._search_google(query, num_results)
            else:
                return self._search_searxng(query, num_results)
        except Exception as e:
            console.print(f"[red]Search error: {str(e)}[/red]")
            return []
    
    def _search_searxng(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using multiple SearXNG instances with fast failover."""
        import requests
        
        # Try multiple public SearXNG instances (fastest first)
        instances = [
            "https://search.bus-hit.me",
            "https://searx.be",
            "https://search.mdosch.de"
        ]
        
        for instance_url in instances:
            try:
                url = f"{instance_url}/search"
                params = {
                    'q': query,
                    'format': 'json',
                    'categories': 'general'
                }
                
                response = requests.get(url, params=params, timeout=3)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get('results', [])[:num_results]:
                    results.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'snippet': item.get('content', '')
                    })
                
                if results:
                    console.print(f"[green]✓ Found {len(results)} results[/green]")
                    return results
                    
            except Exception as e:
                continue  # Try next instance
        
        # All instances failed, try DuckDuckGo as last resort
        console.print(f"[yellow]SearXNG instances unavailable, trying DuckDuckGo...[/yellow]")
        return self._search_duckduckgo(query, num_results)
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (free, no API key needed)."""
        try:
            from duckduckgo_search import DDGS
            
            results = []
            with DDGS(timeout=10) as ddgs:  # 10 second timeout
                search_results = list(ddgs.text(query, max_results=num_results))
                
                for result in search_results:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')
                    })
            
            console.print(f"[green]✓ Found {len(results)} results[/green]")
            return results
            
        except ImportError:
            console.print("[yellow]⚠ duckduckgo-search not installed. Run: pip install duckduckgo-search[/yellow]")
            return []
        except Exception as e:
            console.print(f"[red]DuckDuckGo search error: {str(e)}[/red]")
            return []
    
    def _search_google(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search using Google Custom Search API (100 free queries/day)."""
        try:
            import requests
            
            api_key = os.getenv("GOOGLE_API_KEY")
            search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            
            if not api_key or not search_engine_id:
                console.print("[yellow]⚠ Google API credentials not found. Using SearXNG instead.[/yellow]")
                return self._search_searxng(query, num_results)
            
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': min(num_results, 10)  # Google allows max 10 per request
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            console.print(f"[green]✓ Found {len(results)} results from Google[/green]")
            return results
            
        except Exception as e:
            console.print(f"[yellow]Google search error: {str(e)}, trying SearXNG...[/yellow]")
            return self._search_searxng(query, num_results)
    
    def format_results_for_llm(self, results: List[Dict[str, Any]]) -> str:
        """Format search results for LLM consumption."""
        if not results:
            return "No search results found."
        
        formatted = "Search Results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   URL: {result['url']}\n"
            formatted += f"   {result['snippet']}\n\n"
        
        return formatted


def search_web(query: str, num_results: int = 5) -> List[Dict[str, Any]]:
    """
    Convenience function to search the web.
    
    Args:
        query: Search query
        num_results: Number of results to return
        
    Returns:
        List of search results
    """
    tool = WebSearchTool()
    return tool.search(query, num_results)
