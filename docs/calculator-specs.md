# Calculator Specifications

This guide explains how to create new calculators for the RCPCH Clinical Calculators platform.

## Overview

Each calculator is a Python module that:
1. Defines input and output data models using Pydantic
2. Implements a `calculate()` function with the calculation logic
3. Provides documentation in a structured TOML format

## Validation

Validation is compatible with FastAPI and uses FastAPI request and response classes for easy integration with APIs. These validation classes are specific to each calculator and defined in the same file.

## Instantiation

Whichever way the calculator is accessed (API/pip install or CLI), the requests and responses follow the same pattern - all inputs are validated against the structure provided in the TOML using the FastAPI Response and Request classes defined in the calculator file. There is a `cli` folder, an `api` folder and a `main.py`.

## Templates

The project includes templates with form templates for each field in basic Jinja that can be used with whichever framework you choose.

## Usage Pattern

Calling each function should involve only a single function call, with the parameters as defined in the docstring of the relevant calculator file. The response similarly should follow the same structure as defined in the TOML coupled with the metadata which are generic to all requests.

## File Structure

Calculators are located in the `calculators/` directory:

```
calculators/
├── __init__.py
├── bmi.py
├── hba1c_converter.py
└── your_calculator.py
```

## Creating a Calculator

### 1. Define Data Models

Use Pydantic v1 models to define inputs and outputs:

```python
from pydantic import BaseModel, Field, validator

class YourCalculatorRequest(BaseModel):
    """Input parameters for the calculator."""
    
    parameter1: float = Field(
        ...,
        description="Description of parameter1",
        gt=0  # Validation: must be greater than 0
    )
    parameter2: str = Field(
        ...,
        description="Description of parameter2"
    )
    
    @validator('parameter2')
    def validate_parameter2(cls, v):
        """Custom validation logic."""
        if v not in ['option1', 'option2']:
            raise ValueError('parameter2 must be option1 or option2')
        return v

class YourCalculatorResponse(BaseModel):
    """Output from the calculator."""
    
    result: float = Field(
        ...,
        description="The calculated result"
    )
    interpretation: str = Field(
        ...,
        description="Human-readable interpretation"
    )
```

### 2. Implement the Calculate Function

```python
def calculate(inputs: YourCalculatorRequest) -> YourCalculatorResponse:
    """
    Perform the calculation.
    
    Args:
        inputs: Validated input parameters
        
    Returns:
        Calculated results
    """
    # Your calculation logic here
    result = inputs.parameter1 * 2.5
    
    # Generate interpretation
    if result < 10:
        interpretation = "Low"
    elif result < 20:
        interpretation = "Normal"
    else:
        interpretation = "High"
    
    return YourCalculatorResponse(
        result=result,
        interpretation=interpretation
    )
```

### 3. Add Documentation

Include a module-level docstring with structured documentation:

```python
"""
Your Calculator Name

Description of what this calculator does.

[inputs]
parameter1 = "float: Description of parameter1 (e.g., in meters)"
parameter2 = "str: Description of parameter2 (must be option1 or option2)"

[outputs]
result = "float: The calculated result"
interpretation = "str: Human-readable interpretation of the result"

[example]
inputs = {"parameter1": 5.0, "parameter2": "option1"}
result = {"result": 12.5, "interpretation": "Normal"}

[references]
1. Reference to relevant medical literature or guidelines
2. Another reference if applicable
"""
```

## Example: BMI Calculator

Here's the complete BMI calculator as a reference:

