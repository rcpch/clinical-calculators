def calculate(params):
    a = params["a"]
    b = params["b"]
    if b == 0:
        return {"result": None, "working": "Cannot divide by zero", "interpretation": "Error"}
    result = a / b
    return {
        "result": round(result, 2),
        "working": f"Division: {a} / {b}",
        "interpretation": "Success"
    }
