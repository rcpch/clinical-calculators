def calculate(params):
    """Calculate Body Mass Index."""
    height_m = params["height_cm"] / 100
    bmi = params["weight_kg"] / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "result": round(bmi, 1),
        "working": f"BMI = {params["weight_kg"]}kg / ({height_m}m)² = {bmi:.1f}",
        "interpretation": category
    }
