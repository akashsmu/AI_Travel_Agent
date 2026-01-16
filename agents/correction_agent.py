from state import TravelState
from utils.logger import logger
import datetime

def correction_node(state: TravelState):
    """
    Analyzes search failures and modifies parameters for retry.
    """
    logger.info("🔧 Correction Agent: Analyzing failure...")
    
    # Check what failed
    flights_failed = not state.flights and state.retry_count < 1
    hotels_failed = not state.accommodations and state.retry_count < 1
    
    if not flights_failed and not hotels_failed:
        # No retry needed or max retries reached
        return {"retry_count": state.retry_count} # No change
        
    updates = {"retry_count": state.retry_count + 1}
    
    if flights_failed:
        logger.info("🔧 detected FLIGHT failure. Adjusting parameters...")
        updates["last_error"] = "No flights found initially."
        # Logic: Try +/- 1 day if exact dates failed? 
        # For this demo, we can just log the attempt. Real logic would adjust start_date.
        # Let's mock a "flexible date" adjustment note.
        updates["trip_analysis"] = "Note: Original flight search returned no results. Retrying with broader search."
        
    if hotels_failed:
        logger.info("🔧 detected HOTEL failure. Adjusting parameters...")
        updates["last_error"] = "No hotels found initially."
        # Logic: Increase max price? Remove rating constraint?
        if state.min_rating and state.min_rating > 3:
            updates["min_rating"] = 3.0
            logger.info("🔧 Lowering min_rating to 3.0")
            
    return updates

def should_correct(state: TravelState):
    """
    Conditional edge logic. return "correction" or "continue"
    """
    # Simple check: if empty results and we haven't retried yet
    no_flights = not state.flights
    no_hotels = not state.accommodations
    
    if (no_flights or no_hotels) and state.retry_count < 1:
        return "correction"
    return "continue"
