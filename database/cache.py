from .singlestore_client import get_conn
from utils.logger import setup_logger

logger = setup_logger("cache")

def check_cache(state):
    """
    Check SingleStore for cached hotels & flights for this route.
    If BOTH exist, it's a cache hit. Otherwise, return None (cache miss).
    """
    conn = get_conn()
    cur = conn.cursor()

    # Hotels for destination
    cur.execute("""
        SELECT
            name,
            city,
            country,
            price_per_night,
            rating,
            url,
            bedrooms
        FROM accommodations
        WHERE LOWER(city) = LOWER(%s)
        LIMIT 10
    """, (state.destination,))
    hotel_cols = [col[0] for col in cur.description]
    hotel_rows = cur.fetchall()
    hotels = [dict(zip(hotel_cols, r)) for r in hotel_rows]

    # Flights for origin + destination
    cur.execute("""
        SELECT
            airline,
            origin,
            destination,
            price,
            url
        FROM flights
        WHERE origin = %s AND destination = %s
        LIMIT 10
    """, (state.origin, state.destination))
    flight_cols = [col[0] for col in cur.description]
    flight_rows = cur.fetchall()
    flights = [dict(zip(flight_cols, r)) for r in flight_rows]

    if len(hotels) > 0 and len(flights) > 0:
        state.accommodations = hotels
        state.flights = flights
        return state

    # Cache miss
    return None