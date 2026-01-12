
from agents.tools.serp_tools import (
    search_google_sights, 
    search_google_local, 
    search_google_news, 
    search_google_discussions
)
from utils.logger import setup_logger

logger = setup_logger("community_agent")

def fetch_community_data(state):
    """
    Fetch Sights, Local Gems, News, and Discussions in parallel (conceptually, blocking here for simplicity).
    """
    location = state.destination_city or state.destination or ""
    if not location:
        logger.warning("⚠️ No destination found for community search.")
        return state

    logger.info(f"🏘️ Fetching community data for: {location}")

    # 1. Top Sights
    try:
        state.top_sights = search_google_sights(location)
        logger.info(f"✅ Found {len(state.top_sights)} sights.")
    except Exception as e:
        logger.error(f"Failed sights search: {e}")

    # 2. Local Gems
    try:
        state.local_places = search_google_local(location)
        logger.info(f"✅ Found {len(state.local_places)} local gems.")
    except Exception as e:
        logger.error(f"Failed local search: {e}")

    # 3. Local News
    try:
        state.local_news = search_google_news(f"latest news in {location}")
        logger.info(f"✅ Found {len(state.local_news)} news items.")
    except Exception as e:
        logger.error(f"Failed news search: {e}")

    # 4. Discussions
    try:
        state.discussions = search_google_discussions(location)
        logger.info(f"✅ Found {len(state.discussions)} discussions.")
    except Exception as e:
        logger.error(f"Failed discussion search: {e}")

    return state
