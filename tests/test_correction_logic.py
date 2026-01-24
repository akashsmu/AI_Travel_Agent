import pytest
from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import GEval
from deepeval.params import LLMTestCaseParams
from agents.correction_agent import correction_node

def test_correction_trigger(mock_empty_state):
    """
    Test if the Correction Agent correctly identifies a failure and modifies state.
    """
    # 1. Run Correction Node
    updates = correction_node(mock_empty_state)
    
    # 2. Check State Mutations (Deterministic)
    assert updates["retry_count"] == 1
    assert "last_error" in updates
    assert updates["trip_analysis"] is not None
    
    # 3. LLM Eval of the "Analysis Note"
    # Did the agent explain WHY it's correcting?
    test_case = LLMTestCase(
        input="Search returned 0 results.",
        actual_output=updates.get("trip_analysis", ""),
        retrieval_context=["Flights: []", "Hotels: []"]
    )
    
    explanation_quality = GEval(
        name="Correction Explanation",
        criteria="Check if the agent acknowledges the failure and proposes a valid fallback (e.g. broader search).",
        evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.RETRIEVAL_CONTEXT]
    )
    
    assert_test(test_case, [explanation_quality])
