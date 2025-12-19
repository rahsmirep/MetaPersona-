"""
Timezone Skill
Provides comprehensive timezone information with UTC offsets.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from ..base import Skill, SkillMetadata, SkillParameter, SkillResult


class TimezoneSkill(Skill):
    """Timezone information and conversion skill."""
    
    def __init__(self):
        super().__init__()
        self.tf = TimezoneFinder()
        self.geolocator = Nominatim(user_agent="metapersona-timezone-skill")
    
    # Common location to timezone mapping (fast path for common queries)
    LOCATION_MAP = {
        # US States
        "california": "America/Los_Angeles",
        "new york": "America/New_York",
        "texas": "America/Chicago",
        "florida": "America/New_York",
        "illinois": "America/Chicago",
        "washington": "America/Los_Angeles",
        "arizona": "America/Phoenix",
        "nevada": "America/Los_Angeles",
        "hawaii": "Pacific/Honolulu",
        "alaska": "America/Anchorage",
        
        # Major US Cities
        "los angeles": "America/Los_Angeles",
        "san francisco": "America/Los_Angeles",
        "seattle": "America/Los_Angeles",
        "chicago": "America/Chicago",
        "dallas": "America/Chicago",
        "houston": "America/Chicago",
        "miami": "America/New_York",
        "boston": "America/New_York",
        "denver": "America/Denver",
        "phoenix": "America/Phoenix",
        
        # International Cities
        "london": "Europe/London",
        "paris": "Europe/Paris",
        "berlin": "Europe/Berlin",
        "tokyo": "Asia/Tokyo",
        "beijing": "Asia/Shanghai",
        "shanghai": "Asia/Shanghai",
        "hong kong": "Asia/Hong_Kong",
        "singapore": "Asia/Singapore",
        "sydney": "Australia/Sydney",
        "melbourne": "Australia/Melbourne",
        "dubai": "Asia/Dubai",
        "moscow": "Europe/Moscow",
        "mumbai": "Asia/Kolkata",
        "delhi": "Asia/Kolkata",
        "toronto": "America/Toronto",
        "vancouver": "America/Vancouver",
        "mexico city": "America/Mexico_City",
        "sao paulo": "America/Sao_Paulo",
        "buenos aires": "America/Argentina/Buenos_Aires",
        
        # Countries/Regions
        "uk": "Europe/London",
        "usa": "America/New_York",
        "canada": "America/Toronto",
        "australia": "Australia/Sydney",
        "japan": "Asia/Tokyo",
        "china": "Asia/Shanghai",
        "india": "Asia/Kolkata",
        "germany": "Europe/Berlin",
        "france": "Europe/Paris",
    }
    
    def _resolve_location(self, location: str) -> Optional[str]:
        """Resolve a location name to a timezone identifier using multiple strategies."""
        if not location:
            return None
        
        location_lower = location.lower().strip()
        
        # Strategy 1: Direct timezone name (e.g., "America/Los_Angeles")
        if '/' in location:
            return location
        
        # Strategy 2: Check hardcoded common locations (fast path)
        if location_lower in self.LOCATION_MAP:
            return self.LOCATION_MAP[location_lower]
        
        # Strategy 3: Try partial match in location map
        for key, tz in self.LOCATION_MAP.items():
            if location_lower in key or key in location_lower:
                return tz
        
        # Strategy 4: Fuzzy match against pytz timezone names
        # Try to find timezone names containing the location
        all_timezones = pytz.all_timezones
        for tz_name in all_timezones:
            tz_parts = tz_name.lower().replace('_', ' ').split('/')
            if location_lower in ' '.join(tz_parts):
                return tz_name
        
        # Strategy 5: Use geocoding + timezonefinder (works for any city)
        try:
            # Try different geocoding strategies for better accuracy
            geocode_queries = [
                location,  # Original query
                f"{location}, USA" if 'usa' not in location_lower and 'united states' not in location_lower else location,
            ]
            
            # Try to add country context for US states
            us_states = ['north carolina', 'south carolina', 'california', 'new york', 'texas', 'florida']
            for state in us_states:
                if state in location_lower and ', usa' not in location_lower:
                    geocode_queries.append(f"{location}, USA")
                    break
            
            geocode_result = None
            for query in geocode_queries:
                try:
                    result = self.geolocator.geocode(query, timeout=5, exactly_one=True)
                    if result:
                        # Verify the result is relevant by checking if location name appears in result
                        result_lower = result.address.lower()
                        # For multi-word locations like "winston-salem", check each part
                        location_parts = location_lower.replace('-', ' ').split()
                        match_score = sum(1 for part in location_parts if len(part) > 3 and part in result_lower)
                        
                        if match_score >= len([p for p in location_parts if len(p) > 3]) * 0.5:
                            geocode_result = result
                            break
                except (GeocoderTimedOut, GeocoderServiceError):
                    continue
            
            if geocode_result:
                # Use timezonefinder to get timezone from coordinates
                latitude = geocode_result.latitude
                longitude = geocode_result.longitude
                timezone_name = self.tf.timezone_at(lat=latitude, lng=longitude)
                if timezone_name:
                    return timezone_name
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            # If geocoding fails, continue to return None
            print(f"⚠️ Geocoding error for '{location}': {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error resolving location '{location}': {e}")
        
        return None
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="timezone",
            description="Get comprehensive timezone information, UTC offsets, and time conversions",
            category="Utilities",
            parameters=[
                SkillParameter(
                    name="action",
                    type="str",
                    description="Action to perform: 'list_all' (all timezones), 'get_time' (get current time in location), 'convert' (convert time between zones), 'info' (timezone details)",
                    required=True
                ),
                SkillParameter(
                    name="location",
                    type="str",
                    description="Location name (e.g., 'California', 'London', 'Tokyo') - can be city, state, or country",
                    required=False
                ),
                SkillParameter(
                    name="from_tz",
                    type="str",
                    description="Source timezone name or location for conversion",
                    required=False
                ),
                SkillParameter(
                    name="to_tz",
                    type="str",
                    description="Target timezone name for conversion",
                    required=False
                ),
                SkillParameter(
                    name="time",
                    type="str",
                    description="Time to convert (format: 'YYYY-MM-DD HH:MM:SS'). If not provided, uses current time.",
                    required=False
                )
            ],
            returns="Timezone information or conversion result"
        )
    
    def execute(self, action: str, location: str = None, from_tz: str = None, to_tz: str = None, time: str = None) -> SkillResult:
        """Execute timezone operations."""
        try:
            if action == "list_all":
                return self._list_all_timezones()
            elif action == "get_time":
                if not location:
                    return SkillResult(
                        success=False,
                        error="'location' parameter is required for get_time"
                    )
                return self._get_time_in_location(location)
            elif action == "convert":
                if not from_tz or not to_tz:
                    return SkillResult(
                        success=False,
                        error="Both 'from_tz' and 'to_tz' are required for conversion"
                    )
                return self._convert_timezone(from_tz, to_tz, time)
            elif action == "info":
                loc = location or from_tz
                if not loc:
                    return SkillResult(
                        success=False,
                        error="'location' or 'from_tz' parameter is required for timezone info"
                    )
                return self._get_timezone_info(loc)
            else:
                return SkillResult(
                    success=False,
                    error=f"Unknown action: {action}. Use 'list_all', 'get_time', 'convert', or 'info'"
                )
        except Exception as e:
            return SkillResult(success=False, error=str(e))
    
    def _list_all_timezones(self) -> SkillResult:
        """List all global timezones with UTC offsets."""
        timezone_data = {
            "UTC−12:00": ["Baker Island", "Howland Island"],
            "UTC−11:00": ["American Samoa", "Niue"],
            "UTC−10:00": ["Hawaii-Aleutian Standard Time (HST)", "Honolulu"],
            "UTC−09:30": ["Marquesas Islands"],
            "UTC−09:00": ["Alaska Standard Time (AKST)"],
            "UTC−08:00": ["Pacific Standard Time (PST)", "Los Angeles", "Vancouver"],
            "UTC−07:00": ["Mountain Standard Time (MST)", "Denver", "Phoenix"],
            "UTC−06:00": ["Central Standard Time (CST)", "Chicago", "Mexico City"],
            "UTC−05:00": ["Eastern Standard Time (EST)", "New York", "Toronto"],
            "UTC−04:00": ["Atlantic Standard Time (AST)", "Halifax", "Bermuda"],
            "UTC−03:30": ["Newfoundland Standard Time (NST)", "St. John's"],
            "UTC−03:00": ["Argentina", "Brazil (Brasília)", "Uruguay"],
            "UTC−02:00": ["South Georgia and South Sandwich Islands"],
            "UTC−01:00": ["Cape Verde", "Azores"],
            "UTC±00:00": ["Greenwich Mean Time (GMT)", "London", "Lisbon"],
            "UTC+01:00": ["Central European Time (CET)", "Paris", "Berlin", "Rome"],
            "UTC+02:00": ["Eastern European Time (EET)", "Cairo", "Athens", "Johannesburg"],
            "UTC+03:00": ["Moscow Standard Time (MSK)", "Nairobi", "Istanbul"],
            "UTC+03:30": ["Iran Standard Time (IRST)", "Tehran"],
            "UTC+04:00": ["Gulf Standard Time (GST)", "Dubai", "Baku"],
            "UTC+04:30": ["Afghanistan Time (AFT)", "Kabul"],
            "UTC+05:00": ["Pakistan Standard Time (PKT)", "Karachi", "Tashkent"],
            "UTC+05:30": ["Indian Standard Time (IST)", "Mumbai", "Colombo"],
            "UTC+05:45": ["Nepal Time (NPT)", "Kathmandu"],
            "UTC+06:00": ["Bangladesh Standard Time (BST)", "Dhaka", "Almaty"],
            "UTC+06:30": ["Cocos Islands", "Myanmar (Burma)", "Yangon"],
            "UTC+07:00": ["Indochina Time (ICT)", "Bangkok", "Jakarta", "Hanoi"],
            "UTC+08:00": ["China Standard Time (CST)", "Beijing", "Singapore", "Perth"],
            "UTC+08:45": ["Australian Central Western Standard Time (ACWST)", "Eucla"],
            "UTC+09:00": ["Japan Standard Time (JST)", "Tokyo", "Seoul"],
            "UTC+09:30": ["Australian Central Standard Time (ACST)", "Adelaide", "Darwin"],
            "UTC+10:00": ["Australian Eastern Standard Time (AEST)", "Sydney", "Melbourne"],
            "UTC+10:30": ["Lord Howe Island"],
            "UTC+11:00": ["Solomon Islands", "Vanuatu", "New Caledonia"],
            "UTC+12:00": ["New Zealand Standard Time (NZST)", "Fiji", "Auckland"],
            "UTC+12:45": ["Chatham Islands"],
            "UTC+13:00": ["Tonga", "Phoenix Islands (Kiribati)"],
            "UTC+14:00": ["Line Islands (Kiribati)"]
        }
        
        # Format the output
        output = "**COMPLETE GLOBAL TIMEZONE LIST**\n\n"
        
        for offset, locations in timezone_data.items():
            output += f"**{offset}**\n"
            for location in locations:
                output += f"  • {location}\n"
            output += "\n"
        
        output += "\n**Summary:**\n"
        output += "• Total range: 27 hours (UTC−12 to UTC+14)\n"
        output += "• Quarter-hour offsets: UTC+05:45 (Nepal), UTC+12:45 (Chatham Islands)\n"
        output += "• Half-hour offsets: UTC−09:30, UTC−03:30, UTC+03:30, UTC+04:30, UTC+05:30, UTC+06:30, UTC+08:45, UTC+09:30, UTC+10:30\n"
        output += "• Note: Some regions observe Daylight Saving Time (DST), shifting offsets by +1 hour\n"
        
        return SkillResult(success=True, data=output)
    
    def _get_time_in_location(self, location: str) -> SkillResult:
        """Get current time in a specific location."""
        # Resolve location to timezone
        tz_name = self._resolve_location(location)
        
        if not tz_name:
            return SkillResult(
                success=False,
                error=f"Could not find timezone for '{location}'. Try using specific timezone names like 'America/Los_Angeles' or common cities like 'London', 'Tokyo', 'New York'."
            )
        
        try:
            tz = pytz.timezone(tz_name)
            now = datetime.now(tz)
            
            result = f"**Current Time in {location.title()}**\n\n"
            result += f"Time: {now.strftime('%I:%M:%S %p')}\n"
            result += f"Date: {now.strftime('%A, %B %d, %Y')}\n"
            result += f"Timezone: {tz_name} ({now.strftime('%Z')})\n"
            result += f"UTC Offset: {now.strftime('%z')}\n"
            
            return SkillResult(success=True, data=result)
        except pytz.exceptions.UnknownTimeZoneError:
            return SkillResult(
                success=False,
                error=f"Unknown timezone: {tz_name}"
            )
    
    def _convert_timezone(self, from_tz: str, to_tz: str, time_str: str = None) -> SkillResult:
        """Convert time between timezones."""
        try:
            # Resolve locations to timezone names
            from_tz_resolved = self._resolve_location(from_tz) or from_tz
            to_tz_resolved = self._resolve_location(to_tz) or to_tz
            
            # Get timezone objects
            from_zone = pytz.timezone(from_tz_resolved)
            to_zone = pytz.timezone(to_tz_resolved)
            
            # Parse or use current time
            if time_str:
                dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                dt = from_zone.localize(dt)
            else:
                dt = datetime.now(from_zone)
            
            # Convert
            converted = dt.astimezone(to_zone)
            
            result = f"**Time Conversion**\n\n"
            result += f"From: {dt.strftime('%Y-%m-%d %H:%M:%S %Z')} ({from_tz})\n"
            result += f"To: {converted.strftime('%Y-%m-%d %H:%M:%S %Z')} ({to_tz})\n"
            result += f"\nUTC Offsets:\n"
            result += f"  • {from_tz}: {dt.strftime('%z')}\n"
            result += f"  • {to_tz}: {converted.strftime('%z')}\n"
            
            return SkillResult(success=True, data=result)
        except pytz.exceptions.UnknownTimeZoneError as e:
            return SkillResult(
                success=False,
                error=f"Unknown timezone: {e}. Use pytz.all_timezones to see valid names."
            )
        except ValueError as e:
            return SkillResult(
                success=False,
                error=f"Invalid time format. Use 'YYYY-MM-DD HH:MM:SS'. Error: {e}"
            )
    
    def _get_timezone_info(self, tz_name: str) -> SkillResult:
        """Get detailed information about a specific timezone."""
        try:
            # Resolve location to timezone
            tz_resolved = self._resolve_location(tz_name) or tz_name
            tz = pytz.timezone(tz_resolved)
            now = datetime.now(tz)
            
            result = f"**Timezone Information: {tz_name}**\n\n"
            result += f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            result += f"UTC offset: {now.strftime('%z')} ({now.strftime('%Z')})\n"
            result += f"Timezone: {tz_name}\n"
            
            return SkillResult(success=True, data=result)
        except pytz.exceptions.UnknownTimeZoneError:
            # Try to suggest similar timezones
            all_tz = pytz.all_timezones
            suggestions = [tz for tz in all_tz if tz_name.lower() in tz.lower()]
            
            error_msg = f"Unknown timezone: {tz_name}"
            if suggestions:
                error_msg += f"\n\nDid you mean one of these?\n"
                for s in suggestions[:5]:
                    error_msg += f"  • {s}\n"
            
            return SkillResult(success=False, error=error_msg)
