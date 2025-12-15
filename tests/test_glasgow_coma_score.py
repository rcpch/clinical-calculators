from __future__ import annotations

from calculators.glasgow_coma_score import calculate


def test_basic_calculation():
    """Test basic calculator functionality."""
    result = calculate(
        {
            "eyes": 2,
            "voice": 2,
            "motor": 2,
        }
    )
    assert result.result is not None
    assert result.metadata is not None


def test_response_structure():
    """Test that response has required fields."""
    result = calculate(
        {
            "eyes": 2,
            "voice": 2,
            "motor": 2,
        }
    )
    assert hasattr(result, "result")
    assert hasattr(result, "working")
    assert hasattr(result, "interpretation")
    assert hasattr(result, "metadata")
    assert hasattr(result, "reference")

