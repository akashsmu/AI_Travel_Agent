from state import TravelState
from utils.logger import logger

def check_constraints(state: TravelState) -> dict:
    """
    Validates the current trip plan against constraints.
    Returns update for 'constraint_violations' list.
    """
    violations = []
    
    # 1. Budget Check
    if state.budget and state.budget > 0:
        total_estimated = 0
        
        # Flight cost
        if state.flights:
             # Take average of first 3 unique prices as estimate
             prices = [f.get('price', 0) for f in state.flights[:3] if f.get('price')]
             if prices:
                 total_estimated += sum(prices) / len(prices)
        
        # Hotel cost
        if state.accommodations:
            # Avg nightly rate * nights
            rates = [h.get('avg_nightly_price', h.get('price_per_night', 0)) for h in state.accommodations[:3]]
            if rates:
                avg_rate = sum(rates) / len(rates)
                # Calculate nights
                # (Assuming 5 nights if date parsing complex for this simple check, 
                # or we could parse start/end strings. Let's use simple estimate for now)
                nights = 5 
                total_estimated += avg_rate * nights
                
        if total_estimated > state.budget:
            violations.append(f"Estimated cost (${total_estimated:.0f}) exceeds budget (${state.budget})")

    # 2. Flight Time Check (Example constraint triggered by preferences)
    # If users have "Short flights only" in preferences
    # This logic would be more complex with Mem0, but adding placeholder structure.
    
    if violations:
        logger.warning(f"⚠️ Constraints Violated: {violations}")
        
    return {"constraint_violations": violations}
