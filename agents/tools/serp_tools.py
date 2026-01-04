
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

    params = {
        "engine": "google_flights",
        "departure_id": full_state.get("origin", ""),
        "arrival_id": full_state.get("destination", ""),
        "outbound_date": full_state.get("start_date", ""),
        "return_date": return_date,
        "type": str(trip_type), 
        "currency": "USD",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
    }
    
    # Basic validation
    if not params["departure_id"] or not params["arrival_id"]:
        return []

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # General Google Flights URL for the user to view more
        search_url = results.get("search_metadata", {}).get("google_flights_url", "https://www.google.com/travel/flights")

        flights_data = {
            "best_flights": [],
            "other_flights": []
        }
        
        # Helper to process flight list
        def process_flight_list(key, target_list):
            if key in results:
                for flight in results[key]:
                    # Extract first leg details for main display
                    first_slice = flight.get("flights", [{}])[0]
                    airline = first_slice.get("airline", "Unknown Airline")
                    logo = first_slice.get("airline_logo")
                    flight_number = first_slice.get("flight_number")
                    airplane = first_slice.get("airplane")
                    travel_class = first_slice.get("travel_class")
                    
                    # Extensions often contain legroom, etc.
                    extensions = flight.get("extensions", [])
                    
                    target_list.append({
                        "airline": airline,
                        "airline_logo": logo,
                        "flight_number": flight_number,
                        "airplane": airplane,
                        "travel_class": travel_class,
                        "origin": params["departure_id"],
                        "destination": params["arrival_id"],
                        "price": flight.get("price", 0),
                        "duration": flight.get("total_duration", "N/A"),
                        "stops": "Nonstop" if len(flight.get("layovers", [])) == 0 else f"{len(flight.get('layovers', []))} stops",
                        "layovers": flight.get("layovers", []), # List of layovers if any
                        "extensions": extensions,
                        "url": search_url, 
                        "type": "Best" if key == "best_flights" else "Other",
                        "details": flight 
                    })

        process_flight_list("best_flights", flights_data["best_flights"])
        process_flight_list("other_flights", flights_data["other_flights"])
        
        # Return a flat list sorted by best first, but marked with type
        # Or return detailed dict if state supports it. 
        # For compatibility with current state.flights (List), we concatenate but keep metadata
        return flights_data["best_flights"] + flights_data["other_flights"]
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

    params = {
        "engine": "google_hotels",
        "q": f"hotels in {full_state.get('destination', '')}",
        "check_in_date": full_state.get("start_date", ""),
        "check_out_date": full_state.get("end_date", ""),
        "adults": "1",
        "currency": "USD",
        "gl": "us",
        "hl": "en",
        "api_key": os.getenv("SERPAPI_KEY")
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
