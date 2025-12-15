def calculate(params):
    """Subtract two numbers."""
    result = params["a"] - params["b"]
    return {
        "result": result,
        "working": f"{params["a"]} - {params["b"]} = {result}",
        "interpretation": "Difference calculated successfully"
    }
