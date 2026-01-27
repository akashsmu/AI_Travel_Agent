from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from state import TravelState
from utils.logger import logger

from utils.llm_factory import get_llm

llm = get_llm(temperature=0.7)

def reasoning_node(state: TravelState):
    """
    Analyzes the complete trip and provides a qualitative "Agent Note".
    """
    logger.info("🧠 Reasoning Agent: Analyzing final trip...")
    
    validation_issues = ", ".join(state.constraint_violations) if state.constraint_violations else "None"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are a Helpful Travel Assistant Reviewer.
        
        Task: Review the planned trip and provide a short, helpful "Agent Note" for the user.
        
        Trip Data:
        - Destination: {destination}
        - Flights Found: {num_flights}
        - Hotels Found: {num_hotels}
        - Budget Issues: {issues}
        - Weather: {weather}
        
        Instructions:
        1. Summarize the "vibe" of the options found (e.g., "Found some great budget interaction hotels").
        2. Point out any compromises (e.g., "Flights represent good value but have layovers").
        3. Highlight weather warnings if any.
        4. Keep it conversational and under 3 sentences.
        """),
        ("user", "Analyze this trip.")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        note = chain.invoke({
            "destination": state.destination,
            "num_flights": len(state.flights),
            "num_hotels": len(state.accommodations),
            "issues": validation_issues,
            "weather": state.weather_summary or "Unknown"
        })
        logger.info(f"🧠 Generated Note: {note}")
        return {"trip_analysis": note}
    except Exception as e:
        logger.error(f"Reasoning failed: {e}")
        return {"trip_analysis": "Trip generated successfully."}
