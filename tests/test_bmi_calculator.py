from calculators.bmi_calculator import calculate

def test_normal_weight():
    result = calculate({"height_cm": 170, "weight_kg": 70})
    assert result["result"] == 24.2
    assert result["interpretation"] == "Normal weight"

def test_underweight():
    result = calculate({"height_cm": 180, "weight_kg": 60})
    assert result["interpretation"] == "Underweight"
