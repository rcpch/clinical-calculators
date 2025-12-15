#!/usr/bin/env python3
"""Test the calculator generator endpoint."""

import json

import pytest

try:
    import requests
except ImportError:
    requests = None


def is_api_running():
    """Check if the API server is running."""
    if not requests:
        return False
    try:
        response = requests.get("http://localhost:8000/docs", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


# Valid specification
spec = """[calculator]
name = "simple_multiply"
description = "Multiplies two numbers together"
reference = "Basic arithmetic"
logic = "result = request.num1 * request.num2; working = f'{request.num1} × {request.num2} = {result}'; interpretation = f'The product is {result}'"

[[inputs]]
name = "num1"
type = "number"
description = "First number"
required = true
min = 0

[[inputs]]
name = "num2"
type = "number"
description = "Second number"
required = true
min = 0
"""

invalid_spec = """[calculator]
name = "no_logic"
description = "Missing logic"

[[inputs]]
name = "value"
type = "number"
"""


@pytest.mark.skipif(
    not is_api_running(), reason="API server not running on localhost:8000"
)
def test_valid_calculator_generation():
    """Test generating a calculator with valid specification."""
    response = requests.post(
        "http://localhost:8000/generate-calculator",
        json={"spec": spec},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["name"] == "simple_multiply"
    assert "python_code" in data
    assert len(data["python_code"]) > 0


@pytest.mark.skipif(
    not is_api_running(), reason="API server not running on localhost:8000"
)
def test_invalid_calculator_generation():
    """Test generating a calculator with invalid specification (missing logic)."""
    response = requests.post(
        "http://localhost:8000/generate-calculator",
        json={"spec": invalid_spec},
    )

    assert response.status_code in [400, 422]  # Bad request or validation error
    data = response.json()
    assert "detail" in data


# Manual test mode: run with python core/tests/test_generator_api.py
if __name__ == "__main__":
    print("Testing valid specification...")
    response = requests.post(
        "http://localhost:8000/generate-calculator",
        json={"spec": spec},
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Name: {data['name']}")
        print(f"Message: {data['message']}")
        if data["validation_errors"]:
            print("Validation warnings:")
            for error in data["validation_errors"]:
                print(f"  - {error['field']}: {error['message']} ({error['severity']})")
        print("\nGenerated Python code (first 500 chars):")
        print(data["python_code"][:500])
    else:
        print(f"Error: {response.json()}")

    print("\n" + "=" * 80)

    print("\nTesting invalid specification (missing logic)...")
    response = requests.post(
        "http://localhost:8000/generate-calculator",
        json={"spec": invalid_spec},
    )

    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Detail: {json.dumps(data, indent=2)}")
