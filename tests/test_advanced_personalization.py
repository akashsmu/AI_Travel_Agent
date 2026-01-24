import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from agents.flight_api_agent import fetch_flights_from_api
from deepeval.params import LLMTestCaseParams

def test_conflict_resolution(mock_conflict_state):
    """
    Test how the agent handles conflicting constraints (Brand vs Budget).
    """
    # 1. Run Agent
    updated_state = fetch_flights_from_api(mock_conflict_state)
    top_flight = updated_state.flights[0]
    
    # 2. Define Test Case
    # We expect the agent to likely filter out the $600 Delta flight because max_price is $300, 
    # despite the "Strictly Delta" preference. Or strictly adhere to brand.
    # The Eval determines if the choice was *Reasonable* based on the inputs.
    
    test_case = LLMTestCase(
        input="Find flights under $300. Helper Context: I strictly fly Delta.",
        actual_output=f"Selected: {top_flight['airline']} for ${top_flight['price']}",
        retrieval_context=[
            "User Constraint: Max 300 USD",
            "User Preference: Strictly Delta",
            f"Option A: Delta $600",
            f"Option B: Spirit $200"
        ]
    )
    
    resolution_metric = GEval(
        name="Conflict Resolution Logic",
        criteria="""
        Determine if the selected flight is a logical trade-off. 
        - If budget was strictly respected, Spirit/JetBlue is valid.
        - If brand was strictly respected, Delta is valid (but ignores budget).
        - The output should NOT be random.
        """,
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT]
    )
    
    assert_test(test_case, [resolution_metric])
