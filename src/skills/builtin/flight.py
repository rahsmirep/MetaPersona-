"""
Flight Distance & Time Calculation Skill with API Integration

Provides accurate flight time estimates and real-time flight data using:
1. Distance calculation (offline, always available)
2. OpenSky Network API (free, real-time flight data)
3. AviationStack API (free tier, flight schedules)
"""

from typing import Dict, Optional, Any
import math
import requests
from datetime import datetime, timedelta
import airportsdata

from ..base import Skill, SkillMetadata, SkillParameter, SkillResult


class FlightSkill(Skill):
    """Calculate flight times, distances between airports, and get real-time flight information."""
    
    def __init__(self):
        super().__init__()
        self.opensky_base_url = "https://opensky-network.org/api"
        self.aviationstack_api_key = None  # User can add their free API key
        self.aviationstack_base_url = "http://api.aviationstack.com/v1"
        
        # Load comprehensive airport database (28,000+ airports worldwide)
        self.airports_db = airportsdata.load('IATA')  # Load by IATA code
        
        print(f"✓ Loaded {len(self.airports_db)} airports from database")
        self.AIRPORTS = {
            # US Major Airports
            "ATL": (33.6407, -84.4277, "Hartsfield-Jackson Atlanta", "Atlanta, GA"),
            "LAX": (33.9416, -118.4085, "Los Angeles International", "Los Angeles, CA"),
            "ORD": (41.9742, -87.9073, "O'Hare International", "Chicago, IL"),
            "DFW": (32.8998, -97.0403, "Dallas/Fort Worth International", "Dallas, TX"),
            "DEN": (39.8561, -104.6737, "Denver International", "Denver, CO"),
            "JFK": (40.6413, -73.7781, "John F. Kennedy International", "New York, NY"),
            "SFO": (37.6213, -122.3790, "San Francisco International", "San Francisco, CA"),
            "SEA": (47.4502, -122.3088, "Seattle-Tacoma International", "Seattle, WA"),
            "LAS": (36.0840, -115.1537, "McCarran International", "Las Vegas, NV"),
            "MCO": (28.4312, -81.3081, "Orlando International", "Orlando, FL"),
            "EWR": (40.6895, -74.1745, "Newark Liberty International", "Newark, NJ"),
            "MIA": (25.7959, -80.2870, "Miami International", "Miami, FL"),
            "PHX": (33.4352, -112.0101, "Phoenix Sky Harbor", "Phoenix, AZ"),
            "IAH": (29.9902, -95.3368, "George Bush Intercontinental", "Houston, TX"),
            "BOS": (42.3656, -71.0096, "Logan International", "Boston, MA"),
            "MSP": (44.8848, -93.2223, "Minneapolis-St Paul International", "Minneapolis, MN"),
            "DTW": (42.2162, -83.3554, "Detroit Metropolitan", "Detroit, MI"),
            "PHL": (39.8744, -75.2424, "Philadelphia International", "Philadelphia, PA"),
            "LGA": (40.7769, -73.8740, "LaGuardia Airport", "New York, NY"),
            "BWI": (39.1774, -76.6684, "Baltimore/Washington International", "Baltimore, MD"),
            "SLC": (40.7899, -111.9791, "Salt Lake City International", "Salt Lake City, UT"),
            "IAD": (38.9531, -77.4565, "Washington Dulles International", "Washington, DC"),
            "DCA": (38.8512, -77.0402, "Ronald Reagan Washington National", "Washington, DC"),
            "SAN": (32.7336, -117.1897, "San Diego International", "San Diego, CA"),
            "PDX": (45.5898, -122.5951, "Portland International", "Portland, OR"),
            "HNL": (21.3187, -157.9225, "Daniel K. Inouye International", "Honolulu, HI"),
            "BNA": (36.1245, -86.6782, "Nashville International", "Nashville, TN"),
            "AUS": (30.1945, -97.6699, "Austin-Bergstrom International", "Austin, TX"),
            "MDW": (41.7868, -87.7522, "Chicago Midway International", "Chicago, IL"),
            "TPA": (27.9755, -82.5332, "Tampa International", "Tampa, FL"),
            "ABQ": (35.0402, -106.6092, "Albuquerque International Sunport", "Albuquerque, NM"),
            "RDU": (35.8801, -78.7880, "Raleigh-Durham International", "Raleigh, NC"),
            "OAK": (37.7126, -122.2197, "Oakland International", "Oakland, CA"),
            "SJC": (37.3639, -121.9289, "San Jose International", "San Jose, CA"),
            "SAT": (29.5337, -98.4698, "San Antonio International", "San Antonio, TX"),
            "SMF": (38.6954, -121.5901, "Sacramento International", "Sacramento, CA"),
            "CLE": (41.4117, -81.8498, "Cleveland Hopkins International", "Cleveland, OH"),
            "PIT": (40.4915, -80.2329, "Pittsburgh International", "Pittsburgh, PA"),
            "STL": (38.7487, -90.3700, "St. Louis Lambert International", "St. Louis, MO"),
            "CVG": (39.0533, -84.6630, "Cincinnati/Northern Kentucky International", "Cincinnati, OH"),
            "CMH": (39.9980, -82.8919, "John Glenn Columbus International", "Columbus, OH"),
            "IND": (39.7173, -86.2944, "Indianapolis International", "Indianapolis, IN"),
            "MCI": (39.2976, -94.7139, "Kansas City International", "Kansas City, MO"),
            "MKE": (42.9472, -87.8966, "Milwaukee Mitchell International", "Milwaukee, WI"),
            "OMA": (41.3032, -95.8941, "Eppley Airfield", "Omaha, NE"),
            "BUF": (42.9405, -78.7322, "Buffalo Niagara International", "Buffalo, NY"),
            "RSW": (26.5362, -81.7552, "Southwest Florida International", "Fort Myers, FL"),
            "JAX": (30.4941, -81.6879, "Jacksonville International", "Jacksonville, FL"),
            "BDL": (41.9389, -72.6832, "Bradley International", "Hartford, CT"),
            "ONT": (34.0560, -117.6012, "Ontario International", "Ontario, CA"),
            
            # International Major Airports
            "LHR": (51.4700, -0.4543, "London Heathrow", "London, UK"),
            "CDG": (49.0097, 2.5479, "Charles de Gaulle", "Paris, France"),
            "FRA": (50.0379, 8.5622, "Frankfurt Airport", "Frankfurt, Germany"),
            "AMS": (52.3105, 4.7683, "Amsterdam Schiphol", "Amsterdam, Netherlands"),
            "MAD": (40.4983, -3.5676, "Adolfo Suárez Madrid-Barajas", "Madrid, Spain"),
            "FCO": (41.8003, 12.2389, "Leonardo da Vinci-Fiumicino", "Rome, Italy"),
            "MUC": (48.3537, 11.7750, "Munich Airport", "Munich, Germany"),
            "BCN": (41.2974, 2.0833, "Barcelona-El Prat", "Barcelona, Spain"),
            "LGW": (51.1537, -0.1821, "London Gatwick", "London, UK"),
            "ZRH": (47.4647, 8.5492, "Zurich Airport", "Zurich, Switzerland"),
            "VIE": (48.1103, 16.5697, "Vienna International", "Vienna, Austria"),
            "CPH": (55.6180, 12.6508, "Copenhagen Airport", "Copenhagen, Denmark"),
            "OSL": (60.1939, 11.1004, "Oslo Gardermoen", "Oslo, Norway"),
            "ARN": (59.6498, 17.9238, "Stockholm Arlanda", "Stockholm, Sweden"),
            "HEL": (60.3172, 24.9633, "Helsinki-Vantaa", "Helsinki, Finland"),
            "DUB": (53.4213, -6.2701, "Dublin Airport", "Dublin, Ireland"),
            "BRU": (50.9014, 4.4844, "Brussels Airport", "Brussels, Belgium"),
            "LIS": (38.7742, -9.1342, "Lisbon Portela", "Lisbon, Portugal"),
            "ATH": (37.9364, 23.9445, "Athens International", "Athens, Greece"),
            "IST": (41.2753, 28.7519, "Istanbul Airport", "Istanbul, Turkey"),
            
            # Asia-Pacific
            "NRT": (35.7653, 140.3854, "Narita International", "Tokyo, Japan"),
            "HND": (35.5494, 139.7798, "Tokyo Haneda", "Tokyo, Japan"),
            "ICN": (37.4602, 126.4407, "Incheon International", "Seoul, South Korea"),
            "PEK": (40.0799, 116.6031, "Beijing Capital International", "Beijing, China"),
            "PVG": (31.1443, 121.8083, "Shanghai Pudong International", "Shanghai, China"),
            "HKG": (22.3080, 113.9185, "Hong Kong International", "Hong Kong"),
            "SIN": (1.3644, 103.9915, "Singapore Changi", "Singapore"),
            "BKK": (13.6900, 100.7501, "Suvarnabhumi Airport", "Bangkok, Thailand"),
            "KUL": (2.7456, 101.7072, "Kuala Lumpur International", "Kuala Lumpur, Malaysia"),
            "DEL": (28.5562, 77.1000, "Indira Gandhi International", "New Delhi, India"),
            "BOM": (19.0896, 72.8656, "Chhatrapati Shivaji Maharaj International", "Mumbai, India"),
            "SYD": (-33.9399, 151.1753, "Sydney Kingsford Smith", "Sydney, Australia"),
            "MEL": (-37.6690, 144.8410, "Melbourne Airport", "Melbourne, Australia"),
            "AKL": (-37.0082, 174.7850, "Auckland Airport", "Auckland, New Zealand"),
            
            # Middle East
            "DXB": (25.2532, 55.3657, "Dubai International", "Dubai, UAE"),
            "DOH": (25.2731, 51.6080, "Hamad International", "Doha, Qatar"),
            "AUH": (24.4330, 54.6511, "Abu Dhabi International", "Abu Dhabi, UAE"),
            "TLV": (32.0114, 34.8867, "Ben Gurion Airport", "Tel Aviv, Israel"),
            
            # South America
            "GRU": (-23.4356, -46.4731, "São Paulo-Guarulhos International", "São Paulo, Brazil"),
            "GIG": (-22.8099, -43.2505, "Rio de Janeiro-Galeão International", "Rio de Janeiro, Brazil"),
            "EZE": (-34.8222, -58.5358, "Ministro Pistarini International", "Buenos Aires, Argentina"),
            "BOG": (4.7016, -74.1469, "El Dorado International", "Bogotá, Colombia"),
            "LIM": (-12.0219, -77.1143, "Jorge Chávez International", "Lima, Peru"),
            "SCL": (-33.3930, -70.7858, "Arturo Merino Benítez International", "Santiago, Chile"),
            
            # Canada
            "YYZ": (43.6777, -79.6248, "Toronto Pearson International", "Toronto, Canada"),
            "YVR": (49.1939, -123.1844, "Vancouver International", "Vancouver, Canada"),
            "YUL": (45.4657, -73.7455, "Montréal-Pierre Elliott Trudeau International", "Montreal, Canada"),
            "YYC": (51.1315, -114.0106, "Calgary International", "Calgary, Canada"),
        }
    
    def _resolve_airport(self, location: str) -> Optional[tuple]:
        """
        Resolve location to airport data using comprehensive database.
        Supports: IATA codes, city names, airport names.
        Returns: (code, lat, lon, name, city) or None
        """
        location_clean = location.strip().upper()
        
        # Strategy 1: Direct IATA code lookup
        if len(location_clean) == 3 and location_clean in self.airports_db:
            airport = self.airports_db[location_clean]
            return (
                location_clean,
                airport['lat'],
                airport['lon'],
                airport['name'],
                f"{airport['city']}, {airport['country']}"
            )
        
        # Strategy 2: Search by city name or airport name
        location_lower = location.lower()
        matches = []
        
        for code, airport in self.airports_db.items():
            city_lower = airport['city'].lower()
            name_lower = airport['name'].lower()
            airport_type = airport.get('subt', '').lower()
            
            # Skip heliports, seaplane bases, and small airports
            if any(skip in airport_type for skip in ['heliport', 'seaplane', 'closed', 'balloonport']):
                continue
            if any(skip in name_lower for skip in ['seaplane', 'heliport', 'helipad']):
                continue
            
            # Calculate match score
            score = 0
            
            # Exact city match (highest priority)
            if city_lower == location_lower:
                score = 100
            # City contains location
            elif location_lower in city_lower or city_lower in location_lower:
                score = 80
            # Airport name contains location
            elif location_lower in name_lower:
                score = 50
            
            if score > 0:
                # Bonus for large/medium airports
                if 'large_airport' in airport_type:
                    score += 20
                elif 'medium_airport' in airport_type:
                    score += 10
                
                # Bonus for "International" in name
                if 'international' in name_lower:
                    score += 5
                
                matches.append((code, airport, score))
        
        if matches:
            # Sort by score (highest first)
            matches.sort(key=lambda x: x[2], reverse=True)
            
            best_match = matches[0]
            code, airport = best_match[0], best_match[1]
            return (
                code,
                airport['lat'],
                airport['lon'],
                airport['name'],
                f"{airport['city']}, {airport['country']}"
            )
        
        return None
    
    def get_metadata(self) -> SkillMetadata:
        return SkillMetadata(
            name="flight",
            description="Calculate flight times, distances between airports, and get real-time flight information",
            category="travel",
            parameters=[
                SkillParameter(
                    name="action",
                    type="string",
                    description="Action to perform: flight_time, distance, flight_info, or route_info",
                    required=True
                ),
                SkillParameter(
                    name="from_airport",
                    type="string",
                    description="Origin airport (IATA code like 'LAX' or city name)",
                    required=False
                ),
                SkillParameter(
                    name="to_airport",
                    type="string",
                    description="Destination airport (IATA code like 'JFK' or city name)",
                    required=False
                ),
                SkillParameter(
                    name="flight_number",
                    type="string",
                    description="Flight number for real-time tracking (e.g., 'AA123')",
                    required=False
                )
            ]
        )
    
    def execute(self, **kwargs) -> SkillResult:
        """Execute flight skill action."""
        action = kwargs.get("action")
        
        if action == "flight_time":
            return self._calculate_flight_time(
                kwargs.get("from_airport"),
                kwargs.get("to_airport")
            )
        elif action == "distance":
            return self._calculate_distance(
                kwargs.get("from_airport"),
                kwargs.get("to_airport")
            )
        elif action == "flight_info":
            return self._get_flight_info(
                kwargs.get("flight_number")
            )
        elif action == "route_info":
            return self._get_route_info(
                kwargs.get("from_airport"),
                kwargs.get("to_airport")
            )
        else:
            return SkillResult(
                success=False,
                error=f"Unknown action: {action}. Use 'flight_time', 'distance', 'flight_info', or 'route_info'."
            )
    
    def _calculate_distance_km(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate great circle distance between two points using Haversine formula."""
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Earth's radius in kilometers
        radius = 6371
        
        return radius * c
    
    def _estimate_flight_time(self, distance_km: float) -> dict:
        """
        Estimate flight time based on distance, including realistic delays.
        
        Includes contingency for:
        - Weather conditions
        - Air traffic congestion
        - Wind patterns and routing deviations
        - ATC holds and spacing
        
        Returns dict with total_minutes, flight_minutes, ground_minutes, and contingency_minutes.
        """
        distance_miles = distance_km * 0.621371
        
        # Average cruising speed for commercial jets: ~500 mph
        cruising_speed_mph = 500
        
        # Calculate ideal flight time
        flight_hours = distance_miles / cruising_speed_mph
        flight_minutes = flight_hours * 60
        
        # Add ground time (taxi, takeoff, climb, descent, landing)
        # Short flights: ~20-25 min, Medium: ~25-30 min, Long: ~30-35 min
        if distance_miles < 500:
            ground_minutes = 25
        elif distance_miles < 1500:
            ground_minutes = 30
        else:
            ground_minutes = 35
        
        # Add contingency buffer for external factors
        # Weather, air traffic, wind, routing deviations, ATC holds
        # Typically 10-15% of total flight time
        base_time = flight_minutes + ground_minutes
        
        # Calculate contingency based on distance
        if distance_miles < 500:
            # Short flights: 10-15 minutes (busy airspace, weather impacts)
            contingency_minutes = int(base_time * 0.12)
        elif distance_miles < 1500:
            # Medium flights: 12-18 minutes
            contingency_minutes = int(base_time * 0.13)
        else:
            # Long flights: 15-25 minutes
            contingency_minutes = int(base_time * 0.14)
        
        # Ensure minimum contingency
        contingency_minutes = max(10, contingency_minutes)
        
        total_minutes = base_time + contingency_minutes
        
        return {
            "total_minutes": int(total_minutes),
            "flight_minutes": int(flight_minutes),
            "ground_minutes": ground_minutes,
            "contingency_minutes": contingency_minutes,
            "hours": int(total_minutes // 60),
            "minutes": int(total_minutes % 60)
        }
    
    def _calculate_flight_time(self, from_loc: str, to_loc: str) -> SkillResult:
        """Calculate estimated flight time between two airports."""
        if not from_loc or not to_loc:
            return SkillResult(
                success=False,
                error="Both 'from_airport' and 'to_airport' are required."
            )
        
        # Resolve airports
        from_airport = self._resolve_airport(from_loc)
        to_airport = self._resolve_airport(to_loc)
        
        if not from_airport:
            return SkillResult(
                success=False,
                error=f"Could not find airport for '{from_loc}'. Try IATA codes like LAX, JFK, ORD."
            )
        
        if not to_airport:
            return SkillResult(
                success=False,
                error=f"Could not find airport for '{to_loc}'. Try IATA codes like LAX, JFK, ORD."
            )
        
        from_code, from_lat, from_lon, from_name, from_city = from_airport
        to_code, to_lat, to_lon, to_name, to_city = to_airport
        
        # Calculate distance
        distance_km = self._calculate_distance_km(from_lat, from_lon, to_lat, to_lon)
        distance_miles = distance_km * 0.621371
        
        # Estimate flight time
        time_info = self._estimate_flight_time(distance_km)
        
        # Format result
        result = f"**Flight Time Estimate: {from_code} → {to_code}**\n\n"
        result += f"**Route:**\n"
        result += f"• From: {from_name} ({from_city})\n"
        result += f"• To: {to_name} ({to_city})\n\n"
        result += f"**Distance:**\n"
        result += f"• {distance_miles:,.0f} miles ({distance_km:,.0f} km)\n\n"
        result += f"**Estimated Flight Time:**\n"
        result += f"• Total: {time_info['hours']} hour{'s' if time_info['hours'] != 1 else ''} {time_info['minutes']} minutes\n"
        result += f"• In-air time: ~{time_info['flight_minutes']} minutes\n"
        result += f"• Ground time: ~{time_info['ground_minutes']} minutes (taxi, takeoff, landing)\n"
        result += f"• Contingency buffer: ~{time_info['contingency_minutes']} minutes (weather, air traffic, winds)\n\n"
        result += f"*Note: This estimate includes typical delays from weather conditions, air traffic congestion, wind patterns, and ATC routing. Individual flights may vary based on actual conditions.*"
        
        return SkillResult(success=True, data=result)
    
    def _calculate_distance(self, from_loc: str, to_loc: str) -> SkillResult:
        """Calculate distance between two airports."""
        if not from_loc or not to_loc:
            return SkillResult(
                success=False,
                error="Both 'from_airport' and 'to_airport' are required."
            )
        
        # Resolve airports
        from_airport = self._resolve_airport(from_loc)
        to_airport = self._resolve_airport(to_loc)
        
        if not from_airport:
            return SkillResult(
                success=False,
                error=f"Could not find airport for '{from_loc}'."
            )
        
        if not to_airport:
            return SkillResult(
                success=False,
                error=f"Could not find airport for '{to_loc}'."
            )
        
        from_code, from_lat, from_lon, from_name, from_city = from_airport
        to_code, to_lat, to_lon, to_name, to_city = to_airport
        
        # Calculate distance
        distance_km = self._calculate_distance_km(from_lat, from_lon, to_lat, to_lon)
        distance_miles = distance_km * 0.621371
        distance_nm = distance_miles * 0.868976  # Nautical miles
        
        result = f"**Distance: {from_code} → {to_code}**\n\n"
        result += f"• {from_city} to {to_city}\n"
        result += f"• {distance_miles:,.0f} miles\n"
        result += f"• {distance_km:,.0f} kilometers\n"
        result += f"• {distance_nm:,.0f} nautical miles\n"
        
        return SkillResult(success=True, data=result)
    
    def _get_flight_info(self, flight_number: str) -> SkillResult:
        """Get real-time flight information from OpenSky Network API."""
        if not flight_number:
            return SkillResult(
                success=False,
                error="'flight_number' is required for flight tracking."
            )
        
        try:
            # OpenSky Network API - free, no API key required
            # Get all flights (we'll filter by callsign)
            url = f"{self.opensky_base_url}/states/all"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Search for matching flight
                flight_number_upper = flight_number.upper().strip()
                
                if data and 'states' in data and data['states']:
                    matching_flights = []
                    
                    for state in data['states']:
                        # state[1] is callsign
                        callsign = state[1]
                        if callsign and flight_number_upper in callsign.strip().upper():
                            matching_flights.append(state)
                    
                    if matching_flights:
                        result = f"**Real-Time Flight Information: {flight_number}**\n\n"
                        
                        for idx, state in enumerate(matching_flights[:3], 1):  # Show up to 3 matches
                            callsign = state[1].strip() if state[1] else "N/A"
                            origin_country = state[2] if state[2] else "Unknown"
                            longitude = state[5]
                            latitude = state[6]
                            altitude = state[7]  # meters
                            velocity = state[9]  # m/s
                            
                            if idx > 1:
                                result += "\n---\n\n"
                            
                            result += f"**Flight {idx}: {callsign}**\n"
                            result += f"• Origin Country: {origin_country}\n"
                            
                            if latitude and longitude:
                                result += f"• Position: {latitude:.4f}°, {longitude:.4f}°\n"
                            
                            if altitude:
                                altitude_ft = altitude * 3.28084
                                result += f"• Altitude: {altitude_ft:,.0f} ft ({altitude:,.0f} m)\n"
                            
                            if velocity:
                                velocity_mph = velocity * 2.23694
                                velocity_knots = velocity * 1.94384
                                result += f"• Speed: {velocity_mph:.0f} mph ({velocity_knots:.0f} knots)\n"
                        
                        result += f"\n*Data from OpenSky Network (updated in real-time)*"
                        return SkillResult(success=True, data=result)
                    else:
                        return SkillResult(
                            success=False,
                            error=f"No active flights found matching '{flight_number}'. The flight may not be airborne currently."
                        )
                else:
                    return SkillResult(
                        success=False,
                        error="No flight data available from OpenSky Network at this time."
                    )
            else:
                return SkillResult(
                    success=False,
                    error=f"OpenSky Network API error (status {response.status_code}). Try again later."
                )
                
        except requests.exceptions.Timeout:
            return SkillResult(
                success=False,
                error="Request timed out. OpenSky Network may be busy."
            )
        except Exception as e:
            return SkillResult(
                success=False,
                error=f"Error fetching flight data: {str(e)}"
            )
    
    def _get_route_info(self, from_loc: str, to_loc: str) -> SkillResult:
        """Get route information (falls back to calculation if API unavailable)."""
        # For now, this uses calculation. Could integrate AviationStack API if user provides key.
        
        if not self.aviationstack_api_key:
            # Fallback to calculation
            return self._calculate_flight_time(from_loc, to_loc)
        
        # AviationStack API integration would go here
        # This is a placeholder for when user adds their free API key
        
        return self._calculate_flight_time(from_loc, to_loc)
