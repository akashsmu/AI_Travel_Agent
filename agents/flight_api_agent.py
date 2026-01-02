
from agents.tools.serp_tools import search_google_flights
from utils.logger import setup_logger

logger = setup_logger("flight_agent")

def fetch_flights_from_api(state):
    """
    Fetch flights using SerpAPI (Google Flights).
    """
    logger.info(f"✈️ Searching flights from {state.origin} to {state.destination}...")
    flights = search_google_flights(state.model_dump())
    
    if flights:
        logger.info(f"✅ Found {len(flights)} flights from SerpAPI.")
        state.flights = flights
    else:
        logger.warning("⚠️ No flights found via SerpAPI.")
        state.flights = []
        
    return state