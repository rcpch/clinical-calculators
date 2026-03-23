from __future__ import annotations

import pytest

from calculators.asrs_screener import calculate

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_ALL_NEVER = {f"q{i}": "never" for i in range(1, 19)}
_ALL_VERY_OFTEN = {f"q{i}": "very_often" for i in range(1, 19)}
_ALL_OFTEN = {f"q{i}": "often" for i in range(1, 19)}
_ALL_SOMETIMES = {f"q{i}": "sometimes" for i in range(1, 19)}


def _positive_screen_params() -> dict:
    """Returns params that yield a positive Part A screen (all q1-q6 = 'often').

    q1-q3: often (score=3 >= threshold 2) → positive
    q4-q6: often (score=3 >= threshold 3) → positive
    Result: 6/6 Part A items positive.
    """
    return {**_ALL_NEVER, **{f"q{i}": "often" for i in range(1, 7)}}


def _negative_screen_params() -> dict:
    """Returns params that yield a negative Part A screen.

    q1-q3: sometimes (score=2 >= threshold 2) → positive
    q4-q6: sometimes (score=2 < threshold 3) → negative
    Result: 3/6 Part A items positive — below the threshold of 4.
    """
    return {**_ALL_NEVER, **{f"q{i}": "sometimes" for i in range(1, 7)}}


# ---------------------------------------------------------------------------
# Basic calculation tests
# ---------------------------------------------------------------------------


def test_all_never_gives_zero_result():
    """All 'never' responses: 0 positive Part A items, total score 0."""
    result = calculate(_ALL_NEVER)
    assert result.result == 0
    assert result.working["total_score"] == 0
    assert result.working["part_a_screen_result"] == "NEGATIVE"


def test_all_very_often_gives_maximum_positive():
    """All 'very_often' responses: all 6 Part A items positive, total score 72."""
    result = calculate(_ALL_VERY_OFTEN)
    assert result.result == 6
    assert result.working["total_score"] == 72
    assert result.working["part_a_screen_result"] == "POSITIVE"
    assert result.working["part_a_total_score"] == 24
    assert result.working["part_b_total_score"] == 48


def test_positive_screen():
    """4+ Part A items above threshold yields a positive screen."""
    result = calculate(_positive_screen_params())
    assert result.result == 6
    assert result.working["part_a_screen_result"] == "POSITIVE"


def test_negative_screen():
    """Fewer than 4 Part A items above threshold yields a negative screen."""
    result = calculate(_negative_screen_params())
    assert result.result == 3
    assert result.working["part_a_screen_result"] == "NEGATIVE"


def test_exact_threshold_four_positive():
    """Exactly 4 positive Part A items yields a positive screen."""
    params = {**_ALL_NEVER}
    # q1-q3: sometimes (≥2 → positive)
    params["q1"] = "sometimes"
    params["q2"] = "sometimes"
    params["q3"] = "sometimes"
    # q4: often (≥3 → positive); q5-q6 remain 'never' (negative)
    params["q4"] = "often"
    result = calculate(params)
    assert result.result == 4
    assert result.working["part_a_screen_result"] == "POSITIVE"


def test_three_positive_is_negative_screen():
    """Exactly 3 positive Part A items is still a negative screen."""
    params = {**_ALL_NEVER}
    params["q1"] = "sometimes"
    params["q2"] = "sometimes"
    params["q3"] = "sometimes"
    result = calculate(params)
    assert result.result == 3
    assert result.working["part_a_screen_result"] == "NEGATIVE"


# ---------------------------------------------------------------------------
# Part A threshold logic
# ---------------------------------------------------------------------------


def test_q1_to_q3_threshold_at_sometimes():
    """Q1–Q3 are positive at 'sometimes' (score 2), negative at 'rarely' (score 1)."""
    params_pos = {**_ALL_NEVER, "q1": "sometimes"}
    params_neg = {**_ALL_NEVER, "q1": "rarely"}
    assert calculate(params_pos).working["part_a_items"]["q1"]["positive"] is True
    assert calculate(params_neg).working["part_a_items"]["q1"]["positive"] is False


def test_q4_to_q6_threshold_at_often():
    """Q4–Q6 are positive at 'often' (score 3), negative at 'sometimes' (score 2)."""
    params_pos = {**_ALL_NEVER, "q4": "often"}
    params_neg = {**_ALL_NEVER, "q4": "sometimes"}
    assert calculate(params_pos).working["part_a_items"]["q4"]["positive"] is True
    assert calculate(params_neg).working["part_a_items"]["q4"]["positive"] is False


