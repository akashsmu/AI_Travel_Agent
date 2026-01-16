import os
from typing import List, Dict, Any
from mem0 import MemoryClient
from utils.logger import logger

class MemoryManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MemoryManager, cls).__new__(cls)
            cls._instance.client = None
            cls._instance._initialize_client()
        return cls._instance
    
    def _initialize_client(self):
        """Initialize Mem0 client if API key is present."""
        api_key = os.getenv("MEM0_API_KEY")
        if api_key:
            try:
                self.client = MemoryClient(api_key=api_key)
                logger.info("🧠 Mem0 Client Initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Mem0 client: {e}")
        else:
            logger.warning("⚠️ MEM0_API_KEY not found. Memory features will be disabled.")

    def add_memory(self, user_id: str, text: str) -> None:
        """Add a memory for a specific user."""
        if not self.client:
            return
            
        try:
            self.client.add(text, user_id=user_id)
            logger.info(f"🧠 Added memory for {user_id}: {text}")
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")

    def get_memories(self, user_id: str, query: str = None) -> List[str]:
        """
        Search for relevant memories. 
        If query is provided, performs semantic search.
        Otherwise returns recent memories.
        """
        if not self.client:
            return []
            
        try:
            if query:
                results = self.client.search(query, user_id=user_id)
            else:
                results = self.client.get_all(user_id=user_id)
                
            # Parse results - Mem0 returns list of dicts with 'memory' key usually, 
            # or 'text' depending on version. Let's inspect structure safely.
            memories = []
            for item in results:
                # Handle different potential response structures
                if isinstance(item, dict):
                    memories.append(item.get("memory", item.get("text", str(item))))
                else:
                    memories.append(str(item))
                    
            logger.info(f"🧠 Retrieved {len(memories)} memories for {user_id}")
            return memories
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {e}")
            return []

    def get_all_memories(self, user_id: str) -> List[str]:
        """Wrapper to get all memories without specific query."""
        return self.get_memories(user_id)
