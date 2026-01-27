from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from agents.tools.serp_tools import search_google_flights
from utils.logger import setup_logger
from utils.llm_factory import get_llm

logger = setup_logger("flight_agent")

class AirlinePreferences(BaseModel):
    preferred_airlines: List[str] = Field(default_factory=list, description="List of preferred airline names (e.g., 'Delta', 'United')")
    excluded_airlines: List[str] = Field(default_factory=list, description="List of airlines to avoid (e.g., 'Spirit', 'Ryanair')")

llm = get_llm(temperature=0)
parser = JsonOutputParser(pydantic_object=AirlinePreferences)

preference_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    You are an Airline Preference Extractor.
    
    Task: Analyze the user's travel memories/preferences and extract specific airline constraints.
    
    User Memories:
    {memories}
    
    Instructions:
    1. Identify positive preferences (e.g., "I strictly fly Delta", "Star Alliance only") -> `preferred_airlines`.
    2. Identify negative preferences (e.g., "No Spirit", "Avoid low cost carriers") -> `excluded_airlines`.
    3. If "Star Alliance" is mentioned, expand to: United, Lufthansa, Air Canada, ANA, Singapore Airlines, Turkish Airlines.
    4. If "OneWorld" is mentioned, expand to: American, British Airways, Cathay Pacific, Qantas.
    5. If "SkyTeam" is mentioned, expand to: Delta, Air France, KLM, Korean Air.
    6. If "No Low Cost", add: Spirit, Frontier, Ryanair, EasyJet, Southwest (if context implies).
    
    Return JSON matching the AirlinePreferences schema.
    """),
    ("user", "Extract preferences.")
])

chain = preference_prompt | llm | parser

def fetch_flights_from_api(state):
    """
    Fetch flights using SerpAPI (Google Flights) with smart LLM filtering.
    """
    logger.info(f"✈️ Searching flights from {state.origin} to {state.destination}...")
    flights = search_google_flights(state.model_dump())
    
    # Smart Filter with Mem0
    if state.user_preferences and flights:
        try:
            memories_text = "\n".join(state.user_preferences)
            logger.info("🧠 Analyzing airline preferences with LLM...")
            
            result = chain.invoke({"memories": memories_text})
            prefs = AirlinePreferences(**result)
            
            # Application Logic
            if prefs.excluded_airlines:
                original_count = len(flights)
                flights = [f for f in flights if not any(ex.lower() in f.get('airline', '').lower() for ex in prefs.excluded_airlines)]
                if len(flights) < original_count:
                    logger.info(f"🚫 Filtered {original_count - len(flights)} flights based on exclusion list: {prefs.excluded_airlines}")

            if prefs.preferred_airlines:
                # boost preferred
                logger.info(f"✨ Boosting airlines: {prefs.preferred_airlines}")
                # Create a score: 1 if preferred, 0 if not. Sort desc.
                flights.sort(key=lambda x: any(p.lower() in x.get('airline', '').lower() for p in prefs.preferred_airlines), reverse=True)
                
        except Exception as e:
            logger.error(f"Preference extraction failed: {e}")
            # Fallback: maintain original order

    if flights:
        logger.info(f"✅ Found {len(flights)} flights from SerpAPI.")
        state.flights = flights
    else:
        logger.warning("⚠️ No flights found via SerpAPI.")
        state.flights = []
        
    return state