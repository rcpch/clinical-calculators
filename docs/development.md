# Development Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Git

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/rcpch/clinical-calculators.git
cd clinical-calculators
```

### Start Development Environment

```bash
./s/dev.sh up
```

This will start the API server at `http://localhost:8000`

### Run Tests

```bash
docker compose run --rm api pytest
```

### View API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Project Structure

```
clinical-calculators/
├── api/              # FastAPI application
├── calculators/      # Calculator implementations
├── core/            # Core utilities and loaders
├── tests/           # Test suite
├── site/            # Web client (GitHub Pages)
├── docs/            # Documentation (markdown)
└── static/          # Static assets
```

## Standardization

All calculators are standardized with docstrings that define all input parameters and the structure of outputs in TOML format.

### CalculatorRequest Base Class

All calculator request models should subclass the generic `CalculatorRequest` base class, defined in `core/request/request.py`. This provides a consistent structure and a place for shared logic or metadata.

Example:

```python
from core.request.request import CalculatorRequest
from pydantic import Field, root_validator

class BMIRequest(CalculatorRequest):
    unit_system: Literal["metric", "imperial"]
    weight: float = Field(..., gt=0, description="Weight in kg or lb (UCUM)")
    height: float = Field(..., gt=0, description="Height in m or in (UCUM)")
    # ...validators...
```

### CalculationResponse Standard

All calculators return a response using the generic `CalculationResponse` class from `core/response/response.py`:

- `result`: The main result of the calculation
- `working`: Step-by-step calculation or details
- `interpretation`: Interpretation of the result (e.g., clinical meaning)
- `reference`: Reference or source for the calculation
- `metadata`: Additional metadata (timestamp, version, calculator_name, etc.)

Example:

```python
from core.response.response import CalculationResponse

def calculate(params: ...):
    # ... calculation logic ...
    return CalculationResponse(
        result=...,
        working=...,
        interpretation=...,
        reference="...",
        metadata={...},
    )
```

### UCUM Codes for Units

All units should use [UCUM](https://ucum.org/trac) codes for clarity and interoperability:

- Weight: `kg` (UCUM: `kg`), `lb` (UCUM: `[lb_av]`)
- Height: `m` (UCUM: `m`), `in` (UCUM: `[in_i]`)
- Unit system: `metric` for metric, `imperial` for imperial

## Creating a New Calculator

### Step-by-Step Guide

1. **Create a new file** in `calculators/` (e.g., `my_calculator.py`)
2. **Add TOML docstring** at the top defining inputs and outputs
3. **Define Pydantic models**:
   - Request class inheriting from `CalculatorRequest`
   - Response using `CalculationResponse`
4. **Implement `calculate()` function** with calculation logic
5. **Add comprehensive tests** in `tests/`
6. **Update dependencies** in `requirements.txt` if needed

### Example Calculator File Structure

```python
"""
# Calculator Name

## 📂 Description
[Description of what the calculator does]

## 📂 Configuration

[inputs]
- name: parameter1
  type: number
  unit: kg
  required: true
  min: 0.0
  max: 500.0
  description: Description of parameter1

[dependencies]
  scipy

## 📂 Output (TOML-style)

[result]
  type: number
  description: Main result

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  description: Clinical interpretation

[reference]
  type: string
  default: "Source Guidelines"

## 📂 Validation Rules
- Parameter1 must be > 0
- Parameter2 must be in range

## 📂 Usage
CLI: calc run my_calculator --params '{...}'
API: POST /calculate {...}
"""

from core.request.request import CalculatorRequest
from core.response.response import CalculationResponse
from pydantic import Field

class MyCalculatorRequest(CalculatorRequest):
    parameter1: float = Field(..., gt=0)
    # Add validators as needed

def calculate(params: dict) -> CalculationResponse:
    request = MyCalculatorRequest(**params)
    
    # Calculation logic here
    result = ...
    
    return CalculationResponse(
        result=result,
        working="...",
        interpretation="...",
        reference="...",
        metadata={...}
    )
```

See [Calculator Specifications](calculator-specs.md) for complete details.

## Development Scripts

- `./s/dev.sh up` - Start containers
- `./s/dev.sh down` - Stop containers
- `./s/dev.sh logs` - View logs
- `./s/dev.sh rebuild` - Rebuild containers
- `./s/dev.sh sh` - Open shell in API container

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests
4. Submit a pull request to the `live` branch
