import pytest
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval, AnswerRelevancyMetric, FaithfulnessMetric, ContextualPrecisionMetric
from state import TravelState

@pytest.fixture
def mock_travel_state():
    return TravelState(
        origin="New York",
        destination="London",
        start_date="2025-06-01",
        end_date="2025-06-07",
        user_preferences=["I preferred Delta over British Airways", "I hate early morning flights"],
        weather_summary="Sunny with a chance of rain.",
        flights=[
            {"airline": "Delta", "price": 500, "departure": "10:00"},
            {"airline": "British Airways", "price": 450, "departure": "06:00"},
            {"airline": "United", "price": 600, "departure": "14:00"}
        ]
    )

@pytest.fixture
def mock_itinerary_input():
    return """
    Day 1: Arrive in London. Check into The Ritz.
    Day 2: Visit Buckingham Palace and British Museum.
    Day 3: Day trip to Oxford.
    """
