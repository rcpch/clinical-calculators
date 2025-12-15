def calculate(params):
    """Add two numbers."""
    result = params["a"] + params["b"]
    return {
        "result": result,
        "working": f"{params["a"]} + {params["b"]} = {result}",
        "interpretation": "Sum calculated successfully"
    }
