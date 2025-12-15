# Example TOML specification for testing the generator

VALID_SPEC = """
[calculator]
name = "simple_add"
description = "A simple calculator that adds two numbers"
reference = "Basic arithmetic"
logic = '''
result = request.num1 + request.num2
working = f"{request.num1} + {request.num2} = {result}"
interpretation = f"The sum of {request.num1} and {request.num2} is {result}"
'''

[inputs]
- name: num1
  type: number
  description: First number
  required: true
  min: 0

- name: num2
  type: number
  description: Second number
  required: true
  min: 0
"""

INVALID_SPEC_MISSING_NAME = """
[calculator]
description = "Missing name field"

[inputs]
- name: value
  type: number
"""

INVALID_SPEC_BAD_INPUT_NAME = """
[calculator]
name = "test_calc"
description = "Test calculator"

[inputs]
- name: 1invalid
  type: number
"""

INVALID_SPEC_NO_LOGIC = """
[calculator]
name = "no_logic"
description = "Calculator without logic"

[inputs]
- name: value
  type: number
"""