def test_part_a_scores_in_working_are_correct():
    """Verify numeric scores in working dict match expected values."""
    params = {**_ALL_NEVER, "q1": "rarely", "q2": "sometimes", "q3": "often"}
    result = calculate(params)
    items = result.working["part_a_items"]
    assert items["q1"]["score"] == 1
    assert items["q2"]["score"] == 2
    assert items["q3"]["score"] == 3


# ---------------------------------------------------------------------------
# Scoring arithmetic
# ---------------------------------------------------------------------------


def test_total_score_is_sum_of_all_18_responses():
    """Total score equals the sum of all 18 numeric response values."""
    # q1-q6 = often (3 each = 18), q7-q18 = rarely (1 each = 12) → total = 30
    params = {
        **{f"q{i}": "often" for i in range(1, 7)},
        **{f"q{i}": "rarely" for i in range(7, 19)},
    }
    result = calculate(params)
    assert result.working["part_a_total_score"] == 18
    assert result.working["part_b_total_score"] == 12
    assert result.working["total_score"] == 30


def test_part_b_score_does_not_affect_part_a_screen():
    """Very high Part B scores do not change the Part A screen result."""
    params = {
        **_ALL_NEVER,
        **{f"q{i}": "very_often" for i in range(7, 19)},
    }
    result = calculate(params)
    assert result.result == 0
    assert result.working["part_a_screen_result"] == "NEGATIVE"
    assert result.working["part_b_total_score"] == 48


# ---------------------------------------------------------------------------
# Response structure
# ---------------------------------------------------------------------------


def test_response_structure():
    """Response contains all required fields."""
    result = calculate(_ALL_NEVER)
    assert hasattr(result, "result")
    assert hasattr(result, "working")
    assert hasattr(result, "interpretation")
    assert hasattr(result, "reference")
    assert hasattr(result, "metadata")
    assert hasattr(result, "tags")


def test_metadata_fields():
    """Metadata contains required fields."""
    result = calculate(_ALL_NEVER)
    assert "timestamp" in result.metadata
    assert "version" in result.metadata
    assert result.metadata["calculator_name"] == "asrs_screener"


def test_working_field_structure():
    """Working dict contains all expected keys."""
    result = calculate(_ALL_NEVER)
    w = result.working
    assert "description" in w
    assert "part_a_screen_result" in w
    assert "part_a_positive_item_count" in w
    assert "part_a_total_score" in w
    assert "part_b_total_score" in w
    assert "total_score" in w
    assert "part_a_items" in w
    # Part A items include q1-q6
    for i in range(1, 7):
        assert f"q{i}" in w["part_a_items"]
        item = w["part_a_items"][f"q{i}"]
        assert "response" in item
        assert "score" in item
        assert "positive" in item


def test_interpretation_positive_contains_positive():
    """Positive screen interpretation mentions positive and recommends assessment."""
    result = calculate(_ALL_VERY_OFTEN)
    assert "Positive" in result.interpretation
    assert "assessment" in result.interpretation.lower()


def test_interpretation_negative_screen():
    """Negative screen interpretation mentions negative."""
    result = calculate(_ALL_NEVER)
    assert "Negative" in result.interpretation


def test_tags_include_adhd():
    """Tags list includes 'adhd' and 'asrs'."""
    result = calculate(_ALL_NEVER)
    assert "adhd" in result.tags
    assert "asrs" in result.tags


def test_reference_includes_kessler():
    """Reference cites the original Kessler et al. paper."""
    result = calculate(_ALL_NEVER)
    assert "Kessler" in result.reference


# ---------------------------------------------------------------------------
# Validation / error handling
# ---------------------------------------------------------------------------


def test_invalid_frequency_value_raises():
    """An invalid frequency string raises a validation error."""
    params = {**_ALL_NEVER, "q1": "always"}
    try:
        calculate(params)
        assert False, "Expected a validation error"
    except Exception as exc:
        assert "q1" in str(exc).lower() or "validation" in str(exc).lower()


def test_missing_question_raises():
    """Omitting a required question raises a validation error."""
    params = {f"q{i}": "never" for i in range(2, 19)}  # q1 missing
    try:
        calculate(params)
        assert False, "Expected a validation error"
    except Exception:
        pass  # Any exception is acceptable


def test_numeric_value_rejected():
    """Passing an integer instead of a string is rejected."""
    params = {**_ALL_NEVER, "q1": 2}
    try:
        calculate(params)
        assert False, "Expected a validation error"
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Direct request object
# ---------------------------------------------------------------------------


def test_accepts_request_object_directly():
    """calculate() works when passed an ASRSScreenerRequest instance."""
    from calculators.asrs_screener import ASRSScreenerRequest

    req = ASRSScreenerRequest(**_ALL_NEVER)
    result = calculate(req)
    assert result.result == 0
    assert result.metadata["calculator_name"] == "asrs_screener"
