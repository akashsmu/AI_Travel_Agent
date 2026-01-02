
from agents.tools.serp_tools import search_google_hotels
from utils.logger import setup_logger

logger = setup_logger("search_agent")

def live_search(state):
    """
    Search for accommodations using SerpAPI (Google Hotels).
    """
    logger.info(f"🔎 Searching hotels for {state.destination}...")
    hotels = search_google_hotels(state.model_dump())
    
    if hotels:
        logger.info(f"✅ Found {len(hotels)} hotels from SerpAPI.")
        state.accommodations = hotels
    else:
        logger.warning("⚠️ No hotels found via SerpAPI.")
        state.accommodations = []

    return state