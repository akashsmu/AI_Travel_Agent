import os
import json
from typing import List, Dict, Any
from serpapi import GoogleSearch
from dotenv import load_dotenv
from utils.logger import setup_logger

load_dotenv()
logger = setup_logger()
from utils.retry import with_retry

@with_retry(max_retries=3, backoff_factor=2)
def search_google_flights(full_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search for flights using SerpAPI Google Flights engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        logger.error("SERPAPI_KEY not found in environment")
        return []

    # Determine trip type: 1 = Round Trip, 2 = One Way
    trip_type = 1
    return_date = full_state.get("end_date", "")
    if not return_date:
        trip_type = 2

    # CRITICAL: Use ID (e.g. SFO, /m/0vzm) for flights if available, else name
    dep_id = full_state.get("origin_id") or full_state.get("origin", "")
    arr_id = full_state.get("destination_id") or full_state.get("destination", "")

    # If valid ID format (3 chars uppercase or starts with /m/), use it.
    # Otherwise, try to resolve it via autocomplete.
    def is_valid_id(val):
        return val and ((len(val) == 3 and val.isupper()) or val.startswith("/m/"))

    if dep_id and not is_valid_id(dep_id):
        logger.warning(f"⚠️ Invalid Departure ID '{dep_id}'. Attempting resolution...")
        suggestions = search_google_flights_autocomplete(dep_id)
        if suggestions:
            new_id = suggestions[0].get("id")
            logger.info(f"✅ Resolved '{dep_id}' -> '{new_id}'")
            dep_id = new_id
    
    if arr_id and not is_valid_id(arr_id):
        logger.warning(f"⚠️ Invalid Arrival ID '{arr_id}'. Attempting resolution...")
        suggestions = search_google_flights_autocomplete(arr_id)
        if suggestions:
            new_id = suggestions[0].get("id")
            logger.info(f"✅ Resolved '{arr_id}' -> '{new_id}'")
            arr_id = new_id

    params = {
        "engine": "google_flights",
        "departure_id": dep_id,
        "arrival_id": arr_id,
        "outbound_date": full_state.get("start_date", ""),
        "return_date": return_date,
        "type": str(trip_type), 
        "currency": "USD",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    #logger.info(f"✈️ FLIGHT SEARCH PARAMS: {params}")

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # EXTENSIVE LOGGING
        #logger.info(f"✈️ RAW FLIGHT RESULTS: {json.dumps(results, indent=2)}")

        if "error" in results:
            logger.error(f"SerpAPI Flights Error: {results['error']}")
            return []

        search_url = results.get("search_metadata", {}).get("google_flights_url", "https://www.google.com/travel/flights")
        flights_data = []
        
        def process_flight_list(key, f_type):
            if key in results:
                for flight in results[key]:
                    first_slice = flight.get("flights", [{}])[0]
                    
                    # Extract departure and arrival details
                    dep_airport = first_slice.get("departure_airport", {})
                    arr_airport = first_slice.get("arrival_airport", {})
                    
                    flights_data.append({
                        "airline": first_slice.get("airline", "Unknown"),
                        "airline_logo": first_slice.get("airline_logo"),
                        "flight_number": first_slice.get("flight_number"),
                        "airplane": first_slice.get("airplane"),
                        "travel_class": first_slice.get("travel_class"),
                        
                        # Airport codes (ID)
                        "origin": dep_id,
                        "destination": arr_id,
                        
                        # Airport full names
                        "origin_name": dep_airport.get("name"),
                        "destination_name": arr_airport.get("name"),
                        
                        # Times
                        "departure_time": dep_airport.get("time"),
                        "arrival_time": arr_airport.get("time"),
                        
                        # Airport IDs from actual flight data
                        "departure_airport_id": dep_airport.get("id"),
                        "arrival_airport_id": arr_airport.get("id"),
                        
                        "price": flight.get("price", 0),
                        "duration": flight.get("total_duration", "N/A"),
                        "stops": "Nonstop" if len(flight.get("layovers", [])) == 0 else f"{len(flight.get('layovers', []))} stops",
                        "layovers": flight.get("layovers", []),
                        "extensions": flight.get("extensions", []),
                        "carbon_emissions": flight.get("carbon_emissions", {}),
                        "url": search_url,
                        "type": f_type,
                        "details": flight 
                    })

        process_flight_list("best_flights", "Best")
        process_flight_list("other_flights", "Other")
        
        return flights_data
    except Exception as e:
        logger.error(f"❌ SerpAPI Flights Exception: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_flights_autocomplete(query: str) -> List[Dict[str, Any]]:
    """
    Autocomplete for airports using SerpAPI.
    """
    if not os.getenv("SERPAPI_KEY"):
        return []

    params = {
        "engine": "google_flights_autocomplete",
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()


        suggestions = []
        if "suggestions" in results:
            for item in results["suggestions"]:
                 # Top level (City or Region)
                 raw_id = item.get("id", "")
                 raw_name = item.get("name", "")
                 display_code = raw_id if len(raw_id) == 3 and raw_id.isupper() else None
                 
                 suggestions.append({
                     "id": raw_id, 
                     "name": raw_name,
                     "city_name": raw_name, # Current item is the city
                     "code": display_code,
                     "type": "City"
                 })
                 
                 # Nested airports
                 if "airports" in item:
                     for airport in item["airports"]:
                         air_id = airport.get("id", "")
                         suggestions.append({
                             "id": air_id,
                             "name": f"{airport.get('name')} ({air_id})",
                             "city_name": airport.get("city"),
                             "code": air_id,
                             "type": "Airport"
                         })

        return suggestions[:10]
    except Exception as e:
        logger.error(f"SerpAPI Autocomplete Error: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_hotels(full_state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Search for hotels using SerpAPI Google Hotels engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        return []

    # Use City Name (e.g. Austin) for Hotels if available, else destination
    dest_query = full_state.get("destination_city") or full_state.get("destination", "")
    
    params = {
        "engine": "google_hotels",
        "q": f"hotels in {dest_query}",
        "check_in_date": full_state.get("start_date", ""),
        "check_out_date": full_state.get("end_date", ""),
        "adults": "1",
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    #logger.info(f"🏨 HOTEL SEARCH PARAMS: {params}")

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # EXTENSIVE LOGGING
        #logger.info(f"🏨 RAW HOTEL RESULTS: {json.dumps(results, indent=2)}")

        if "error" in results:
            logger.error(f"SerpAPI Hotels Error: {results['error']}")
            return []
        
        hotels = []
        if "properties" in results:
            for prop in results["properties"]:
                price_val = 0
                if prop.get("rate_per_night") and "lowest" in prop["rate_per_night"]:
                    price_str = prop["rate_per_night"]["lowest"]
                    price_val = float(price_str.replace('$', '').replace(',', ''))
                
                hotels.append({
                    "name": prop.get("name"),
                    "city": dest_query,
                    "country": "", 
                    "price": price_val,
                    "rating": prop.get("overall_rating", 0.0),
                    "url": prop.get("link"),
                    "image": prop.get("images", [{}])[0].get("thumbnail") if prop.get("images") else None,
                    "description": prop.get("description")
                })
        
        return hotels[:10]
    except Exception as e:
        logger.error(f"❌ SerpAPI Hotels Exception: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_sights(location: str) -> List[Dict[str, Any]]:
    """
    Search for top sights using Google Search (or specialized engine if available).
    """
    if not os.getenv("SERPAPI_KEY"):
        return []

    params = {
        "engine": "google", # Using standard google search for broad coverage, or google_local
        "q": f"top sights in {location}",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        sights = []
        # Attempt to parse knowledge graph or organic results
        if "knowledge_graph" in results:
             kg = results["knowledge_graph"]
             if "title" in kg:
                 sights.append({
                     "title": kg.get("title"),
                     "type": kg.get("type"),
                     "description": kg.get("description"),
                     "image": kg.get("header_images", [{}])[0].get("image") if kg.get("header_images") else None
                 })
        
        # Parse 'Top Sights' carousel if available
        if "top_sights" in results:
             for sight in results["top_sights"].get("sights", []):
                 sights.append({
                     "title": sight.get("title"),
                     "description": sight.get("description"),
                     "price": sight.get("price"),
                     "rating": sight.get("rating"),
                     "reviews": sight.get("reviews"),
                     "image": sight.get("thumbnail")
                 })

        return sights[:10]
    except Exception as e:
        logger.error(f"❌ SerpAPI Sights Exception: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_local(location: str) -> List[Dict[str, Any]]:
    """
    Search for local gems (restaurants/attractions) using Google Local.
    """
    if not os.getenv("SERPAPI_KEY"):
        return []

    params = {
        "engine": "google_local",
        "q": f"places to visit in {location}", # Broad query
        "location": location,
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        places = []
        if "local_results" in results:
            for place in results["local_results"]:
                places.append({
                    "title": place.get("title"),
                    "rating": place.get("rating"),
                    "reviews": place.get("reviews"),
                    "type": place.get("type"),
                    "address": place.get("address"),
                    "thumbnail": place.get("thumbnail"),
                    "description": place.get("description") # Sometimes available
                })
        return places[:10]
    except Exception as e:
        logger.error(f"❌ SerpAPI Local Exception: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_news(location: str) -> List[Dict[str, Any]]:
    """
    Search for local news using Google News engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        return []

    params = {
        "engine": "google_news",
        "q": location,
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        news_items = []
        if "news_results" in results:
            for item in results["news_results"]:
                news_items.append({
                    "title": item.get("title"),
                    "source": item.get("source", {}).get("title"),
                    "date": item.get("date"),
                    "snippet": item.get("snippet"),
                    "image": item.get("thumbnail"),
                    "link": item.get("link")
                })
        return news_items[:5]
    except Exception as e:
        logger.error(f"❌ SerpAPI News Exception: {e}")
        return []

@with_retry(max_retries=3, backoff_factor=2)
def search_google_discussions(location: str) -> List[Dict[str, Any]]:
    """
    Search for forum discussions (Reddit, TripAdvisor, etc.).
    """
    if not os.getenv("SERPAPI_KEY"):
        return []
    
    # We use standard google search with "Discussions" filter logic or specific site queries
    # A reliable way is checking 'discussions_and_forums' block in standard search
    
    params = {
        "engine": "google",
        "q": f"{location} travel tips forum",
        "google_domain": "google.com",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        discussions = []
        if "discussions_and_forums" in results:
            for item in results["discussions_and_forums"]:
                 discussions.append({
                     "title": item.get("title"),
                     "source": item.get("source"),
                     "link": item.get("link"),
                     "date": item.get("date"),
                     "snippet": item.get("snippet")
                 })
                 
        # Fallback to organic results if they look like forums
        if not discussions and "organic_results" in results:
             for item in results["organic_results"]:
                 link = item.get("link", "")
                 if "reddit.com" in link or "tripadvisor.com" in link or "lonelyplanet.com" in link:
                     discussions.append({
                         "title": item.get("title"),
                         "source": item.get("source") or item.get("displayed_link"),
                         "link": link,
                         "snippet": item.get("snippet")
                     })

        return discussions[:5]
    except Exception as e:
        logger.error(f"❌ SerpAPI Discussions Exception: {e}")
        return []
