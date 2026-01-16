from langgraph.graph import StateGraph, END

from state import TravelState
from agents.weather_agent import fetch_weather
from agents.search_agent import live_search
from agents.recommend_agent import recommend_hotels
from agents.flights_agent import recommend_flights
from agents.flight_api_agent import fetch_flights_from_api
from agents.itinerary_agent import generate_itinerary
from database.ops import find_cached_trip as check_cache
from database.store_results import store_results


def route_cache(state):
    if state is None:
        return "live_search"

    if isinstance(state, dict):
        accommodations = state.get("accommodations") or []
        flights = state.get("flights") or []
    else:
        accommodations = getattr(state, "accommodations", []) or []
        flights = getattr(state, "flights", []) or []

    if accommodations and flights:
        return "recommend_hotels"
    return "live_search"


from agents.community_agent import fetch_community_data
from agents.constraint_agent import check_constraints
from agents.correction_agent import correction_node, should_correct
from agents.reasoning_agent import reasoning_node
from utils.memory import MemoryManager
from utils.logger import logger

def load_memories(state: TravelState) -> dict:
    mem_mgr = MemoryManager()
    user_id = "default_user" 
    try:
        prefs = mem_mgr.get_all_memories(user_id)
        logger.info(f"Loaded {len(prefs)} memories")
        return {"user_preferences": prefs}
    except Exception as e:
        logger.error(f"Error loading memories: {e}")
        return {"user_preferences": []}

def build_graph():
    graph = StateGraph(TravelState)

    graph.add_node("load_profile", load_memories) 
    graph.add_node("weather", fetch_weather)
    graph.add_node("cache", check_cache)
    graph.add_node("live_search", live_search)
    graph.add_node("flight_api", fetch_flights_from_api)
    graph.add_node("store", store_results)
    graph.add_node("recommend_hotels", recommend_hotels)
    graph.add_node("recommend_flights", recommend_flights)
    graph.add_node("check_constraints", check_constraints)
    graph.add_node("itinerary", generate_itinerary)
    graph.add_node("community_agent", fetch_community_data)
    
    # New Nodes
    graph.add_node("correction", correction_node)
    graph.add_node("reasoning", reasoning_node)

    graph.set_entry_point("load_profile") 

    graph.add_edge("load_profile", "weather")
    graph.add_edge("weather", "cache")

    graph.add_conditional_edges(
        "cache",
        route_cache,
        {
            "live_search": "live_search",
            "recommend_hotels": "recommend_hotels",
        },
    )

    # Cache miss path
    graph.add_edge("live_search", "flight_api")
    
    # Conditional Edge for Correction (After Flights)
    graph.add_conditional_edges(
        "flight_api",
        should_correct,
        {
            "correction": "correction",
            "continue": "community_agent"
        }
    )
    
    # Correction Loop
    graph.add_edge("correction", "live_search") # Restart search with new params

    graph.add_edge("community_agent", "store")
    graph.add_edge("store", "recommend_hotels")

    # Common path
    graph.add_edge("recommend_hotels", "recommend_flights")
    graph.add_edge("recommend_flights", "check_constraints") 
    graph.add_edge("check_constraints", "itinerary")
    graph.add_edge("itinerary", "reasoning") # UPDATED
    graph.add_edge("reasoning", END)         # UPDATED

    return graph.compile()