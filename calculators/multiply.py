def calculate(params):
    """Multiply two numbers."""
    result = params["x"] * params["y"]
    return {
        "result": result,
        "working": f"{params["x"]} × {params["y"]} = {result}",
        "interpretation": "Product calculated successfully"
    }
