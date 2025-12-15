#!/usr/bin/env python3
"""Test the calculator generator endpoint."""

import json
import requests

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

# Test valid spec
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
    if data['validation_errors']:
        print("Validation warnings:")
        for error in data['validation_errors']:
            print(f"  - {error['field']}: {error['message']} ({error['severity']})")
    print("\nGenerated Python code (first 500 chars):")
    print(data['python_code'][:500])
else:
    print(f"Error: {response.json()}")

print("\n" + "="*80)

# Test invalid spec
print("\nTesting invalid specification (missing logic)...")
invalid_spec = """[calculator]
name = "no_logic"
description = "Missing logic"

[[inputs]]
name = "value"
type = "number"
"""

response = requests.post(
    "http://localhost:8000/generate-calculator",
    json={"spec": invalid_spec},
)

print(f"Status: {response.status_code}")
data = response.json()
print(f"Detail: {json.dumps(data, indent=2)}")
