from utils.retry import with_retry
from utils.llm_factory import get_llm, FallbackLLM
from langchain.schema import HumanMessage
import time
import os

# Mock environment variables for testing logic without real calls
os.environ["OPENAI_API_KEY"] = "sk-test-key-mock"

def test_retry_logic():
    print("\n--- Testing Retry Logic ---")
    
    # Define a failing function
    @with_retry(max_retries=2, backoff_factor=1)
    def failing_function():
        print("Calling failing function...")
        raise ValueError("Simulated network failure")
        
    try:
        failing_function()
    except ValueError:
        print("✅ Correctly raised exception after retries.")
    except Exception as e:
        print(f"❌ Unexpected exception: {e}")

def test_fallback_logic():
    print("\n--- Testing LLM Fallback ---")
    # This requires API keys, so we'll just verify the factory returns an object
    # capable of fallback configuration
    
    llm = get_llm(temperature=0)
    print(f"Got primary LLM: {llm}")
    
    if hasattr(llm, "with_fallbacks") or hasattr(llm, "fallbacks") or isinstance(llm, FallbackLLM):
        print("✅ LLM configured with potential fallbacks (native or custom).")
    else:
        # If it's a raw ChatOpenAI object, it might be because other keys aren't set.
        # Check if we should have had fallbacks
        if os.getenv("ANTHROPIC_API_KEY") or os.getenv("GROQ_API_KEY"):
             print("⚠️ Warning: Keys present but fallback wrapper not detected. Check llm_factory logic.")
        else:
             print("ℹ️ No secondary keys found, so simple LLM return is expected.")

if __name__ == "__main__":
    test_retry_logic()
    test_fallback_logic()
