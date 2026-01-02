
import logging
import sys
import os

def setup_logger(name: str = "ai_travel_agent"):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File Handler (optional)
        # fh = logging.FileHandler("agent.log")
        # fh.setLevel(logging.DEBUG)
        # fh.setFormatter(formatter)
        # logger.addHandler(fh)
        
    return logger
