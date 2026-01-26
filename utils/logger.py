import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name="ai_travel_agent", log_file="app.log", level=logging.INFO):
    """Function to setup as many loggers as you want"""
    
    # Create logs directory if not exists
    if not os.path.exists("logs"):
        os.makedirs("logs")

    log_path = os.path.join("logs", log_file)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=5)
    handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding handlers multiple times
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)
        
    return logger

# Create a default logger instance for easy import
logger = setup_logger()
