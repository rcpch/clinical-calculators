from calculators.divide import calculate

def test_divide():
    result = calculate({"a": 10, "b": 2})
    assert result["result"] == 5.0

def test_divide_by_zero():
    result = calculate({"a": 10, "b": 0})
    assert result["result"] is None
