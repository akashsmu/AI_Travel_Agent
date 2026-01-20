
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
    Fetch Sights, Local Gems, News, and Discussions and format as Dynamic Widgets.
    """
    location = state.destination_city or state.destination or ""
    if not location:
        logger.warning("⚠️ No destination found for community search.")
        return state

    logger.info(f"🏘️ Fetching community data for: {location}")
    
    widgets = []

    # 1. Top Sights -> Place Cards
    try:
        sights = search_google_sights(location)
        state.top_sights = sights
        # Convert first 3 to widgets
        for sight in sights[:3]:
            widgets.append({
                "type": "place_card",
                "priority": 10,
                "data": {
                    "name": sight.get("title") or sight.get("name"),
                    "type": "Sightseeing",
                    "rating": sight.get("rating"),
                    "reviews": sight.get("reviews"),
                    "address": sight.get("address"),
                    "thumbnail": sight.get("thumbnail")
                }
            })
    except Exception as e:
        logger.error(f"Failed sights search: {e}")

    # 2. Local Gems -> Place Cards
    try:
        gems = search_google_local(location)
        state.local_places = gems
        for gem in gems[:3]:
             widgets.append({
                "type": "place_card",
                "priority": 8,
                "data": {
                    "name": gem.get("title"),
                    "type": "Local Gem",
                    "rating": gem.get("rating"),
                    "thumbnail": gem.get("thumbnail")
                }
            })
    except Exception as e:
        logger.error(f"Failed local search: {e}")

    # 3. Local News -> News Widgets
    try:
        news_items = search_google_news(f"latest travel news {location}")
        state.local_news = news_items
        for news in news_items[:3]:
             widgets.append({
                "type": "news_card",
                "priority": 5,
                "data": {
                    "title": news.get("title"),
                    "snippet": news.get("snippet"),
                    "link": news.get("link"),
                    "source": news.get("source"),
                    "date": news.get("date"),
                    "thumbnail": news.get("thumbnail")
                }
            })
    except Exception as e:
        logger.error(f"Failed news search: {e}")

    # 4. Discussions (not widgetized yet, but stored)
    try:
        state.discussions = search_google_discussions(location)
    except Exception as e:
        logger.error(f"Failed discussion search: {e}")
        
    # Sort widgets by priority
    widgets.sort(key=lambda x: x["priority"], reverse=True)
    state.generated_ui = widgets
    
    logger.info(f"✅ Generated {len(widgets)} UI widgets.")

    return state
