from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agents.tools.serp_tools import search_google_hotels
from utils.logger import setup_logger
from utils.llm_factory import get_llm

logger = setup_logger("search_agent")
llm = get_llm(temperature=0)

def live_search(state):
    """
    Search for accommodations using SerpAPI (Google Hotels) with personalized query.
    """
    dest = state.destination
    city_name = state.destination_city or dest
    
    # Include user preferences from Mem0
    preferences_text = "\n".join(state.user_preferences) if state.user_preferences else "None"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a Hotel Search Expert.
        
        Task: Create a targeted search query for Google Hotels based on the user's trip details and PREFERENCES.
        
        Trip Details:
        - Destination: {destination} (City: {city})
        - Budget: {budget}
        - Travelers: {party}
        - Rating: {rating}+
        
        User Preferences (Long-term memory):
        {preferences}
        
        Instructions:
        1. Combine the destination with specific keywords from preferences (e.g., "hotels in Tokyo near gym").
        2. If no preferences, just use generic "hotels in {{city}}".
        3. Return ONLY the raw search query string.
        """),
        ("user", "Genereate query.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    try:
        query = chain.invoke({
            "destination": dest,
            "city": city_name,
            "budget": state.max_price_per_night,
            "party": state.travel_party,
            "rating": state.min_rating,
            "preferences": preferences_text
        })
        logger.info(f"🔎 Generated Query: {query}")
        
        # We need to pass this query to serp_tools. 
        # Updating state temporarily or passing explicit arg if tool supports it.
        # Check serp_tools.py to see if it accepts a custom 'q' or uses state fields.
        # Assuming we need to override the implicit query construction in serp_tools
        # For now, let's create a temporary state dict with a 'custom_query' or just pass it.
        # Looking at serp_tools logic (previous context), it uses params.get("q").
        
        params = state.dict()
        params["q"] = query # Override default query construction
        
        hotels = search_google_hotels(params)
        
        if hotels:
            logger.info(f"✅ Found {len(hotels)} hotels from SerpAPI.")
            state.accommodations = hotels
        else:
            logger.warning("⚠️ No hotels found via SerpAPI.")
            state.accommodations = []
            
    except Exception as e:
        logger.error(f"Search failed: {e}")
        state.accommodations = []

    return state