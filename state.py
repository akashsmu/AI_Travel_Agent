from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TravelState(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

    bedrooms: Optional[int] = 1
    max_price_per_night: Optional[float] = 200.0
    min_rating: Optional[float] = 4.0
    max_flight_price: Optional[float] = None
    
    # Trip parameters
    trip_purpose: Optional[str] = "vacation"  # vacation or work
    travel_party: Optional[str] = "solo_male"  # solo_male, solo_female, or group
    budget: Optional[float] = None  # Total budget

    weather_summary: Optional[str] = None
    accommodations: List[Dict[str, Any]] = []
    flights: List[Dict[str, Any]] = []
    recommended_hotels: List[Dict[str, Any]] = []
    
    itinerary: Optional[str] = None
    messages: List[Any] = [] # For chat history