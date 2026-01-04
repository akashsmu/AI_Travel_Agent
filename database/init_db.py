
from dotenv import load_dotenv
from database.singlestore_client import get_conn

# Load environment variables
load_dotenv()

def init_db():
    """
    Initialize database tables only (assumes database already exists).
    Run this after ensuring your SingleStore database is created.
    """
    print("🛠️ Initializing Database Tables...")
    
    conn = get_conn()
    cur = conn.cursor()

    # 1. Trip Plans (Parent Table)
    cur.execute("DROP TABLE IF EXISTS trip_plans")
    cur.execute("""
        CREATE TABLE trip_plans (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            -- Search Parameters
            origin VARCHAR(255),
            destination VARCHAR(255),
            start_date DATE,
            end_date DATE,
            trip_purpose VARCHAR(50),
            travel_party VARCHAR(50),
            traveler_age INT,
            group_age_min INT,
            group_age_max INT,
            transportation_mode VARCHAR(50),
            budget FLOAT,
            bedrooms INT,
            max_price_per_night FLOAT,
            min_rating FLOAT,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY cache_idx (origin, destination, start_date, end_date)
        );
    """)

    # 2. Flights (Child)
    cur.execute("DROP TABLE IF EXISTS flights")
    cur.execute("""
        CREATE TABLE flights (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            trip_id BIGINT,
            airline VARCHAR(255),
            origin VARCHAR(10),
            destination VARCHAR(10),
            price FLOAT,
            url TEXT,
            details JSON, -- Stores rich data like flight number, extensions
            search_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY(trip_id)
        );
    """)

    # 3. Accommodations (Child)
    cur.execute("DROP TABLE IF EXISTS accommodations")
    cur.execute("""
        CREATE TABLE accommodations (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            trip_id BIGINT,
            name VARCHAR(255),
            city VARCHAR(255),
            country VARCHAR(255),
            price_per_night FLOAT,
            rating FLOAT,
            bedrooms INT,
            url TEXT,
            image_url TEXT,
            description TEXT,
            search_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY(trip_id)
        );
    """)
    
    # 4. Itineraries (Child)
    cur.execute("DROP TABLE IF EXISTS itineraries")
    cur.execute("""
        CREATE TABLE itineraries (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            trip_id BIGINT,
            itinerary_text LONGTEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY(trip_id)
        );
    """)

    # 5. Weather (Child)
    cur.execute("DROP TABLE IF EXISTS weather")
    cur.execute("""
        CREATE TABLE weather (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            trip_id BIGINT,
            summary TEXT,
            weather_info JSON, -- Structured forecast
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY(trip_id)
        );
    """)

    conn.commit()
    print("✅ Database tables initialized successfully.")
    conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    init_db()
