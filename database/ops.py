import json
from datetime import datetime, timedelta
from typing import Union, List, Dict, Any
from database.singlestore_client import get_conn
from state import TravelState
from utils.logger import setup_logger

logger = setup_logger()

def save_trip_plan(state: TravelState):
    """
    Saves the completed trip plan to the database (Normalized).
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # 1. Insert Parent Trip Plan
        query_plan = """
            INSERT INTO trip_plans (
                origin, destination, origin_city, destination_city, start_date, end_date, 
                trip_purpose, travel_party, traveler_age, 
                group_age_min, group_age_max, transportation_mode, 
                budget, bedrooms, max_price_per_night, min_rating
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values_plan = (
            state.origin, state.destination, state.origin_city, state.destination_city, state.start_date, state.end_date,
            state.trip_purpose, state.travel_party, state.traveler_age,
            state.group_age_min, state.group_age_max, state.transportation_mode,
            state.budget, state.bedrooms, state.max_price_per_night, state.min_rating
        )
        cur.execute(query_plan, values_plan)
        trip_id = cur.lastrowid
        
        # 2. Insert Itinerary (One-to-One here, but separate table)
        if state.itinerary:
            cur.execute(
                "INSERT INTO itineraries (trip_id, itinerary_text) VALUES (%s, %s)",
                (trip_id, state.itinerary)
            )

        # 3. Insert Weather (One-to-One usually)
        if state.weather_info:
            cur.execute(
                "INSERT INTO weather (trip_id, summary, weather_info) VALUES (%s, %s, %s)",
                (trip_id, state.weather_summary, json.dumps(state.weather_info))
            )

        # 4. Insert Flights (One-to-Many)
        flight_query = """
            INSERT INTO flights (trip_id, airline, origin, destination, price, url, details)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        for f in state.flights:
            cur.execute(flight_query, (
                trip_id, 
                f.get("airline"), 
                f.get("origin"), 
                f.get("destination"), 
                f.get("price"), 
                f.get("url"), 
                json.dumps(f)  # store full object in details for reconstruction
            ))

        # 5. Insert Accommodations (One-to-Many)
        hotel_query = """
            INSERT INTO accommodations (trip_id, name, city, country, price_per_night, rating, bedrooms, url, image_url, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        for h in state.accommodations:
            cur.execute(hotel_query, (
                trip_id,
                h.get("name"),
                h.get("city"),
                h.get("country"),
                h.get("price") or h.get("price_per_night"), # handle inconsistent naming if any
                h.get("rating"),
                state.bedrooms, # assuming request param implies this
                h.get("url"),
                h.get("image"),
                h.get("description")
            ))

        conn.commit()
        conn.close()
        logger.info(f"💾 Trip plan saved for {state.destination} (ID: {trip_id})")
        
    except Exception as e:
        logger.error(f"❌ Failed to save trip plan: {e}")

def find_cached_trip(params: Union[dict, TravelState]) -> Union[dict, None]:
    """
    Attempts to find a recent matching trip plan (Normalized).
    Returns None if no cache hit.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        
        # Handle both dict and TravelState (Pydantic model)
        if hasattr(params, "dict"):
            p = params.dict()
        elif hasattr(params, "model_dump"): # Pydantic v2
            p = params.model_dump()
        else:
            p = params

        # 1. Find Trip ID
        query = """
            SELECT id, created_at, origin_city, destination_city
            FROM trip_plans
            WHERE 
                origin = %s 
                AND destination = %s 
                AND start_date = %s 
                AND end_date = %s
                AND trip_purpose = %s
                AND created_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY created_at DESC
            LIMIT 1
        """
        cur.execute(query, (
            p.get("origin"), p.get("destination"), 
            p.get("start_date"), p.get("end_date"), 
            p.get("trip_purpose")
        ))
        row = cur.fetchone()
        
        if not row:
            conn.close()
            return None
            
        trip_id = row[0]
        logger.info(f"⚡️ Cache HIT: Found Trip ID {trip_id}")

        # 2. Fetch Components
        
        # Itinerary
        cur.execute("SELECT itinerary_text FROM itineraries WHERE trip_id = %s LIMIT 1", (trip_id,))
        itinerary_row = cur.fetchone()
        itinerary = itinerary_row[0] if itinerary_row else None
        
        # Weather
        cur.execute("SELECT summary, weather_info FROM weather WHERE trip_id = %s LIMIT 1", (trip_id,))
        weather_row = cur.fetchone()
        weather_summary = weather_row[0] if weather_row else None
        weather_info = json.loads(weather_row[1]) if weather_row and weather_row[1] else None
        
        # Flights 
        cur.execute("SELECT details FROM flights WHERE trip_id = %s", (trip_id,))
        flight_rows = cur.fetchall()
        flights = [json.loads(r[0]) for r in flight_rows]
        
        # Accommodations
        cur.execute("""
            SELECT name, city, country, price_per_night, rating, bedrooms, url, image_url, description 
            FROM accommodations WHERE trip_id = %s
        """, (trip_id,))
        
        columns = [col[0] for col in cur.description]
        hotel_rows = cur.fetchall()
        hotels = []
        for r in hotel_rows:
            h = dict(zip(columns, r))
            h['price'] = h['price_per_night'] 
            h['image'] = h['image_url']
            hotels.append(h)

        conn.close()

        return {
            "origin_city": row[2],
            "destination_city": row[3],
            "weather_info": weather_info,
            "weather_summary": weather_summary,
            "flights": flights,
            "accommodations": hotels,
            "itinerary": itinerary,
            "cached": True
        }

    except Exception as e:
        logger.error(f"⚠️ Cache lookup failed: {e}")
        return None
