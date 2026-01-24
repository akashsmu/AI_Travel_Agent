import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import ContextualPrecisionMetric, GEval, ContextualRecallMetric
from agents.flight_api_agent import fetch_flights_from_api
from deepeval.params import LLMTestCaseParams

def test_flight_personalization(mock_travel_state):
    """
    Test if the Flight Agent correctly ranks flights based on user preferences.
    """
    # 1. Run the actual agent logic (mocking the search part to use state.flights)
    # in this case, fetch_flights_from_api re-sorts the existing list if prefs exist
    updated_state = fetch_flights_from_api(mock_travel_state)
    
    top_flight = updated_state.flights[0]
    
    # 2. Define the Test Case
    test_case = LLMTestCase(
        input="Find flights from NY to London",
        actual_output=f"Top recommendation: {top_flight['airline']} at {top_flight['departure']}",
        retrieval_context=[p for p in mock_travel_state.user_preferences]
    )
    
    # 3. Define Metrics
    
    # Custom GEval to check if Delta is favored
    preference_metric = GEval(
        name="Preference Adherence",
        criteria="Determine if the output favors Delta airlines as requested in the context.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT]
    )
    
    # Contextual Precision: Did we use the relevant memory?
    precision_metric = ContextualPrecisionMetric(threshold=0.7)
    
    # 4. Assert
    assert_test(test_case, [preference_metric, precision_metric])
