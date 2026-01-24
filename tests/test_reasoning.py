import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, HallucinationMetric
from agents.reasoning_agent import reasoning_node

def test_reasoning_agent_insight(mock_travel_state):
    """
    Test if the Reasoning Agent produces faithful and relevant insights.
    """
    # 1. Run the agent
    result = reasoning_node(mock_travel_state)
    agent_note = result.get("trip_analysis", "")
    
    # 2. Define Context (The data the agent saw)
    context = [
        f"Weather: {mock_travel_state.weather_summary}",
        f"Flights available: {len(mock_travel_state.flights)}",
        f"Top flight price: {mock_travel_state.flights[0]['price']}"
    ]
    
    test_case = LLMTestCase(
        input="Analyze this trip plan and provide insights.",
        actual_output=agent_note,
        retrieval_context=context
    )
    
    # 3. Metrics
    faithfulness = FaithfulnessMetric(threshold=0.7) # Are facts in the note supported by context?
    relevancy = AnswerRelevancyMetric(threshold=0.7) # Is the note helpful?
    hallucination = HallucinationMetric(threshold=0.5)
    
    assert_test(test_case, [faithfulness, relevancy, hallucination])
