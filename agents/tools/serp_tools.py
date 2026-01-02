
import os
from serpapi import GoogleSearch

def search_google_flights(full_state):
    """
    Search for flights using SerpAPI Google Flights engine.
    """
    if not os.getenv("SERPAPI_API_KEY"):
        print("SERPAPI_API_KEY not found")
        return []

    params = {
        "engine": "google_flights",
        "departure_id": full_state.get("origin", ""),
        "arrival_id": full_state.get("destination", ""),
        "outbound_date": full_state.get("start_date", ""),
        "return_date": full_state.get("end_date", ""),
        "currency": "USD",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }
    
    # Basic validation
    if not params["departure_id"] or not params["arrival_id"]:
        return []

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        flights = []
        if "best_flights" in results:
            for flight in results["best_flights"]:
                flights.append({
                    "airline": flight["flights"][0]["airline"],
                    "origin": params["departure_id"],
                    "destination": params["arrival_id"],
                    "price": flight.get("price", 0),
                    "url": "https://www.google.com/travel/flights", # SerpAPI doesn't always give direct partial deep links easily, but let's check
                    "details": flight
                })
        # If best_flights empty, try other_flights
        if not flights and "other_flights" in results:
             for flight in results["other_flights"]:
                flights.append({
                    "airline": flight["flights"][0]["airline"],
                    "origin": params["departure_id"],
                    "destination": params["arrival_id"],
                    "price": flight.get("price", 0),
                    "url": "https://www.google.com/travel/flights", 
                    "details": flight
                })
                
        return flights[:5] # Return top 5
    except Exception as e:
        print(f"SerpAPI Flights Error: {e}")
        return []

def search_google_hotels(full_state):
    """
    Search for hotels using SerpAPI Google Hotels engine.
    """
    if not os.getenv("SERPAPI_API_KEY"):
        print("SERPAPI_API_KEY not found")
        return []

    params = {
        "engine": "google_hotels",
        "q": f"hotels in {full_state.get('destination', '')}",
        "check_in_date": full_state.get("start_date", ""),
        "check_out_date": full_state.get("end_date", ""),
        "adults": "1",
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_API_KEY")
    }

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
