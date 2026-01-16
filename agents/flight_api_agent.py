
from agents.tools.serp_tools import search_google_flights
from utils.logger import setup_logger

logger = setup_logger("flight_agent")

def fetch_flights_from_api(state):
    """
    Fetch flights using SerpAPI (Google Flights).
    """
    logger.info(f"✈️ Searching flights from {state.origin} to {state.destination}...")
    flights = search_google_flights(state.model_dump())
    
    # Post-process with Mem0 Preferences
    if state.user_preferences and flights:
        preferred_airlines = [p.lower() for p in state.user_preferences if "airline" in p.lower() or "fly" in p.lower()]
        
        # Simple extraction of airline names from preferences (e.g., "I prefer Delta")
        # In a real agent, we'd use an LLM or stricter Memory structure. 
        
        target_keywords = []
        for p in state.user_preferences:
            if "delta" in p.lower(): target_keywords.append("Delta")
            if "united" in p.lower(): target_keywords.append("United")
            if "american" in p.lower(): target_keywords.append("American")
            if "lufthansa" in p.lower(): target_keywords.append("Lufthansa")
            if "british" in p.lower(): target_keywords.append("British")
            if "france" in p.lower(): target_keywords.append("France")
            if "emirates" in p.lower(): target_keywords.append("Emirates")
            
        if target_keywords:
            logger.info(f"✨ Filtering for preferred airlines: {target_keywords}")
            # Sort to put preferred airlines at top
            flights.sort(key=lambda x: any(k.lower() in x.get('airline', '').lower() for k in target_keywords), reverse=True)

    if flights:
        logger.info(f"✅ Found {len(flights)} flights from SerpAPI.")
        state.flights = flights
    else:
        logger.warning("⚠️ No flights found via SerpAPI.")
        state.flights = []
        
    return state