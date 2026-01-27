
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from utils.logger import setup_logger
from utils.llm_factory import get_llm

logger = setup_logger("itinerary_agent")

def generate_itinerary(state):
    """
    Generate a day-by-day itinerary based on the user's trip details 
    and the selected/found accommodations and flights.
    """
    
    logger.info("📝 Generating itinerary...")
    
    llm = get_llm(temperature=0.7)
    
    # Prepare context
    hotels_str = "\n".join([f"- {h.get('name')} in {h.get('city')} (${h.get('price')}/night)" for h in state.accommodations[:3]])
    flights_str = "\n".join([f"- {f.get('airline')} (${f.get('price')})" for f in state.flights[:2]])
    
 
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are a production-grade AI Travel Planner responsible for creating realistic,
            safe, budget-aware, and enjoyable travel itineraries.

            Your task is to generate a detailed itinerary using ONLY the information provided
            below, external search results supplied to you (flights, hotels, transport),
            and reasonable geographic assumptions. Do NOT invent unavailable flights,
            hotels, or attractions.

            ────────────────────────────
            TRIP DETAILS
            ────────────────────────────
            - Origin: {origin}
            - Destination: {destination}
            - Dates: {start_date} to {end_date}
            - Purpose of Travel: {trip_purpose} (Vacation | Job Relocation)
            - Number of Travelers: {travel_party}
            - Age Information: {age_context}
            - Accessibility or Disability Needs: {accessibility_needs}
            - Budget (total or per person): ${budget}
            - Transportation Preference: {transportation_mode}
            - Location Type: {location_scope} (International | Domestic)

            ────────────────────────────
            TRAVEL STYLE & PREFERENCES
            ────────────────────────────
            - Travel Pace: {travel_pace} (Relaxed | Moderate | Hectic)
            - Tourist Type:
            - In-depth Explorer
            - Wannabe Tourist (easy, Instagram-friendly landmarks)
            - Hidden-Gems Traveler
            - Solo Traveler (safety-aware)
            - Interests:
            {interests}

            ────────────────────────────
            AVAILABLE OPTIONS (USE THESE FIRST)
            ────────────────────────────
            Hotels:
            {hotels}

            Flights / Trains / Buses / Rental Cars:
            {flights}

            ────────────────────────────
            PLANNING RULES (IMPORTANT)
            ────────────────────────────
            1. Cluster nearby locations to minimize travel time.
            2. Adjust walking distance, activity density, and rest time based on age and accessibility needs.
            3. Strictly respect the budget:
            - Prefer free/low-cost attractions when budget is limited.
            - Recommend public transport over taxis when appropriate.
            4. Prioritize safety:
            - Avoid unsafe areas.
            - Prefer well-reviewed neighborhoods.
            - Mention nearby hospitals or clinics when relevant.
            5. Adapt recommendations based on travel purpose:
            - Job Relocation → apartments, groceries, cafes, social spaces, quiet work spots.
            - Vacation → landmarks, experiences, food, relaxation.
            6. Recommend realistic daily schedules (avoid overpacking days).
            7. If data is missing, make conservative assumptions and clearly state them.

            ────────────────────────────
            ITINERARY REQUIREMENTS
            ────────────────────────────
            For EACH day, include:
            - Morning / Afternoon / Evening structure
            - Key attractions and activities
            - How to get there (walk / metro / bus / taxi / car)
            - Approximate travel time between stops
            - Nearby food options
            - Rest or buffer time when needed

            Additionally include:
            - Arrival & check-in plan (Day 1)
            - Departure plan (Last Day)
            - Best time of day to visit major landmarks
            - Weather or seasonal considerations (if relevant)
            - Estimated local transport costs (rough ranges are fine)

            ────────────────────────────
            OUTPUT FORMAT
            ────────────────────────────
            - Clear day-by-day sections (Day 1, Day 2, …)
            - Bullet points for readability
            - Friendly, professional tone
            - Optimized for interactive map visualization

            End with:
            1. Traveler Profile Summary
            2. Why This Works
            3. Swap or Refresh Suggestions

            Your goal is to make the itinerary feel:
            ✔ realistic
            ✔ easy to follow
            ✔ personalized
            ✔ safe
            ✔ worth sharing
            """
        )
    ])

    
    chain = prompt | llm | StrOutputParser()
    
    # Construct age context string
    age_context = "Unknown"
    if state.travel_party == "solo":
        age_context = f"Age: {state.traveler_age}" if state.traveler_age else "Adult"
    elif state.travel_party == "group":
        age_context = f"Ages {state.group_age_min}-{state.group_age_max}" if state.group_age_min else "Mixed Group"

    try:
        result = chain.invoke({
            "destination": state.destination,
            "origin": state.origin,
            "start_date": state.start_date,
            "end_date": state.end_date,
            "trip_purpose": state.trip_purpose or "vacation",
            "travel_party": state.travel_party or "solo",
            "age_context": age_context,
            "transportation_mode": state.transportation_mode or "public",
            "budget": state.budget or "Flexible",
            "accessibility_needs": state.accessibility_needs or "None",
            "location_scope": state.location_scope or "Domestic",
            "travel_pace": state.travel_pace or "Moderate",
            "interests": state.interests or "General sightseeing",
            "hotels": hotels_str,
            "flights": flights_str
        })
        
        state.itinerary = result
        logger.info("✅ Itinerary generated.")
    except Exception as e:
        logger.error(f"⚠️ Error creating itinerary: {e}")
        state.itinerary = "Could not generate itinerary at this time."
        
    return state
