import os
import singlestoredb as s2
from dotenv import load_dotenv

load_dotenv()

from utils.logger import setup_logger

logger = setup_logger("db_client")

def get_conn():
    """
    Create and return a SingleStore database connection.
    """
    host = os.getenv("SINGLESTORE_HOST")
    user = os.getenv("SINGLESTORE_USER")
    password = os.getenv("SINGLESTORE_PASSWORD")
    db = os.getenv("SINGLESTORE_DB")

    if not all([host, user, password, db]):
        logger.error("Missing database connection parameters (URL or individual fields)")
        raise ValueError("Missing SingleStore environment variables")

    try:
        conn = s2.connect(
            host=host,
            user=user,
            password=password,
            database=db,
            port=3306,
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to SingleStore: {e}")
        raise RuntimeError(f"Database connection failed: {e}")

