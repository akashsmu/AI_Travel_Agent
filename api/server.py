
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

app = FastAPI()

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
    travel_party: Optional[str] = "solo_male"
    budget: Optional[float] = None

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

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        data = await websocket.receive_text()
        req_data = json.loads(data)
        
        initial_state = TravelState(
            origin=req_data.get("origin"),
            destination=req_data.get("destination"),
            start_date=req_data.get("start_date"),
            end_date=req_data.get("end_date"),
        )
        
        await websocket.send_text(json.dumps({"type": "status", "message": "Starting travel planning..."}))
        
        # Stream events from graph
        async for event in graph.astream(initial_state):
             for key, value in event.items():
                if key == "__end__":
                    continue
                
                # Send update to client
                await websocket.send_text(json.dumps({
                    "type": "update",
                    "step": key,
                    "data": value if isinstance(value, dict) else str(value) # simplified
                }))
        
        await websocket.send_text(json.dumps({"type": "complete", "message": "Planning complete!"}))
        
    except Exception as e:
        print(f"WebSocket Error: {e}")
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
