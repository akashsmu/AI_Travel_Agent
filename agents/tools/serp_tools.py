
import os
from serpapi import GoogleSearch
from dotenv import load_dotenv


load_dotenv()

def search_google_flights(full_state):
    """
    Search for flights using SerpAPI Google Flights engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        print("SERPAPI_KEY not found")
        return []

    # Determine trip type: 1 = Round Trip, 2 = One Way
    trip_type = 1
    return_date = full_state.get("end_date", "")
    if not return_date:
        trip_type = 2

    # CRITICAL: Use ID (e.g. SFO, /m/0vzm) for flights if available, else Name
    dep_id = full_state.get("origin_id") or full_state.get("origin", "")
    arr_id = full_state.get("destination_id") or full_state.get("destination", "")

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
    
    print(f"✈️ FLIGHT PARAMS: {params}") # Log inputs

    # Basic validation
    if not params["departure_id"] or not params["arrival_id"]:
        print("❌ Missing flight params")
        return []

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # ... processing logic ...
        
    except Exception as e:
        print(f"SerpAPI Flights Error: {e}")
        return []

def search_google_flights_autocomplete(query):
    """
    Autocomplete for airports using SerpAPI Google Flights Autocomplete engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        print("SERPAPI_KEY not found")
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
                 # Only use ID as 'code' if it looks like an IATA code (3 chars), else fallback to Name for display
                 raw_id = item.get("id", "")
                 display_code = raw_id if len(raw_id) == 3 and raw_id.isupper() else None
                 
                 suggestions.append({
                     "id": raw_id, 
                     "name": item.get("name"),
                     "code": display_code,
                     "type": "City"
                 })
                 
                 # Nested airports
                 if "airports" in item:
                     for airport in item["airports"]:
                         air_id = airport.get("id", "")
                         suggestions.append({
                             "id": air_id, # e.g. "JFK"
                             "name": f"{airport.get('name')} ({air_id})",
                             "code": air_id,
                             "type": "Airport"
                         })
                         
        return suggestions[:10]
    except Exception as e:
        print(f"SerpAPI Autocomplete Error: {e}")
        return []

def search_google_hotels(full_state):
    """
    Search for hotels using SerpAPI Google Hotels engine.
    """
    if not os.getenv("SERPAPI_KEY"):
        print("SERPAPI_KEY not found")
        return []

    # CRITICAL: Use Name (e.g. Austin, TX) for Hotels, NOT ID
    # Frontend sends Name in "destination" and ID in "destination_id"
    dest_query = full_state.get("destination", "")
    
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
    
    print(f"🏨 HOTEL PARAMS: {params}") # Log inputs

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        hotels = []
        if "properties" in results:
            for prop in results["properties"]:
                # Filter by simple constraints if possible, or just return top
                price_val = 0
                if prop.get("rate_per_night") and "lowest" in prop["rate_per_night"]:
                    price_str = prop["rate_per_night"]["lowest"]
                    # Clean string "$120" -> 120
                    price_val = float(price_str.replace('$', '').replace(',', ''))
                
                rating = prop.get("overall_rating", 0.0)

                hotels.append({
                    "name": prop.get("name"),
                    "city": full_state.get("destination"),
                    "country": "", # SerpAPI doesn't always explicit this in list
                    "price": price_val,
                    "rating": rating,
                    "url": prop.get("link"),
                    "image": prop.get("images", [{}])[0].get("thumbnail") if prop.get("images") else None,
                    "description": prop.get("description")
                })
        
        return hotels[:10]
    except Exception as e:
        print(f"SerpAPI Hotels Error: {e}")
        return []
