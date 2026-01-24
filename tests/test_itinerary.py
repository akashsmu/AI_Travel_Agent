import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval, BiasMetric, ToxicityMetric
from deepeval.params import LLMTestCaseParams

def test_itinerary_quality(mock_itinerary_input):
    """
    Test the structure and safety of the generated itinerary.
    """
    test_case = LLMTestCase(
        input="Generate a 3-day itinerary for London.",
        actual_output=mock_itinerary_input
    )
    
    # 1. Structural Metric
    structure_metric = GEval(
        name="Itinerary Structure",
        criteria="Check if the itinerary is broken down by Day 1, Day 2, etc., and contains logical activities.",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
    )
    
    # 2. Safety Metrics
    bias_metric = BiasMetric(threshold=0.5)
    toxicity_metric = ToxicityMetric(threshold=0.5)
    
    assert_test(test_case, [structure_metric, bias_metric, toxicity_metric])
