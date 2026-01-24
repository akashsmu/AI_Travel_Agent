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
def mock_conflict_state():
    """
    Scenario: User loves Delta but has a low budget.
    Delta is expensive ($600), Spirit is cheap ($200). Max budget is $300.
    """
    return TravelState(
        origin="New York",
        destination="Miami",
        max_flight_price=300.0,
        user_preferences=["I strictly fly Delta"],
        flights=[
            {"airline": "Delta", "price": 600, "departure": "10:00"},
            {"airline": "Spirit", "price": 200, "departure": "06:00"},
            {"airline": "JetBlue", "price": 290, "departure": "14:00"}
        ]
    )

@pytest.fixture
def mock_empty_state():
    """
    Scenario: User searches but no results found initially.
    """
    state = TravelState(
        origin="Nowhere",
        destination="Nowhere",
        retry_count=0
    )
    state.flights = []
    state.accommodations = []
    return state
