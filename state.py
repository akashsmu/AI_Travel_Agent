from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TravelState(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    origin_id: Optional[str] = None # For Flight API (IATA or KG ID)
    destination_id: Optional[str] = None # For Flight API (IATA or KG ID)
    origin_city: Optional[str] = None    # For Weather/Hotels
    destination_city: Optional[str] = None # For Weather/Hotels
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    bedrooms: Optional[int] = 1
    max_price_per_night: Optional[float] = 200.0
    min_rating: Optional[float] = 4.0
    max_flight_price: Optional[float] = None
    
    # Trip parameters
    trip_purpose: Optional[str] = "vacation"
    travel_party: Optional[str] = "solo" # 'solo' or 'group'
    
    # Age logic
    traveler_age: Optional[int] = None # For solo
    group_age_min: Optional[int] = None # For group
    group_age_max: Optional[int] = None # For group
    
    transportation_mode: Optional[str] = "public" # public, car, walking
    budget: Optional[float] = None
    
    # Missing fields for Itinerary Agent
    accessibility_needs: Optional[str] = "None"
    location_scope: Optional[str] = "Domestic" # Domestic | International
    travel_pace: Optional[str] = "Moderate" # Relaxed | Moderate | Hectic
    interests: Optional[str] = "General sightseeing"

    weather_summary: Optional[str] = None
    weather_info: Optional[Dict[str, Any]] = None # Structured forecast
    accommodations: List[Dict[str, Any]] = []
    flights: List[Dict[str, Any]] = []
    recommended_hotels: List[Dict[str, Any]] = []
    
    # New SerpAPI Data
    top_sights: List[Dict[str, Any]] = []
    local_places: List[Dict[str, Any]] = []
    local_news: List[Dict[str, Any]] = []
    discussions: List[Dict[str, Any]] = []
    
    itinerary: Optional[str] = None
    messages: List[Any] = [] # For chat history
    
    # Personalization & Constraints
    user_preferences: List[str] = [] # From Mem0
    constraint_violations: List[str] = [] # Budget/Time issues
    
    # Analysis & Correction
    trip_analysis: Optional[str] = None
    retry_count: int = 0
    last_error: Optional[str] = None