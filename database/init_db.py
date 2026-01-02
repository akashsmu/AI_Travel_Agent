
from dotenv import load_dotenv
from singlestore_client import get_conn

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

    # 1. Flights Table
    # Added: created_at, unique constraint logic (optional but good for data quality)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flights (
            id INT AUTO_INCREMENT PRIMARY KEY,
            airline VARCHAR(255),
            origin VARCHAR(10),
            destination VARCHAR(10),
            price FLOAT,
            url TEXT,
            details JSON,
            search_id VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            KEY(origin, destination)
        );
    """)

    # 2. Accommodations Table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accommodations (
            id INT AUTO_INCREMENT PRIMARY KEY,
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
            KEY(city)
        );
    """)
    
    # 3. Trip Plans Table
    # To store the generated plans and chat history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trip_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            origin VARCHAR(255),
            destination VARCHAR(255),
            start_date DATE,
            end_date DATE,
            trip_purpose VARCHAR(50),
            travel_party VARCHAR(50),
            budget FLOAT,
            itinerary_text LONGTEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()
    print("✅ Database tables initialized successfully.")
    conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    init_db()
