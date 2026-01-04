
from fastapi import FastAPI, WebSocket, HTTPException
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
    origin: str
    destination: str
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
        initial_state = TravelState(
            origin=req_data.get("origin"),
            destination=req_data.get("destination"),
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
                
                # Send update to client
                await websocket.send_text(json.dumps({
                    "type": "update",
                    "step": key,
                    "message": f"Completed {key}"
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
        
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        print(f"WebSocket Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
