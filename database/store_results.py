from .singlestore_client import get_conn
from utils.logger import setup_logger
import json

logger = setup_logger("store_results")

def store_results(state):
    """
    Store freshly fetched accommodations and flights into SingleStore.
    Called only on cache miss.
    """
    conn = get_conn()
    cur = conn.cursor()

    try:
        # Accommodations
        if state.accommodations:
            logger.info(f"Storing {len(state.accommodations)} accommodations")
            for h in state.accommodations:
                cur.execute(
                    """
                    INSERT INTO accommodations
                        (name, city, country, price_per_night, rating, url, bedrooms, description)
                    VALUES
                        (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        h.get("name"),
                        h.get("city"),
                        h.get("country", ""),
                        h.get("price"),
                        h.get("rating"),
                        h.get("url"),
                        h.get("bedrooms", 1),
                        h.get("description", "")
                    )
                )

        # Flights
        if state.flights:
            logger.info(f"Storing {len(state.flights)} flights")
            for f in state.flights:
                # details might be a dict, stash it as JSON
                details_json = json.dumps(f.get("details", {}))
                
                cur.execute(
                    """
                    INSERT INTO flights
                        (airline, origin, destination, price, url, details)
                    VALUES
                        (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        f.get("airline"),
                        f.get("origin"),
                        f.get("destination"),
                        f.get("price"),
                        f.get("url"),
                        details_json
                    )
                )

        conn.commit()
        logger.info("✅ Results stored successfully.")
        
    except Exception as e:
        logger.error(f"Failed to store results: {e}")
        # Don't raise, just log, so graph can continue
    finally:
        conn.close()
        return state