
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import uvicorn
import asyncio
import json

# Import the graph
from graph import build_graph
from state import TravelState
from database.init_db import init_db
from agents.tools.serp_tools import search_google_flights_autocomplete
from utils.logger import setup_logger

logger = setup_logger()

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Run database initialization on startup."""
    try:
        logger.info("Starting up AI Travel Agent Server...")
        init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print(f"❌ Database initialization failed: {e}")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()

class ChatRequest(BaseModel):
    origin_id: Optional[str] = None
    destination_id: Optional[str] = None
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    start_date: str
    end_date: str
    bedrooms: Optional[int] = 1
    max_price: Optional[float] = 200.0
    min_rating: Optional[float] = 4.0
    trip_purpose: Optional[str] = "vacation"
    travel_party: Optional[str] = "solo"
    traveler_age: Optional[int] = None
    group_age_min: Optional[int] = None
    group_age_max: Optional[int] = None
    transportation_mode: Optional[str] = "public"
    budget: Optional[float] = None

@app.get("/autocomplete")
async def autocomplete(query: str):
    """
    Autocomplete airport search.
    """
    if not query:
        return []
    
    # Run in thread pool to avoid blocking
    results = await asyncio.to_thread(search_google_flights_autocomplete, query)
    return results

@app.post("/plan")
async def plan_trip(req: ChatRequest):
    """
    Standard HTTP endpoint to run the full graph and return final state.
    """
    initial_state = TravelState(
        origin=req.origin,
        destination=req.destination,
        origin_id=req.origin_id,
        destination_id=req.destination_id,
        origin_city=req.origin_city,
        destination_city=req.destination_city,
        start_date=req.start_date,
        end_date=req.end_date,
        bedrooms=req.bedrooms,
        max_price_per_night=req.max_price,
        min_rating=req.min_rating,
        trip_purpose=req.trip_purpose,
        travel_party=req.travel_party,
        traveler_age=req.traveler_age,
        group_age_min=req.group_age_min,
        group_age_max=req.group_age_max,
        transportation_mode=req.transportation_mode,
        budget=req.budget
    )
    
    try:
        final_state = await asyncio.to_thread(graph.invoke, initial_state)
        # Convert to dict for JSON response
        if isinstance(final_state, TravelState):
            return final_state.model_dump()
        return final_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from database.ops import save_trip_plan, find_cached_trip

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        data = await websocket.receive_text()
        req_data = json.loads(data)
        
        # 1. CHECK CACHE logic
        cache_params = {
            "origin": req_data.get("origin"),
            "destination": req_data.get("destination"),
            "start_date": req_data.get("start_date"),
            "end_date": req_data.get("end_date"),
            "trip_purpose": req_data.get("trip_purpose")
        }
        
        cached_result = await asyncio.to_thread(find_cached_trip, cache_params)
        
        if cached_result:
            # CACHE HIT: Send immediately
            logger.info("⚡️ Serving from cache")
            await websocket.send_text(json.dumps({
                "type": "update", 
                "step": "cache",
                "message": "⚡️ Found a recent matching itinerary! Loading from cache..."
            }))
            
            # Simulate a small delay for UX
            await asyncio.sleep(0.5)

            await websocket.send_text(json.dumps({
                "type": "complete",
                "message": "Planning complete (Cached)!",
                "data": cached_result
            }))
            return 
        
        # 2. NO CACHE: Run Agents
        logger.info(f"🚀 Starting plan for: {req_data.get('origin')} -> {req_data.get('destination')}")
        
        initial_state = TravelState(
            origin=req_data.get("origin"),
            destination=req_data.get("destination"),
            origin_id=req_data.get("origin_id"),
            destination_id=req_data.get("destination_id"),
            origin_city=req_data.get("origin_city"),
            destination_city=req_data.get("destination_city"),
            start_date=req_data.get("start_date"),
            end_date=req_data.get("end_date"),
            bedrooms=req_data.get("bedrooms", 1),
            max_price_per_night=req_data.get("max_price", 200.0),
            min_rating=req_data.get("min_rating", 4.0),
            trip_purpose=req_data.get("trip_purpose", "vacation"),
            travel_party=req_data.get("travel_party", "solo"),
            traveler_age=req_data.get("traveler_age"),
            group_age_min=req_data.get("group_age_min"),
            group_age_max=req_data.get("group_age_max"),
            transportation_mode=req_data.get("transportation_mode", "public"),
            budget=req_data.get("budget"),
        )
        
        await websocket.send_text(json.dumps({"type": "status", "message": "Starting travel planning..."}))
        
        # Keep track of the final state to send at the end
        final_state_data = {}
        # Also keep a real TravelState obj if possible, or construct one at end for saving
        # Since we are iterating events, we update `final_state_data` dictionary.
        
        # We need the accumulation of state because streaming gives partial updates.
        # Ideally, we should get the full state at the end.
        
        async for event in graph.astream(initial_state):
             for key, value in event.items():
                if key == "__end__":
                    continue
                
                # Update our tracking of the state (dict merge)
                if isinstance(value, dict):
                    final_state_data.update(value)
                elif hasattr(value, "dict"): 
                     final_state_data.update(value.dict())
                
                # Send update to client with partial data
                await websocket.send_text(json.dumps({
                    "type": "update",
                    "step": key,
                    "message": f"Completed {key}",
                    "data": final_state_data  # Send accumulated state
                }))
        
        # 3. SAVE to DB
        # Re-construct TravelState from accumulated dict to safely pass to save_trip_plan
        # (save_trip_plan expects TravelState object)
        try:
             # Merge initial params with results
             full_state_dict = initial_state.dict()
             full_state_dict.update(final_state_data)
             final_state_obj = TravelState(**full_state_dict)
             
             await asyncio.to_thread(save_trip_plan, final_state_obj)
        except Exception as save_err:
             logger.error(f"Failed to save plan: {save_err}")

        # Send complete message with full final data for rendering
        await websocket.send_text(json.dumps({
            "type": "complete", 
            "message": "Planning complete!",
            "data": final_state_data
        }))

        # 4. CHAT LOOP for Refinement
        while True:
            try:
                msg_text = await websocket.receive_text()
                msg_json = json.loads(msg_text)
                
                if msg_json.get("type") == "user_feedback":
                    user_msg = msg_json.get("message")
                    logger.info(f"💬 Received feedback: {user_msg}")
                    
                    await websocket.send_text(json.dumps({"type": "status", "message": "Refining your plan..."}))

                    # 1. Access current state (reconstruct from final_state_data + initial)
                    # We need to make sure 'final_state_data' has the latest values
                    current_full_dict = initial_state.dict()
                    current_full_dict.update(final_state_data)
                    current_state_obj = TravelState(**current_full_dict)

                    # 2. Run Modifier
                    from agents.modifier_agent import modify_state
                    new_state, updates = await asyncio.to_thread(modify_state, current_state_obj, user_msg)
                    
                    # Update local tracking
                    final_state_data.update(new_state.dict())
                    initial_state = new_state # Update baseline for next loop
                    
                    # 3. Conditional Re-runs
                    # If rerun_hotels -> Run hotels THEN itinerary
                    # If rerun_itinerary -> Run itinerary only
                    
                    rerun_hotels = updates.get("rerun_hotels")
                    rerun_itinerary = updates.get("rerun_itinerary")
                    
                    if rerun_hotels:
                        logger.info("🏨 Re-running Hotel Recommendations...")
                        await websocket.send_text(json.dumps({"type": "update", "step": "recommend_hotels", "message": "Finding new hotels..."}))
                        
                        # Invoke Agent Directly
                        hotel_result = await asyncio.to_thread(recommend_hotels, new_state)
                        # Update state
                        if "accommodations" in hotel_result:
                            new_state.accommodations = hotel_result["accommodations"]
                            final_state_data["accommodations"] = hotel_result["accommodations"]
                            
                        # Send Partial Update
                        await websocket.send_text(json.dumps({
                            "type": "update", "step": "recommend_hotels", "message": "Hotels updated!", "data": final_state_data
                        }))
                        
                        # Force Itinerary update if hotels changed
                        rerun_itinerary = True

                    if rerun_itinerary:
                        logger.info("📝 Re-generating Itinerary...")
                        await websocket.send_text(json.dumps({"type": "update", "step": "itinerary", "message": "Updating itinerary..."}))
                        
                        itin_result = await asyncio.to_thread(generate_itinerary, new_state)
                        if "itinerary" in itin_result:
                            new_state.itinerary = itin_result["itinerary"]
                            final_state_data["itinerary"] = itin_result["itinerary"]
                            
                        await websocket.send_text(json.dumps({
                            "type": "update", "step": "itinerary", "message": "Itinerary updated!", "data": final_state_data
                        }))

                    # Save updated plan
                    # await asyncio.to_thread(save_trip_plan, new_state) # Optional: save every refinement

                    await websocket.send_text(json.dumps({
                        "type": "complete", "message": "Plan updated!", "data": final_state_data
                    }))

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Chat Loop Error: {e}")
                break

        
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected (Normal)")
    except Exception as e:
        logger.error(f"❌ WebSocket Error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
