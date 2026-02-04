import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.params import LLMTestCaseParams

# Import the chain logic from the agent
# We need to make sure we can import 'chain' or reconstruct it
import os
os.environ["OPENAI_API_KEY"] = "sk-test-mock-key"
from agents.flight_api_agent import chain, AirlinePreferences

def test_airline_preference_extraction():
    """
    Regression Test: Ensure 'Delta' preference is correctly extracted.
    """
    user_memory = "I strictly fly Delta and hate Spirit airlines."
    
    # 1. Run the actual agent chain
    result = chain.invoke({"memories": user_memory})
    print(f"DEBUG: Agent Output: {result}")
    
    # 2. Strict Assertion (Code Level)
    # The output should match the Pydantic schema structure
    # result is a dict because the chain ends with JsonOutputParser
    assert "Delta" in result.get("preferred_airlines", []), "Delta should be in preferred_airlines"
    assert "Spirit" in result.get("excluded_airlines", []), "Spirit should be in excluded_airlines"

    # 3. Semantic Assertion (DeepEval)
    # We use GEval to check if the extracted JSON is faithful to the input memory
    
    test_case = LLMTestCase(
        input=user_memory,
        actual_output=str(result),
        expected_output='{"preferred_airlines": ["Delta"], "excluded_airlines": ["Spirit"]}'
    )
    
    consistency_metric = GEval(
        name="Consistency",
        criteria="Is the extracted JSON strictly consistent with the user's stated preferences?",
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        threshold=0.7
    )
    
    assert_test(test_case, [consistency_metric])
