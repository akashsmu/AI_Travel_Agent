import time
import functools
from utils.logger import logger

def with_retry(max_retries=3, backoff_factor=2, exceptions=(Exception,)):
    """
    Decorator for exponential backoff.
    
    Args:
        max_retries (int): Maximum number of retries before giving up.
        backoff_factor (int): Multiplier for the wait time (1s, 2s, 4s...).
        exceptions (tuple): Tuple of exceptions to catch and retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = 1
            
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"❌ {func.__name__} failed after {max_retries} retries. Error: {e}")
                        raise e
                    
                    logger.warning(f"⚠️ {func.__name__} failed (Attempt {retries}/{max_retries}). Retrying in {delay}s... Error: {e}")
                    time.sleep(delay)
                    delay *= backoff_factor
        return wrapper
    return decorator
