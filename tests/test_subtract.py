from calculators.subtract import calculate

def test_subtract():
    result = calculate({"a": 10, "b": 3})
    assert result["result"] == 7
    assert "10 - 3 = 7" in result["working"]

def test_subtract_negative():
    result = calculate({"a": 5, "b": 10})
    assert result["result"] == -5
