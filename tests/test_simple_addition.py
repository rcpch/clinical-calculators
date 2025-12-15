from calculators.simple_addition import calculate

def test_addition():
    result = calculate({"a": 5, "b": 3})
    assert result["result"] == 8
    assert "5 + 3 = 8" in result["working"]

def test_negative_numbers():
    result = calculate({"a": -5, "b": 3})
    assert result["result"] == -2
