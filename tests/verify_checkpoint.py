import os
from dotenv import load_dotenv
load_dotenv()

from graph import build_graph
from state import TravelState

def test_checkpointer_persistence():
    print("Testing LangGraph Checkpointer Persistence...")
    graph = build_graph()
    config = {"configurable": {"thread_id": "test_thread_1"}}
    
    # 1. First invocation: Set some state
    initial_input = {
        "origin": "NYC",
        "destination": "London",
        "messages": ["I want to go to London"]
    }
    print("Inhoking graph for the first time...")
    state1 = graph.invoke(initial_input, config=config)
    
    # Check if messages were updated
    messages1 = state1.get("messages", []) if isinstance(state1, dict) else state1.messages
    print(f"Messages after run 1: {len(messages1)}")
    
    # 2. Second invocation: Check if state is preserved
    print("Inhoking graph for the second time with same thread_id...")
    # We send minimal input, checkpointer should provide the rest
    second_input = {
        "messages": ["And also I need a hotel"]
    }
    state2 = graph.invoke(second_input, config=config)
    
    messages2 = state2.get("messages", []) if isinstance(state2, dict) else state2.messages
    print(f"Messages after run 2: {len(messages2)}")
    
    # Verification
    if len(messages2) > len(messages1):
        print("✅ SUCCESS: Checkpointer preserved message history.")
    else:
        print("❌ FAILURE: Checkpointer did not preserve message history.")

    if state2.get("origin") == "NYC" or getattr(state2, "origin", "") == "NYC":
        print("✅ SUCCESS: Checkpointer preserved 'origin' state.")
    else:
        print(f"❌ FAILURE: Checkpointer lost 'origin' state. Found: {state2.get('origin')}")

if __name__ == "__main__":
    test_checkpointer_persistence()
