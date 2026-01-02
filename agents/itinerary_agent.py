
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from utils.logger import setup_logger

logger = setup_logger("itinerary_agent")

def generate_itinerary(state):
    """
    Generate a day-by-day itinerary based on the user's trip details 
    and the selected/found accommodations and flights.
    """
    
    logger.info("📝 Generating itinerary...")
    
    llm = ChatOpenAI(model=os.getenv("OPENAI_CHAT_MODEL", "gpt-4-turbo"), temperature=0.7)
    
    # Prepare context
    hotels_str = "\n".join([f"- {h.get('name')} in {h.get('city')} (${h.get('price')}/night)" for h in state.accommodations[:3]])
    flights_str = "\n".join([f"- {f.get('airline')} (${f.get('price')})" for f in state.flights[:2]])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert travel agent. Create a detailed, engaging day-by-day itinerary."),
        ("user", """
        Create an itinerary for a trip to {destination} from {origin}.
        Dates: {start_date} to {end_date}.
        
        Trip Context:
        - Purpose: {trip_purpose}
        - Travelers: {travel_party}
        - Budget: ${budget}
        
        Using these options found:
        Hotels:
        {hotels}
        
        Flights:
        {flights}
        
        The itinerary should include:
        1. Arrival and check-in.
        2. Daily activities (mix of sightseeing, food, relaxation) tailored to the trip purpose (e.g., if work, ensure wifi/cafes; if vacation, focus on fun) and party type.
        3. Departure details.
        
        Keep it structured and fun!
        """)
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        result = chain.invoke({
            "destination": state.destination,
            "origin": state.origin,
            "start_date": state.start_date,
            "end_date": state.end_date,
            "trip_purpose": state.trip_purpose or "vacation",
            "travel_party": state.travel_party or "solo",
            "budget": state.budget or "Flexible",
            "hotels": hotels_str,
            "flights": flights_str
        })
        
        state.itinerary = result
        logger.info("✅ Itinerary generated.")
    except Exception as e:
        logger.error(f"⚠️ Error creating itinerary: {e}")
        state.itinerary = "Could not generate itinerary at this time."
        
    return state
