from calculators.multiply import calculate

def test_multiply():
    result = calculate({"x": 6, "y": 7})
    assert result["result"] == 42

def test_multiply_zero():
    result = calculate({"x": 5, "y": 0})
    assert result["result"] == 0