```python
"""
Body Mass Index (BMI) Calculator

Calculate BMI from height and weight, and provide weight category classification.

[inputs]
height_m = "float: Height in meters"
weight_kg = "float: Weight in kilograms"

[outputs]
bmi = "float: Calculated BMI value"
category = "str: Weight category (Underweight, Normal weight, Overweight, Obese)"
healthy_weight_range_kg = "str: Recommended healthy weight range"

[example]
inputs = {"height_m": 1.75, "weight_kg": 70}
result = {"bmi": 22.86, "category": "Normal weight", "healthy_weight_range_kg": "56.7 - 76.6"}

[references]
1. WHO BMI Classification
"""

from pydantic import BaseModel, Field, validator

class BmiRequest(BaseModel):
    height_m: float = Field(..., description="Height in meters", gt=0)
    weight_kg: float = Field(..., description="Weight in kilograms", gt=0)

class BmiResponse(BaseModel):
    bmi: float = Field(..., description="Calculated BMI")
    category: str = Field(..., description="Weight category")
    healthy_weight_range_kg: str = Field(..., description="Healthy weight range")

def calculate(inputs: BmiRequest) -> BmiResponse:
    bmi = inputs.weight_kg / (inputs.height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    min_healthy_weight = 18.5 * (inputs.height_m ** 2)
    max_healthy_weight = 24.9 * (inputs.height_m ** 2)
    healthy_range = f"{min_healthy_weight:.1f} - {max_healthy_weight:.1f}"
    
    return BmiResponse(
        bmi=round(bmi, 2),
        category=category,
        healthy_weight_range_kg=healthy_range
    )
```

## Testing

Create comprehensive tests in the `tests/` directory:

```python
import pytest
from calculators.your_calculator import calculate, YourCalculatorRequest

def test_basic_calculation():
    """Test basic calculation."""
    result = calculate(YourCalculatorRequest(
        parameter1=5.0,
        parameter2="option1"
    ))
    assert result.result == 12.5
    assert result.interpretation == "Normal"

def test_validation():
    """Test input validation."""
    with pytest.raises(ValueError):
        YourCalculatorRequest(
            parameter1=-1.0,  # Invalid: must be > 0
            parameter2="option1"
        )

def test_edge_cases():
    """Test edge cases."""
    # Test boundary conditions
    result = calculate(YourCalculatorRequest(
        parameter1=0.1,
        parameter2="option1"
    ))
    assert result.result == 0.25
```

## Best Practices

### Input Validation

- Use Pydantic validators for type checking and constraints
- Provide clear error messages for invalid inputs
- Consider edge cases and boundary conditions

### Calculation Logic

- Keep calculations simple and readable
- Add comments for complex formulas
- Round results appropriately for clinical use
- Handle special cases (e.g., division by zero)

### Output Formatting

- Return precise numeric values
- Provide human-readable interpretations
- Include relevant ranges or categories
- Consider units and significant figures

### Documentation

- Write clear, concise descriptions
- Include all input/output parameters
- Provide realistic examples
- Reference clinical guidelines or literature

### Testing

- Test normal cases
- Test edge cases and boundaries
- Test error handling
- Test round-trip conversions (if applicable)
- Aim for high code coverage

## Registration

Calculators are automatically discovered by the API through the `calculators/` directory. No manual registration is required.

## Deployment

1. Create your calculator file in `calculators/`
2. Write comprehensive tests in `tests/`
3. Run tests: `./s/dev.sh pytest`
4. Submit a pull request to the `live` branch
5. Once merged, the calculator will be deployed automatically

## Common Patterns

### Unit Conversion

```python
def calculate(inputs: Request) -> Response:
    # Convert input units if needed
    value_in_standard_units = inputs.value * CONVERSION_FACTOR
    
    # Perform calculation
    result = compute(value_in_standard_units)
    
    # Convert result back if needed
    return Response(result=result / CONVERSION_FACTOR)
```

### Bidirectional Conversion

```python
def calculate(inputs: Request) -> Response:
    if inputs.value_a is not None:
        # Convert A to B
        value_b = inputs.value_a * FACTOR
        return Response(value_a=inputs.value_a, value_b=value_b)
    elif inputs.value_b is not None:
        # Convert B to A
        value_a = inputs.value_b / FACTOR
        return Response(value_a=value_a, value_b=inputs.value_b)
    else:
        raise ValueError("Must provide either value_a or value_b")
```

### Interpretation Logic

```python
def _interpret(value: float) -> str:
    """Generate clinical interpretation."""
    if value < THRESHOLD_LOW:
        return "Low"
    elif value < THRESHOLD_HIGH:
        return "Normal"
    else:
        return "High"
```

## Resources

- [Pydantic v1 Documentation](https://docs.pydantic.dev/1.10/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [RCPCH Development Guidelines](development.md)
