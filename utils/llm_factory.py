from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from utils.logger import logger
import os

class FallbackLLM:
    """
    A simple wrapper that tries a list of LLMs in order until one succeeds.
    This mimics the behavior of LangChain's .with_fallbacks() but gives us more explicit control if needed.
    """
    def __init__(self, models):
        self.models = models

    def invoke(self, *args, **kwargs):
        last_exception = None
        for i, model in enumerate(self.models):
            try:
                # logger.info(f"🤖 Attempting to run with model: {model.model_name if hasattr(model, 'model_name') else 'unknown'}")
                return model.invoke(*args, **kwargs)
            except Exception as e:
                logger.warning(f"⚠️ Model {i+1} failed: {e}. Switching to next fallback...")
                last_exception = e
        
        logger.error("❌ All fallback models failed.")
        raise last_exception

def get_llm(temperature=0.7) -> BaseChatModel:
    """
    Returns an LLM with fallback capabilities.
    Order: GPT-4o -> Claude 3.5 Sonnet -> Llama (via Groq or Local)
    """
    
    # 1. Primary: GPT-4o
    primary = ChatOpenAI(model="gpt-4o", temperature=temperature)
    
    fallbacks = []

    # 2. Secondary: Claude 3.5 Sonnet (if key exists)
    # Using ChatOpenAI compatible interface or specific Anthropic class
    # Assuming standard LangChain setup. If API key missing, we skip.
    if os.getenv("ANTHROPIC_API_KEY"):
         try:
             claude = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=temperature)
             fallbacks.append(claude)
         except Exception as e:
             logger.warning(f"Could not initialize Claude fallback: {e}")

    # 3. Tertiary: Llama 3 (via Groq)
    if os.getenv("GROQ_API_KEY"):
        try:
            from langchain_groq import ChatGroq
            llama = ChatGroq(model_name="llama3-70b-8192", temperature=temperature)
            fallbacks.append(llama)
        except ImportError:
             logger.warning("langchain_groq not installed. Skipping Groq fallback.")
        except Exception as e:
             logger.warning(f"Could not initialize Groq fallback: {e}")

    if not fallbacks:
        return primary
    
    # Use LangChain's native fallback feature for best compatibility
    return primary.with_fallbacks(fallbacks)
