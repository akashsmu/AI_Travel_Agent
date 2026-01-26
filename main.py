from dotenv import load_dotenv
load_dotenv()

from graph import build_graph
from state import TravelState


def main():
    print("=== AI Travel Agent (LangGraph Edition) ===")

    graph = build_graph()
    thread_id = "user_123"
    config = {"configurable": {"thread_id": thread_id}}
    
    # Initialize messages list to track history in state
    messages = []

    while True:
        print("\n--- New Request (type 'exit' to quit) ---")
        origin = input("Origin (e.g., BLR) [Enter for last]: ").strip()
        if origin.lower() == 'exit':
            break
            
        destination = input("Destination (e.g., Mumbai) [Enter for last]: ").strip()
        if destination.lower() == 'exit':
            break

        start_date = input("Start date (YYYY-MM-DD): ").strip()
        end_date = input("End date (YYYY-MM-DD): ").strip()

        bedrooms = input("Bedrooms (default 1): ").strip()
        bedrooms = int(bedrooms) if bedrooms else 1
        
        max_price = input("Max price per night (default 200): ").strip()
        max_price = float(max_price) if max_price else 200.0
        
        min_rating = input("Min rating (default 4.0): ").strip()
        min_rating = float(min_rating) if min_rating else 4.0

        # Create input state. 
        # Note: In multi-turn, we might want to preserve some previous state but override others.
        # LangGraph checkpointer handles merging.
        input_data = {
            "messages": messages + [f"Traveling from {origin} to {destination} on {start_date} to {end_date}"]
        }
        
        if origin: input_data["origin"] = origin
        if destination: input_data["destination"] = destination
        if start_date: input_data["start_date"] = start_date
        if end_date: input_data["end_date"] = end_date
        input_data["bedrooms"] = bedrooms
        input_data["max_price_per_night"] = max_price
        input_data["min_rating"] = min_rating

        final_state = graph.invoke(input_data, config=config)

        # Normalize to dict
        if hasattr(final_state, "model_dump"):
            final_state = final_state.model_dump()
        elif not isinstance(final_state, dict):
            final_state = vars(final_state)

        # Update local message tracker
        messages = final_state.get("messages", [])

        weather_summary = final_state.get("weather_summary")
        recommended_hotels = final_state.get("recommended_hotels", [])
        flights = final_state.get("flights", [])
        trip_analysis = final_state.get("trip_analysis")

        print("\n=== WEATHER ===")
        if weather_summary:
            print(weather_summary)
        else:
            print("No weather summary available.")

        print("\n=== TOP HOTELS ===")
        if recommended_hotels:
            for h in recommended_hotels:
                name = h.get("name")
                rating = h.get("rating")
                price = h.get("price") or h.get("price_per_night")
                url = h.get("url")

                try:
                    price_str = f"{float(price):.2f}" if price is not None else "N/A"
                except Exception:
                    price_str = "N/A"

                print(f"- {name} — ⭐ {rating} — {price_str} per night → {url}")
        else:
            print("No hotel recommendations found.")

        print("\n=== TOP FLIGHTS ===")
        if flights:
            for f in flights:
                airline = f.get("airline")
                origin_f = f.get("origin")
                dest_f = f.get("destination")
                price = f.get("price")
                url = f.get("url")
                print(f"- {airline} {origin_f} → {dest_f} — {price} → {url}")
        else:
            print("No flight options found.")

        if trip_analysis:
            print(f"\n=== AGENT NOTE ===\n{trip_analysis}")

    print("\n🎉 Done! Your LangGraph-powered travel planning run is complete.\n")


if __name__ == "__main__":
    main()