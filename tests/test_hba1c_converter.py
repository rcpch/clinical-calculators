from __future__ import annotations

import math

from calculators.hba1c_converter import HbA1cRequest, calculate


def test_hba1c_percent_to_mmol_mol():
    """Test conversion from percentage to mmol/mol."""
    resp = calculate({"value": 7.5, "input_unit": "percent"})
    # (7.5 - 2.15) × 10.929 = 58.5
    assert abs(resp.result - 58.5) < 0.1
    assert resp.result_unit == "mmol/mol"
    assert resp.input_value == 7.5
    assert resp.input_unit == "percent"
    assert resp.metadata["calculator_name"] == "hba1c_converter"


def test_hba1c_mmol_mol_to_percent():
    """Test conversion from mmol/mol to percentage."""
    resp = calculate({"value": 58.5, "input_unit": "mmol_mol"})
    # (58.5 / 10.929) + 2.15 = 7.5
    assert abs(resp.result - 7.5) < 0.1
    assert resp.result_unit == "percent"
    assert resp.input_value == 58.5
    assert resp.input_unit == "mmol_mol"


def test_hba1c_round_trip():
    """Test that converting back and forth preserves the value."""
    # Start with 6.5% (diabetes threshold)
    resp1 = calculate({"value": 6.5, "input_unit": "percent"})
    mmol_mol_result = resp1.result
    
    # Convert back to percentage
    resp2 = calculate({"value": mmol_mol_result, "input_unit": "mmol_mol"})
    assert abs(resp2.result - 6.5) < 0.1


def test_hba1c_normal_range():
    """Test normal range interpretation."""
    resp = calculate({"value": 5.5, "input_unit": "percent"})
    assert "Normal range" in resp.interpretation


def test_hba1c_diabetes_range():
    """Test diabetes diagnosis threshold interpretation."""
    resp = calculate({"value": 48, "input_unit": "mmol_mol"})
    assert "Diabetes" in resp.interpretation


def test_invalid_percentage_range():
    """Test that invalid percentage values are rejected."""
    try:
        calculate({"value": 25, "input_unit": "percent"})
        assert False, "Should have raised ValueError"
    except Exception as e:
        assert "percentage must be in" in str(e)


def test_invalid_mmol_mol_range():
    """Test that invalid mmol/mol values are rejected."""
    try:
        calculate({"value": 250, "input_unit": "mmol_mol"})
        assert False, "Should have raised ValueError"
    except Exception as e:
        assert "mmol/mol must be in" in str(e)


def test_hba1c_working_field():
    """Test that working field shows the calculation."""
    resp = calculate({"value": 7.0, "input_unit": "percent"})
    assert "7.0" in resp.working
    assert "10.929" in resp.working
