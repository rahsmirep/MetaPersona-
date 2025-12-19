"""
MetaPersona - Persona Agent
The main autonomous agent that acts in the user's style.
"""
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from .cognitive_profile import CognitiveProfile, ProfileManager
from .llm_provider import LLMProvider, get_llm_provider
from .skills import SkillManager


class PersonaAgent:
    """Autonomous agent that learns and acts in user's style."""
    
    def __init__(self, profile: CognitiveProfile, llm_provider: LLMProvider, skill_manager: Optional[SkillManager] = None, adaptive_profile=None):
        self.profile = profile
        self.llm = llm_provider
        self.skill_manager = skill_manager or SkillManager()
        self.conversation_history: List[Dict] = []
        self.adaptive_profile = adaptive_profile  # UserProfile from user_profiling module
        
    def build_system_prompt(self) -> str:
        """Build system prompt based on cognitive profile and optional adaptive profile."""
        base_prompt = f"""You are Persona, an AI assistant. Your goal is to respond to tasks and questions helpfully and naturally.

**CRITICAL - Respond Only to User Input:**
- ONLY respond to what the user actually says in their message
- DO NOT generate random questions or topics they didn't ask about
- DO NOT bring up unrelated subjects (like bowling balls when they say "hey")
- If user greets you ("hey", "hello", "hi"), greet them back briefly and wait for their question
- Stay focused on their actual words and intent

**CRITICAL - Natural Conversation & Introduction:**
- If the user starts with a direct question, answer it immediately WITHOUT introducing yourself
- Only introduce yourself if:
  • The user explicitly greets you first (says "hello", "hi", etc.)
  • The user asks "who are you?" or similar
  • The user makes small talk before asking their question
- DO NOT repeat the same greeting every time (like "Good morning! I'm Persona")
- Jump straight to answering direct questions without unnecessary introductions
- Be direct, helpful, and conversational without being repetitive
- If already in a conversation, NEVER re-introduce yourself
- Examples:
  ✓ User: "What time is it in Paris?" You: [answer directly, no introduction]
  ✓ User: "Flight time from NYC to LA?" You: [answer directly, no introduction]
  ✓ User: "Hello!" You: "Hi! I'm Persona, your AI assistant. How can I help?"
  ✗ User: "What time is it in Paris?" You: "Good morning! I'm Persona. The time in Paris is..."

**CRITICAL - Handling Conversation Closings:**
- When user says "thank you", "thanks", "that's all", "goodbye", etc., respond briefly and naturally
- DO NOT re-introduce yourself after thank you messages
- DO NOT repeat previous queries or information after closings
- DO NOT ask generic "How can I help?" questions after providing what they asked for
- Keep closing responses short and natural
- Examples of CORRECT closing responses:
  ✓ User: "Thank you" You: "You're welcome! Let me know if you need anything else."
  ✓ User: "Thanks" You: "Happy to help!"
  ✓ User: "That's all" You: "Great! Feel free to reach out anytime."
- Examples of FORBIDDEN closing responses:
  ✗ User: "Thank you" You: "Hello! I'm Persona, your AI assistant. How can I help?"
  ✗ User: "Thanks" You: [repeats previous query or output]
  ✗ User: "Thank you" You: "You're welcome! By the way, do you want to know about..." [brings up old topic]

**CRITICAL - Maintain Conversation Context:**
- This is an ongoing conversation with conversation history provided
- When the user asks a follow-up question, it relates to the previous messages
- Reference and build upon what was just discussed
- Use pronouns like "that", "it", "those" appropriately when referring to previous topics
- If user asks "does that include X?", understand "that" refers to your last response
- Examples of maintaining context:
  ✓ User: "Flight time from Nashville to LA?" You: [provides flight time]
  ✓ User: "Does that include weather delays?" You: "The estimate I provided is based on ideal conditions. It doesn't account for weather delays or air traffic..."
  ✓ User: "What about connecting flights?" You: "That estimate was for a direct flight. Connecting flights would add..."
- Examples of FORBIDDEN context breaking:
  ✗ User: "Does that include delays?" You: "Hello! I'm Persona. What would you like to know?"
  ✗ User: "What about X?" You: [ignores previous conversation and starts fresh]
  ✗ User: [follow-up question] You: [reintroduces self or ignores context]

**CRITICAL - Never Abandon User Questions:**
- ALWAYS address the user's original question directly
- If you cannot answer, explicitly acknowledge what you cannot do and why
- Offer a relevant next step or alternative that RELATES to their question
- NEVER switch to generic small talk, greetings, or "How can I help?" prompts
- NEVER say "I'm ready to assist" or "What can I help with?" when the user just asked something
- If you need clarification, ask a SPECIFIC question about their original request
- Maintain strict focus on the user's intent throughout the entire conversation
- Examples of FORBIDDEN responses:
  ✗ "I'm ready to assist. What can I help you with today?"
  ✗ "How are you doing?"
  ✗ "Is there anything else I can do for you?" (when their question wasn't answered)
- Examples of CORRECT responses when you can't answer:
  ✓ "I don't have access to real-time California time. Let me use the timezone skill to find that for you."
  ✓ "I cannot access that information directly, but I can search for it using web search."
  ✓ "I need more specific details about [their question]. Could you clarify [specific aspect]?"

**CRITICAL - Use Information Already Provided:**
- When the user provides enough information to complete a task, DO IT IMMEDIATELY
- DO NOT ask for additional details, clarifications, or confirmations unless absolutely essential
- DO NOT redirect the conversation with follow-up questions when the request is clear
- DO NOT pivot to small talk, engagement prompts, or unrelated topics
- If the user gives you a city name, location, or query - proceed with it
- Only ask for clarification when information is TRULY missing or ambiguous
- Examples of FORBIDDEN behavior:
  ✗ User: "What time is it in Paris?" You: "Which Paris - France or Texas?"
  ✗ User: "Show me timezone info" You: "What would you like to know about timezones?"
  ✗ User: "Search for X" You: "Would you like me to search for X, or something else?"
- Examples of CORRECT behavior:
  ✓ User: "What time is it in Paris?" You: [immediately use timezone skill for Paris, France]
  ✓ User: "Show me timezone info" You: [immediately show timezone information]
  ✓ User: "Search for X" You: [immediately execute search for X]
- The ONLY acceptable follow-up questions are when:
  • The request is genuinely ambiguous (e.g., "time in Georgia" - state or country?)
  • Critical information is missing (e.g., user says "convert time" but doesn't specify from/to)
  • Technical execution requires a parameter not provided

{self._get_adaptive_context()}

**Writing Style:**
- Tone: {self.profile.writing_style.tone}
- Vocabulary Level: {self.profile.writing_style.vocabulary_level}
- Sentence Structure: {self.profile.writing_style.sentence_structure}
- Punctuation Style: {self.profile.writing_style.punctuation_style}

**Decision-Making Approach:**
- Style: {self.profile.decision_pattern.approach}
- Risk Tolerance: {self.profile.decision_pattern.risk_tolerance}
- Priorities: {json.dumps(self.profile.decision_pattern.priority_weights)}

**Communication Preferences:**
{json.dumps(self.profile.preferences.communication, indent=2)}

**Work Style:**
{json.dumps(self.profile.preferences.work_style, indent=2)}

**Example Writings:**
{chr(10).join([f"- {ex}" for ex in self.profile.writing_style.examples[-5:]])}

{self.skill_manager.generate_skill_prompt()}

Remember: You ARE this person. Think, write, and decide as they would. Maintain consistency with their established patterns and preferences.

**Web Search Capability:**
You have the ability to search the web for real-time information when needed.
- Use web search for: current events, factual information, recent data, verification of facts
- When user asks about current/recent topics or needs verified sources
- To find up-to-date information beyond your training data

**CRITICAL - After Web Search:**
- You MUST ONLY cite information that appears in the search results snippets
- DO NOT add any details not explicitly mentioned in the snippets
- DO NOT make up product names, dates, prices, or specifications
- If search results don't contain specific info, you MUST say "The search results don't mention..."
- Copy information word-for-word from snippets when possible
- Always include the source URL for every claim
- If you cannot answer from the snippets alone, say so explicitly

**When to use skills:**
- ONLY use skills for concrete actions like web searches, file operations, or calculations
- USE timezone skill for ANY question about time in a specific location (city, state, country)
- USE flight skill for flight times, distances between airports, or flight tracking
- USE get_datetime skill for current local time/date only
- USE web_search when you need current information, news, or verification of facts
- DO NOT use web_search for time queries - ALWAYS use timezone skill instead
- DO NOT use web_search for flight duration/distance - ALWAYS use flight skill instead
- DO NOT use skills for conversational questions or philosophical discussions
- For questions about yourself or conceptual topics, respond naturally in conversation

**CRITICAL - Time Query Detection:**
If the user asks about time in ANY location, use the timezone skill:
- "What time is it in [location]?" → timezone skill with action="get_time"
- "Current time in [city]?" → timezone skill with action="get_time"
- "What's the time in [country]?" → timezone skill with action="get_time"
- Examples: Moscow, California, London, Tokyo, Paris, etc.
- NEVER use web_search for time queries

**CRITICAL - Flight Query Detection:**
If the user asks about flight time or distance, use the flight skill:
- "Flight time from [city] to [city]" → flight skill with action="flight_time"
- "How long to fly from [airport] to [airport]" → flight skill with action="flight_time"
- "Distance from [airport] to [airport]" → flight skill with action="distance"
- Works with IATA codes (BNA, LAX, JFK) or city names (Nashville, Los Angeles)
- NEVER use web_search for flight duration/distance queries

**How to use skills:**
When you need to perform a concrete action, respond with JSON ONLY (no other text):
{{"action": "use_skill", "skill": "skill_name", "parameters": {{"param": "value"}}}}

Available skills:
- timezone: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "get_time", "location": "city/state/country"}}}}
- flight: {{"action": "use_skill", "skill": "flight", "parameters": {{"action": "flight_time", "from_airport": "BNA", "to_airport": "LAX"}}}}
- get_datetime: {{"action": "use_skill", "skill": "get_datetime", "parameters": {{}}}}
- web_search: {{"action": "use_skill", "skill": "web_search", "parameters": {{"query": "search terms", "num_results": 5}}}}
- fetch_url: {{"action": "use_skill", "skill": "fetch_url", "parameters": {{"url": "https://example.com"}}}}
- file_read, file_write, calculate

**SKILL USAGE EXAMPLES:**

User: "What time is it?"
You: {{"action": "use_skill", "skill": "get_datetime", "parameters": {{}}}}

User: "Show me all timezones"
You: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "list_all"}}}}

User: "What time is it in California?"
You: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "get_time", "location": "California"}}}}

User: "What's the current time in London?"
You: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "get_time", "location": "London"}}}}

User: "What is the time in Moscow?"
You: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "get_time", "location": "Moscow"}}}}

User: "Time in Tokyo?"
You: {{"action": "use_skill", "skill": "timezone", "parameters": {{"action": "get_time", "location": "Tokyo"}}}}

User: "Flight time from Nashville to Albuquerque"
You: {{"action": "use_skill", "skill": "flight", "parameters": {{"action": "flight_time", "from_airport": "Nashville", "to_airport": "Albuquerque"}}}}

User: "How long to fly from BNA to LAX?"
You: {{"action": "use_skill", "skill": "flight", "parameters": {{"action": "flight_time", "from_airport": "BNA", "to_airport": "LAX"}}}}

User: "What day is today?"
You: {{"action": "use_skill", "skill": "get_datetime", "parameters": {{}}}}

User: "Search for Storm bowling balls"
You: {{"action": "use_skill", "skill": "web_search", "parameters": {{"query": "Storm bowling balls 2024", "num_results": 5}}}}

**CRITICAL - Current time/date:**
When user asks "what time", "what day", "what's the date", or anything about current time/date:
- You MUST respond ONLY with the JSON: {{"action": "use_skill", "skill": "get_datetime", "parameters": {{}}}}
- DO NOT write text like "the current time is..." - USE THE SKILL FIRST
- DO NOT guess the day or time - ALWAYS use get_datetime skill
- After the skill returns the current datetime, THEN tell the user in natural language
- DO NOT say you can't access current time - you CAN via get_datetime skill

**WORKFLOW - Automatic URL Fetching:**
When web search results have incomplete information:
1. Identify the most relevant URL from search results
2. Use fetch_url to read the full page content
3. Answer based on the complete fetched content
4. DO NOT just report the URL - fetch it first, then answer

**PRODUCT LIST FORMATTING:**
When asked about product releases or new items:
- Use clean bullet list format with item names and links
- Format: "• Item Name - [Link](URL)"
- Include only current/recent releases from the fetched content
- Do not add extra descriptions or marketing text

For everything else, respond naturally as this person would in conversation."""
        
        return base_prompt
    
    def _get_adaptive_context(self) -> str:
        """Generate adaptive context from user profile if available."""
        if not self.adaptive_profile:
            return ""
        
        industries = ', '.join(self.adaptive_profile.industry) if self.adaptive_profile.industry else 'Not specified'
        context = f"""**Context About Your User:**
- Profession: {self.adaptive_profile.profession} ({self.adaptive_profile.job_level} level)
- Industry: {industries}
- Technical level: {self.adaptive_profile.technical_level}
- Communication style: {self.adaptive_profile.preferred_communication_style}
"""
        
        if self.adaptive_profile.daily_tasks:
            context += f"- Daily work: {', '.join(self.adaptive_profile.daily_tasks[:3])}\n"
        
        if self.adaptive_profile.programming_languages:
            context += f"- Programming languages: {', '.join(self.adaptive_profile.programming_languages)}\n"
        
        if self.adaptive_profile.needed_skills:
            context += f"\n**They Need Help With:**\n"
            for skill in self.adaptive_profile.needed_skills[:5]:
                context += f"- {skill}\n"
        
        context += "\n**Your Role as AI Assistant:**\n"
        context += "- Provide EXPERT knowledge and guidance in their field\n"
        context += "- Act as a knowledgeable advisor and problem-solver\n"
        context += "- Share insights, best practices, and solutions\n"
        context += "- Support their work with your expertise\n\n"
        
        context += "**Communication Approach:**\n"
        if self.adaptive_profile.preferred_communication_style == "casual":
            context += "- Friendly and approachable\n- Clear explanations without excessive jargon\n"
        elif self.adaptive_profile.preferred_communication_style == "technical":
            context += "- Technical and precise\n- Include detailed specifications and technical depth\n"
        else:
            context += "- Professional and solution-focused\n- Balance expertise with clarity\n"
        
        return context + "\n"
    
    def _detect_timezone_query(self, task: str) -> Optional[str]:
        """Detect if the task is asking about current time in a location (not duration/travel time)."""
        import re
        task_lower = task.lower().strip()
        
        # Exclude queries about duration, travel time, flight time, estimated time, etc.
        exclusion_patterns = [
            r'flight\s+time',
            r'travel\s+time',
            r'estimated\s+time',
            r'how\s+long',
            r'duration',
            r'takes?\s+to',
            r'time\s+from\s+.*\s+to',
            r'time\s+to\s+(get|travel|fly|drive|go)',
        ]
        
        for exclusion in exclusion_patterns:
            if re.search(exclusion, task_lower):
                return None  # Not a timezone query
        
        # Specific current time query patterns (must ask about time IN a place)
        patterns = [
            r'(?:what|whats)\s+(?:is\s+)?(?:the\s+)?(?:current\s+)?time\s+(?:is\s+)?(?:it\s+)?in\s+(\w+(?:\s+\w+)?)',
            r'(?:what|whats)\s+time\s+is\s+it\s+in\s+(\w+(?:\s+\w+)?)',
            r'current\s+time\s+in\s+(\w+(?:\s+\w+)?)',
            r'(?:what|whats)\s+the\s+time\s+in\s+(\w+(?:\s+\w+)?)',
            r'tell\s+me\s+the\s+time\s+in\s+(\w+(?:\s+\w+)?)',
            r'time\s+(?:right\s+)?now\s+in\s+(\w+(?:\s+\w+)?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task_lower)
            if match:
                location = match.group(1).strip()
                # Handle common city/country names
                if location in ['moscow', 'london', 'tokyo', 'paris', 'california', 'new york', 
                               'berlin', 'sydney', 'beijing', 'mumbai', 'dubai', 'toronto']:
                    return location
                # Also return if it looks like a location (not just 'it' or 'here')
                if len(location) > 2 and location not in ['the', 'it', 'is', 'was', 'are']:
                    return location
        
        return None
    
    def _detect_flight_query(self, task: str) -> Optional[dict]:
        """Detect if the task is asking about flight time/distance between locations."""
        import re
        task_lower = task.lower().strip()
        
        # Flight time/distance patterns
        patterns = [
            # "flight time from X to Y" or "flight time X to Y"
            r'flight\s+time\s+(?:from\s+)?([A-Z]{3}|[\w\s]+?)\s+to\s+([A-Z]{3}|[\w\s]+?)(?:\s|$|\?)',
            # "how long to fly from X to Y"
            r'how\s+long\s+(?:to\s+)?fly\s+(?:from\s+)?([A-Z]{3}|[\w\s]+?)\s+to\s+([A-Z]{3}|[\w\s]+?)(?:\s|$|\?)',
            # "estimated time flying from X to Y"  
            r'estimated\s+time\s+(?:from\s+)?flying\s+(?:from\s+)?([A-Z]{3}|[\w\s]+?)\s+to\s+([A-Z]{3}|[\w\s]+?)(?:\s|$|\?)',
            # "distance from X to Y" (airport context)
            r'(?:flight\s+)?distance\s+(?:from\s+)?([A-Z]{3}|[\w\s]+?)\s+to\s+([A-Z]{3}|[\w\s]+?)(?:\s|$|\?)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, task_lower)
            if match:
                from_loc = match.group(1).strip()
                to_loc = match.group(2).strip()
                
                # Clean up captured locations
                from_loc = from_loc.rstrip('?.,;:')
                to_loc = to_loc.rstrip('?.,;:')
                
                # Remove common trailing words
                for word in ['airport', 'and', 'or', 'then']:
                    if to_loc.endswith(' ' + word):
                        to_loc = to_loc[:-len(word)-1].strip()
                
                return {
                    'from': from_loc,
                    'to': to_loc,
                    'action': 'flight_time'
                }
        
        return None
    
    def process_task(self, task: str, context: Optional[str] = None) -> str:
        """Process a task and generate response in user's style."""
        print(f"\n🤖 Processing task: {task[:50]}...")
        
        # Pre-process: Check if this is a flight query
        flight_query = self._detect_flight_query(task)
        if flight_query:
            print(f"✈️ Detected flight query: {flight_query['from']} → {flight_query['to']}")
            try:
                flight_result = self.skill_manager.execute_skill(
                    "flight",
                    action=flight_query['action'],
                    from_airport=flight_query['from'],
                    to_airport=flight_query['to']
                )
                if flight_result.success:
                    return flight_result.data
                else:
                    print(f"⚠️ Flight skill failed: {flight_result.error}")
            except Exception as e:
                print(f"⚠️ Flight query detection error: {e}")
        
        # Pre-process: Check if this is a timezone query
        location = self._detect_timezone_query(task)
        if location:
            print(f"🌍 Detected timezone query for: {location}")
            try:
                time_result = self.skill_manager.execute_skill(
                    "timezone",
                    action="get_time",
                    location=location
                )
                if time_result.success:
                    return time_result.data
                else:
                    # If timezone skill fails, fall through to normal processing
                    print(f"⚠️ Timezone skill failed: {time_result.error}")
            except Exception as e:
                print(f"⚠️ Timezone query detection error: {e}")
        
        # Get current datetime and inject it into system prompt
        from datetime import datetime
        now = datetime.now()
        
        system_prompt = self.build_system_prompt()
        system_prompt += f"\n\n**CURRENT SYSTEM INFORMATION:**\n"
        system_prompt += f"- Current Date: {now.strftime('%A, %B %d, %Y')}\n"
        system_prompt += f"- Current Time: {now.strftime('%I:%M %p')}\n"
        system_prompt += f"- Day of Week: {now.strftime('%A')}\n"
        system_prompt += f"\nWhen users ask about the current time or date, use this information directly."
        
        # Add context reminder if there's conversation history
        if self.conversation_history:
            system_prompt += f"\n\n**CONVERSATION CONTEXT:**\n"
            system_prompt += f"This is an ongoing conversation. You have exchanged {len(self.conversation_history)//2} messages with the user.\n"
            system_prompt += f"The conversation history is included below. Reference it when the user asks follow-up questions.\n"
            system_prompt += f"Maintain continuity and don't reset or reintroduce yourself.\n"
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history (last 10 messages = 5 back-and-forth exchanges)
        messages.extend(self.conversation_history[-10:])
        
        # Add current task
        user_message = task
        if context:
            user_message = f"Context: {context}\n\nTask: {task}"
        
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        try:
            response = self.llm.generate(messages, temperature=0.7)
            
            # Check if response is a skill request
            response = self._handle_skill_request(response)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": task})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        except Exception as e:
            return f"Error processing task: {str(e)}"
    
    def _handle_skill_request(self, response: str) -> str:
        """Check if response contains a skill request and execute it."""
        try:
            import json
            import re
            
            # Check if response contains a JSON skill request
            if "use_skill" in response:
                # Try to extract JSON from response (may have text before/after)
                # Match balanced braces to handle nested parameters
                json_match = re.search(r'\{[^{}]*"action"[^{}]*"use_skill"[^{}]*\{[^{}]*\}[^{}]*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    # Clean up any formatting issues
                    json_str = json_str.replace('\n', ' ').replace('  ', ' ')
                    request = json.loads(json_str)
                    
                    if request.get("action") == "use_skill":
                        skill_name = request.get("skill")
                        parameters = request.get("parameters", {})
                        
                        print(f"\n🔧 Executing skill: {skill_name}")
                        
                        # Handle web search specially
                        if skill_name == "web_search":
                            return self._execute_web_search(parameters.get("query", ""), parameters.get("num_results", 5))
                        
                        # Handle URL fetching specially
                        if skill_name == "fetch_url":
                            return self._fetch_url_content(parameters.get("url", ""))
                        
                        # Handle datetime requests
                        if skill_name == "get_datetime":
                            return self._get_current_datetime()
                        
                        # Execute other skills
                        result = self.skill_manager.execute_skill(skill_name, **parameters)
                        
                        if result.success:
                            return f"✓ Skill executed successfully:\n{result.data}"
                        else:
                            # If skill fails, return normal response without skill
                            # This prevents disrupting the conversation
                            return response.split('\n')[0] if '\n' in response else response
        except Exception as e:
            print(f"⚠️ Skill parsing error: {e}")
            pass  # Not a skill request, return original response
        
        return response
    
    def _execute_web_search(self, query: str, num_results: int = 5) -> str:
        """Execute a web search and format results."""
        from .web_search import search_web
        
        results = search_web(query, num_results)
        
        if not results:
            return f"I searched for '{query}' but couldn't find any results."
        
        # Format results with clear instruction to only cite what's shown
        formatted = f"Here are the search results for '{query}'. ONLY use information from these results:\n\n"
        for i, result in enumerate(results, 1):
            formatted += f"{i}. **{result['title']}**\n"
            formatted += f"   {result['snippet']}\n"
            formatted += f"   URL: {result['url']}\n\n"
        
        formatted += "\n[INSTRUCTION: Answer the user's question using ONLY the information above. Do not add details not present in these snippets. If the snippets don't contain specific information, say so.]"
        
        return formatted
    
    def _fetch_url_content(self, url: str) -> str:
        """Fetch and extract clean content from a URL."""
        if not url:
            return "Error: No URL provided."
        
        print(f"\n📄 Fetching content from: {url}")
        
        try:
            # Try Jina AI Reader first (free, converts to clean markdown)
            import requests
            jina_url = f"https://r.jina.ai/{url}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(jina_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                content = response.text
                
                # Limit content length to avoid token overload (keep first 5000 chars)
                if len(content) > 5000:
                    content = content[:5000] + "\n\n[Content truncated for length...]\n"
                
                print(f"✓ Fetched {len(content)} characters")
                return f"Content from {url}:\n\n{content}"
            else:
                # Fallback to direct fetch with BeautifulSoup
                return self._fetch_url_fallback(url)
                
        except Exception as e:
            print(f"⚠️ Jina fetch failed, trying fallback: {e}")
            return self._fetch_url_fallback(url)
    
    def _fetch_url_fallback(self, url: str) -> str:
        """Fallback method using direct requests + BeautifulSoup."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            content = '\n'.join(lines)
            
            # Limit length
            if len(content) > 5000:
                content = content[:5000] + "\n\n[Content truncated for length...]\n"
            
            print(f"✓ Fetched {len(content)} characters (fallback method)")
            return f"Content from {url}:\n\n{content}"
            
        except ImportError:
            return f"Error: BeautifulSoup not installed. Install with: pip install beautifulsoup4\nURL: {url}"
        except Exception as e:
            return f"Error fetching URL: {str(e)}\nURL: {url}"
    
    def _get_current_datetime(self) -> str:
        """Get current date and time."""
        from datetime import datetime
        import pytz
        
        try:
            # Get current time
            now = datetime.now()
            
            # Format multiple useful representations
            info = f"""Current Date and Time:

• Full: {now.strftime('%A, %B %d, %Y at %I:%M:%S %p')}
• Date: {now.strftime('%Y-%m-%d')}
• Time: {now.strftime('%I:%M:%S %p')}
• Day: {now.strftime('%A')}
• Unix timestamp: {int(now.timestamp())}

Use this information to answer the user's question about the current time or date."""
            
            return info
            
        except Exception as e:
            return f"Error getting current datetime: {str(e)}"
    
    def make_decision(self, decision_prompt: str, options: List[str]) -> Dict:
        """Make a decision based on user's decision patterns."""
        print(f"\n🎯 Making decision: {decision_prompt[:50]}...")
        
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        task = f"""Decision Required: {decision_prompt}

Options:
{options_text}

Based on my decision-making style and priorities, which option should I choose? Explain your reasoning and provide the choice number."""
        
        response = self.process_task(task)
        
        return {
            "prompt": decision_prompt,
            "options": options,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def learn_from_example(self, example_text: str, example_type: str = "writing"):
        """Learn from a new example of user behavior."""
        print(f"📚 Learning from {example_type} example...")
        
        if example_type == "writing":
            self.profile.writing_style.examples.append(example_text)
            self.profile.writing_style.examples = self.profile.writing_style.examples[-50:]
    
    def update_preferences(self, category: str, preferences: Dict):
        """Update preferences in the profile."""
        if category == "communication":
            self.profile.preferences.communication.update(preferences)
        elif category == "work_style":
            self.profile.preferences.work_style.update(preferences)
        elif category == "interaction_style":
            self.profile.preferences.interaction_style.update(preferences)
        else:
            self.profile.preferences.custom.update(preferences)
    
    def get_agent_status(self) -> Dict:
        """Get current agent status and metrics."""
        return {
            "user_id": self.profile.user_id,
            "total_interactions": self.profile.interaction_count,
            "feedback_received": self.profile.feedback_received,
            "accuracy_score": f"{self.profile.accuracy_score:.2%}",
            "writing_examples": len(self.profile.writing_style.examples),
            "decision_history": len(self.profile.decision_pattern.past_decisions),
            "last_updated": self.profile.updated_at
        }
    
    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []


class AgentManager:
    """Manages the persona agent lifecycle."""
    
    def __init__(self, data_dir: str = "./data", encryption_key: str = None):
        self.profile_manager = ProfileManager(data_dir, encryption_key)
        self.data_dir = data_dir
        
    def initialize_agent(self, user_id: str = None, provider_name: str = None, use_adaptive_profile: bool = False) -> PersonaAgent:
        """Initialize or load persona agent with optional adaptive profile."""
        # Load or create profile
        profile = self.profile_manager.load_profile()
        if not profile:
            if not user_id:
                user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
            profile = self.profile_manager.create_profile(user_id)
        
        # Initialize LLM provider
        llm = get_llm_provider(provider_name)
        
        # Initialize skill manager and load built-in skills
        from .skills.builtin import CalculatorSkill, FileOpsSkill, WebSearchSkill, TimezoneSkill, FlightSkill
        skill_manager = SkillManager()
        skill_manager.registry.register(CalculatorSkill())
        skill_manager.registry.register(FileOpsSkill())
        skill_manager.registry.register(WebSearchSkill())
        skill_manager.registry.register(TimezoneSkill())
        skill_manager.registry.register(FlightSkill())
        
        # Load adaptive profile if requested
        adaptive_profile = None
        if use_adaptive_profile:
            from .user_profiling import UserProfilingSystem
            profiling_system = UserProfilingSystem(self.data_dir)
            adaptive_profile = profiling_system.load_profile(profile.user_id)
            
            if adaptive_profile:
                print(f"✓ Loaded adaptive profile: {adaptive_profile.profession} ({adaptive_profile.preferred_communication_style})")
        
        # Create agent
        agent = PersonaAgent(profile, llm, skill_manager, adaptive_profile)
        print(f"✓ Persona Agent initialized for: {profile.user_id}")
        print(f"✓ Loaded {len(skill_manager.list_available_skills())} skills")
        
        return agent
    
    def save_agent_state(self, agent: PersonaAgent):
        """Save agent's profile state."""
        self.profile_manager.save_profile(agent.profile)
