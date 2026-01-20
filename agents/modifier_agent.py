from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import Optional, List
from state import TravelState
from utils.memory import MemoryManager

class StateUpdate(BaseModel):
    """
    Schema for updating the TravelState based on user feedback.
    Only fields relevant to refinement are included.
    """
    max_price_per_night: Optional[float] = Field(None, description="Updated max price per night")
    min_rating: Optional[float] = Field(None, description="Updated minimum hotel rating")
    travel_pace: Optional[str] = Field(None, description="Updated travel pace (e.g., relaxed, fast, balanced)")
    interests: Optional[List[str]] = Field(None, description="Updated list of interests")
    trip_purpose: Optional[str] = Field(None, description="Updated trip purpose")
    bedrooms: Optional[int] = Field(None, description="Updated number of bedrooms")
    
    # New Field for Memory
    new_preference: Optional[str] = Field(None, description="Any permanent user preference extracted from the feedback (e.g., 'User hates hostels', 'User prefers Delta')")

    # Flags to indicate what needs re-running
    rerun_hotels: bool = Field(False, description="True if hotel preferences changed")
    rerun_itinerary: bool = Field(False, description="True if itinerary preferences changed (pace, interests, purpose)")

llm = ChatOpenAI(model="gpt-4o", temperature=0)

parser = JsonOutputParser(pydantic_object=StateUpdate)

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are a Travel State Modifier. Your goal is to interpret user feedback and update the travel parameters.
    
    Current State:
    {current_state}
    
    User Feedback:
    {user_message}
    
    Instructions:
    1. Identify what the user wants to change.
    2. Map it to the `StateUpdate` schema fields.
    3. Set `rerun_hotels` to True if price, rating, or bedrooms change.
    4. Set `rerun_itinerary` to True if pace, interests, or purpose change.
    5. If the user expresses a general preference, extract it into `new_preference` using a structured format like "Category: [Value]".
       - Example: "Airline: Delta Only"
       - Example: "Hotel: No Hostels"
       - Example: "Food: Vegetarian options required"
    
    Return only the JSON object matching StateUpdate.
    """),
    ("user", "{user_message}")
])

chain = prompt | llm | parser

def modify_state(state: TravelState, message: str) -> tuple[TravelState, dict]:
    """
    Updates the state based on message.
    Returns (updated_state, diff_dict)
    """
    # 1. Run LLM
    try:
        # Create a simplified dict representation for the LLM
        current_summary = {
            "max_price": state.max_price_per_night,
            "min_rating": state.min_rating,
            "bedrooms": state.bedrooms,
            "pace": state.travel_pace,
            "interests": state.interests,
            "purpose": state.trip_purpose
        }
        
        result = chain.invoke({"current_state": str(current_summary), "user_message": message})
        updates = StateUpdate(**result)
        
        # 2. Apply updates
        new_state = state.copy()
        
        if updates.max_price_per_night is not None:
             new_state.max_price_per_night = updates.max_price_per_night
        if updates.min_rating is not None:
             new_state.min_rating = updates.min_rating
        if updates.bedrooms is not None:
             new_state.bedrooms = updates.bedrooms
        
        if updates.travel_pace:
             new_state.travel_pace = updates.travel_pace
        if updates.interests:
             new_state.interests = updates.interests
        if updates.trip_purpose:
             new_state.trip_purpose = updates.trip_purpose
             
        # 3. Handle Memory
        if updates.new_preference:
            mem_mgr = MemoryManager()
            user_id = "default_user" # Should come from state in real app
            mem_mgr.add_memory(user_id, updates.new_preference)
            # Update local state too so it's used immediately
            new_state.user_preferences.append(updates.new_preference)
             
        return new_state, updates.dict()
        
    except Exception as e:
        print(f"Error modifying state: {e}")
        return state, {}


