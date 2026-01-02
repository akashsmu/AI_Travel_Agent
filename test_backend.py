
import os
import sys

# Ensure current dir is in path
sys.path.append(os.getcwd())

from graph import build_graph
from state import TravelState
from dotenv import load_dotenv

load_dotenv()

print(f"📂 Current working directory: {os.getcwd()}")
print(f"📄 .env exists: {os.path.exists('.env')}")
if os.path.exists('.env'):
    print("Trying to read .env first line...")
    with open('.env', 'r') as f:
         print(f"First line: {f.readline()}")

def test_graph():
    print("🚀 Starting Backend Test...")
    
    # Check keys
    if not os.getenv("SERPAPI_API_KEY"):
        print("❌ SERPAPI_API_KEY missing in .env")
        return
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY missing in .env")
        return
        
    print("✅ Keys found.")
    
    graph = build_graph()
    
    print("🌍 Invoking graph with test data (San Francisco -> New York)...")
    initial_state = TravelState(
        origin="San Francisco",
        destination="New York",
        start_date="2024-05-10",
        end_date="2024-05-15",
        bedrooms=1,
        max_price_per_night=300,
        min_rating=4.0
    )
    
    try:
        final_state = graph.invoke(initial_state)
        
        print("\n✅ Graph Result:")
        if final_state.get("accommodations"):
            print(f"   - Hotels found: {len(final_state['accommodations'])}")
            print(f"     Example: {final_state['accommodations'][0]['name']}")
        else:
            print("   - No hotels found.")
            
        if final_state.get("flights"):
            print(f"   - Flights found: {len(final_state['flights'])}")
            print(f"     Example: {final_state['flights'][0]['airline']}")
        else:
            print("   - No flights found.")
            
        if final_state.get("itinerary"):
            print("   - Itinerary generated!")
            print("   --- Snippet ---")
            print(str(final_state['itinerary'])[:200] + "...")
        else:
            print("   - No itinerary generated.")
            
    except Exception as e:
        print(f"❌ Graph execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_graph()
