# Skill: Create a New RCPCH Clinical Calculator

## Purpose

This skill guides an LLM through creating a fully compatible new clinical calculator for the RCPCH Clinical Calculators project. The end result is a calculator that works across all four surfaces: **Python package**, **REST API**, **CLI**, and **Web UI** — with zero additional registration or wiring required.

---

## Phase 0: Clarification Questions

Before writing any code, ask the user these questions to fully understand the calculator requirements. Adapt based on what the user has already provided.

### Required Information

1. **What does this calculator compute?**
   - Clinical purpose (e.g., "Convert HbA1c between percentage and mmol/mol")
   - The exact formula(s) or algorithm
   - Any conditional logic (branching based on inputs)

2. **What are the input parameters?**
   For each input, determine:
   - Name (will become a Python variable in `snake_case`)
   - Data type: `float`, `int`, `str`, `bool`, or `Literal[...]` (for enum/select)
   - Unit of measurement (use UCUM codes where applicable: `kg`, `m`, `[lb_av]`, `[in_i]`)
   - Whether it's required or optional
   - Valid range (min/max) or allowed values
   - Brief description

3. **What is the clinical interpretation logic?**
   - How should results be categorised or interpreted?
   - What thresholds define different categories? (e.g., BMI < 18.5 = "Underweight")
   - What clinical reference or guideline is the source? (e.g., "WHO 2023 Guidelines")

4. **Does this calculator need any external Python dependencies?**
   - Beyond the project's standard dependencies (pydantic, fastapi, etc.)
   - If yes, these go in a `[dependencies]` section in the docstring

5. **Does this calculator support multiple unit systems?**
   - e.g., metric and imperial
   - If yes, what conversion factors apply?

### Optional Clarifications

- Should the `working` field show step-by-step calculation or a summary?
- Are there edge cases that need special handling (e.g., division by zero)?
- What tags describe this calculator? (e.g., `["bmi", "anthropometry", "weight"]`)
- Should the result be rounded? To how many decimal places?

---

## Phase 1: Project Architecture Overview

### Repository Structure (What You Need to Touch)

```
clinical-calculators/
  calculators/
    __init__.py              # No changes needed
    bmi.py                   # Example calculator (reference)
    hba1c_converter.py       # Example calculator (reference)
    <your_calculator>.py     # NEW FILE: Your calculator
  tests/
    test_bmi.py              # Example test (reference)
    test_hba1c_converter.py  # Example test (reference)
    test_<your_calculator>.py # NEW FILE: Your tests
```

### What You Do NOT Touch

- `api/main.py` — Calculators are auto-discovered. No registration needed.
- `cli/main.py` — Uses dynamic loading via `core/loader.py`. No changes needed.
- `site/` — The web UI dynamically fetches calculator list and renders forms from docstring specs. No changes needed.
- `core/` — Shared infrastructure. Do not modify unless the calculator needs a new base class feature.

### How Auto-Discovery Works

1. **API**: `core/loader.py` -> `available_calculators()` uses `pkgutil.iter_modules()` to find all modules in `calculators/`. Each module's docstring becomes its documentation. The `calculate()` function is called dynamically.
2. **CLI**: `cli/main.py` -> `calc run <name> --params '{...}'` loads the module by name and calls `calculate()`.
3. **Web UI**: `site/app.js` -> Fetches `/list` endpoint (which calls `available_calculators()`), then fetches `/<name>/doc` to parse the `[inputs]` section from the docstring and auto-generate HTML form fields.
4. **Python package**: Direct import: `from calculators.<name> import calculate`.

### Technology Constraints

- **Python**: 3.11+
- **Pydantic**: v2 (2.x). Use `BaseModel`, `Field`, `model_validator`, `field_validator`. Do NOT use deprecated v1 syntax (`root_validator`, `validator`, `.dict()`, `.json()`).
- **Formatting**: Black (line-length 88), isort (profile "black"), Ruff
- **Testing**: pytest
- **Type hints**: Use `from __future__ import annotations` at top of every file

---

## Phase 2: Create the Calculator File

Create `calculators/<calculator_name>.py`. The file has three parts:

### Part 1: Module Docstring (TOML-Style Specification)

This docstring is **critical** — it serves as:
- Documentation displayed in the API (`/<name>/doc` and `/<name>/doc.html`)
- The schema parsed by `core/loader.py` -> `parse_inputs_spec()` to auto-generate HTML forms in the web UI and API form views
- Human-readable specification

**Format — follow this exact structure:**

```python
"""
# Calculator Display Name

## Description

[Description]
Brief description of what this calculator does.
The formula or algorithm used.
What units and systems are supported.

## Configuration

### Inputs

[inputs]
  - name: parameter_one
    type: number
    unit: kg (UCUM: kg)
    required: true
    min: 0.0
    max: 500.0
    description: Description of parameter_one

  - name: parameter_two
    type: string
    enum: ["option_a", "option_b"]
    required: true
    description: Description of parameter_two

### Outputs

[result]
  type: number
  description: Main calculated result

[working]
  type: string
  description: Step-by-step calculation details

[interpretation]
  type: string
  description: Clinical interpretation of result

[reference]
  type: string
  default: "Source Guidelines Year"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string (e.g., "1.0")
    calculator_name: string

## Validation Rules
- Parameter_one must be > 0 and <= 500
- Parameter_two must be one of: option_a, option_b

## Usage (CLI or API)

>**CLI**:
  ```console
    calc run <calculator_name> --params '{"parameter_one": 70, "parameter_two": "option_a"}'
  ```

>**API**:
```console
  POST /calculate
  {
    "calculator": "<calculator_name>",
    "params": {
      "parameter_one": 70,
      "parameter_two": "option_a"
    }
  }
  ```
"""
```

**Critical docstring rules:**
- The `[inputs]` section MUST use the exact format: `- name: <field_name>` followed by indented `key: value` pairs
- The `type` field must be one of: `number`, `string`, `boolean`, `integer`
- The `enum` field, if present, must be a bracketed list: `["val1", "val2"]`
- The `required` field must be `true` or `false`
- The `min` and `max` fields must be numeric
- The `description` field is displayed as the form label in the web UI
- The `unit` field is displayed as helper text in the form

### Part 2: Imports and Request Model

```python
from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from core.metadata import build_metadata
from core.request.request import CalculatorRequest
from core.response.response import CalculationResponse
```

**Request model rules:**
- MUST inherit from `CalculatorRequest` (which inherits from `pydantic.BaseModel`)
- `CalculatorRequest` provides an optional `metadata: dict | None = None` field
- Use `Literal["option_a", "option_b"]` for enum/select fields
- Use `Field(...)` with constraints: `gt`, `ge`, `lt`, `le`, `description`
- Use `@model_validator(mode="before")` with `@classmethod` for cross-field validation (replaces Pydantic v1's `@root_validator`)
- Use `@field_validator('field_name')` with `@classmethod` for single-field validation (replaces Pydantic v1's `@validator`)
- Class name convention: `<PascalCaseName>Request` (e.g., `BMIRequest`, `HbA1cRequest`)

**Example:**

```python
class BMIRequest(CalculatorRequest):
    unit_system: Literal["metric", "imperial"]
    weight: float = Field(..., gt=0, description="Weight in kg or lb (UCUM)")
    height: float = Field(..., gt=0, description="Height in m or in (UCUM)")

    @model_validator(mode="before")
    @classmethod
    def validate_ranges(cls, values):
        unit = values.get("unit_system")
        w = values.get("weight")
        h = values.get("height")
        if unit == "metric":
            if w is not None and not (0 < w <= 500):
                raise ValueError("weight (kg) must be in (0, 500]")
            if h is not None and not (0 < h <= 3.0):
                raise ValueError("height (m) must be in (0, 3.0]")
        elif unit == "imperial":
            if w is not None and not (0 < w <= 1100):
                raise ValueError("weight (lb) must be in (0, 1100]")
            if h is not None and not (0 < h <= 118):
                raise ValueError("height (in) must be in (0, 118]")
        else:
            raise ValueError("unit_system must be one of: metric, imperial")
        return values
```

### Part 3: Calculate Function

**Signature and rules:**
- Function MUST be named `calculate`
- MUST accept `params: <RequestClass> | dict` — both a typed request and a plain dict
- MUST return `CalculationResponse`
- First line: coerce dict to request model: `req = params if isinstance(params, <RequestClass>) else <RequestClass>(**params)`
- Build and return `CalculationResponse` with all fields

**CalculationResponse fields** (from `core/response/response.py`):

| Field | Type | Required | Description |
|---|---|---|---|
| `result` | `Any` | Yes | The main calculation result (typically `float` or `int`) |
| `working` | `dict[str, Any] \| None` | Recommended | Step-by-step calculation details. Convention: `{"description": "..."}` |
| `interpretation` | `str \| None` | Recommended | Clinical meaning of the result |
| `reference` | `str \| None` | Recommended | Clinical guideline or source |
| `metadata` | `dict[str, Any] \| None` | Yes | Use `build_metadata("<calculator_name>")` from `core.metadata` |
| `tags` | `list \| None` | Optional | Searchable tags like `["bmi", "anthropometry"]` |

**Example:**

```python
def calculate(params: BMIRequest | dict) -> CalculationResponse:
    """Calculate BMI from request parameters."""
    req = params if isinstance(params, BMIRequest) else BMIRequest(**params)

    # Unit conversion if needed
    if req.unit_system == "imperial":
        weight_kg = req.weight * 0.45359237
        height_m = req.height * 0.0254
    else:
        weight_kg = req.weight
        height_m = req.height

    # Core calculation
    bmi = round(weight_kg / (height_m ** 2), 2)

    # Interpretation
    if bmi < 18.5:
        interp = "Underweight"
    elif bmi < 25:
        interp = "Normal"
    elif bmi < 30:
        interp = "Overweight"
    else:
        interp = "Obese"

    # Working (step-by-step)
    working = {
        "description": f"Weight: {weight_kg:.2f} kg, Height: {height_m:.2f} m -> BMI = {bmi:.2f}"
    }

    return CalculationResponse(
        result=bmi,
        working=working,
        interpretation=interp,
        reference="WHO 2023 Guidelines",
        metadata=build_metadata("bmi"),
        tags=["bmi", "body mass index", "weight", "height", "anthropometry"],
    )
```

### Alternative Pattern: Custom Response Model

The HbA1c converter uses a **custom response model** (not `CalculationResponse`) that includes additional fields like `result_unit`, `input_value`, and `input_unit`. This is valid — the API endpoint calls `.model_dump()` on whatever is returned. However, the standard `CalculationResponse` is preferred for consistency and for compatibility with the auto-generated forms.

If using a custom response:
- It MUST inherit from `pydantic.BaseModel`
- It MUST have at least `result` and `metadata` fields
- The `metadata` field MUST be populated with `build_metadata("<name>")`

---

## Phase 3: Create the Test File

Create `tests/test_<calculator_name>.py`.

### Test Structure

```python
from __future__ import annotations

from calculators.<calculator_name> import calculate


def test_basic_calculation():
    """Test basic functionality with typical valid inputs."""
    result = calculate({"param1": <value>, "param2": <value>})
    assert abs(result.result - <expected>) < <tolerance>
    assert result.interpretation == "<expected_interpretation>"
    assert result.metadata["calculator_name"] == "<calculator_name>"


def test_alternative_scenario():
    """Test a different valid input combination."""
    result = calculate({"param1": <value>, "param2": <value>})
    assert abs(result.result - <expected>) < <tolerance>


def test_edge_case_minimum():
    """Test minimum boundary values."""
    result = calculate({"param1": <min_value>, ...})
    assert result.result is not None


def test_edge_case_maximum():
    """Test maximum boundary values."""
    result = calculate({"param1": <max_value>, ...})
    assert result.result is not None


def test_invalid_input_out_of_range():
    """Test that out-of-range values are rejected."""
    try:
        calculate({"param1": <invalid_value>, ...})
        raise AssertionError("Should have raised ValueError")
    except Exception as e:
        assert "<expected_error_substring>" in str(e)


def test_invalid_input_wrong_type():
    """Test that wrong types are rejected."""
    try:
        calculate({"param1": "not_a_number", ...})
        raise AssertionError("Should have raised")
    except Exception:
        pass  # Expected


def test_response_structure():
    """Test that response has all required fields."""
    result = calculate({"param1": <value>, ...})
    assert hasattr(result, "result")
    assert hasattr(result, "working")
    assert hasattr(result, "interpretation")
    assert hasattr(result, "metadata")
    assert hasattr(result, "reference")


def test_metadata_fields():
    """Test that metadata includes required fields."""
    result = calculate({"param1": <value>, ...})
    assert "timestamp" in result.metadata
    assert "version" in result.metadata
    assert "calculator_name" in result.metadata
    assert result.metadata["calculator_name"] == "<calculator_name>"


def test_working_field():
    """Test that working field shows calculation details."""
    result = calculate({"param1": <value>, ...})
    assert result.working is not None
    assert "<expected_substring>" in str(result.working)
```

### Test Requirements

- **Import pattern**: Always `from calculators.<name> import calculate`
- **Call pattern**: Always pass a dict to `calculate()` (this is how the API and CLI call it)
- **Assertions**: Use `abs(result.result - expected) < tolerance` for floating point comparisons
- **Error testing**: Use try/except pattern (not `pytest.raises`) — this matches the existing test style
- **Coverage**: Must test normal cases, edge cases, validation errors, response structure, and metadata
- **File location**: MUST be in `tests/` directory, named `test_<calculator_name>.py`

---

## Phase 4: Verification Checklist

### Before Declaring Done

1. **File created**: `calculators/<calculator_name>.py` exists
2. **Test file created**: `tests/test_<calculator_name>.py` exists
3. **Docstring format**: The `[inputs]` section in the docstring follows the exact format so `parse_inputs_spec()` can parse it
4. **Imports correct**:
   - `from __future__ import annotations` at top
   - `from core.request.request import CalculatorRequest`
   - `from core.response.response import CalculationResponse`
   - `from core.metadata import build_metadata`
5. **Request class**: Inherits from `CalculatorRequest`
6. **Calculate function**: Named `calculate`, accepts `dict | RequestClass`, returns `CalculationResponse`
7. **Metadata**: Uses `build_metadata("<calculator_name>")` with the exact module name
8. **Pydantic v2**: Uses `model_validator`, `field_validator` with `@classmethod` — NOT deprecated v1 `root_validator`, `validator`
9. **Black-compatible**: Line length <= 88, proper formatting
10. **No new dependencies needed** (or they're declared in `[dependencies]` section of docstring)

### How to Test Locally

```bash
# Run just the new calculator's tests
docker compose run --rm api pytest tests/test_<calculator_name>.py -v

# Run all tests
docker compose run --rm api pytest -v

# Run linting
docker compose run --rm api black calculators/<calculator_name>.py tests/test_<calculator_name>.py
docker compose run --rm api isort calculators/<calculator_name>.py tests/test_<calculator_name>.py
docker compose run --rm api ruff check calculators/<calculator_name>.py tests/test_<calculator_name>.py

# Or run the full lint script
./s/lint
```

### How to Test All 4 Surfaces

**Python package** (direct import):
```python
from calculators.<calculator_name> import calculate
result = calculate({"param1": value1, "param2": value2})
print(result.model_dump())
```

**CLI**:
```bash
calc run <calculator_name> --params '{"param1": value1, "param2": "value2"}'
```

**API** (requires `./s/dev up` running):
```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"calculator": "<calculator_name>", "params": {"param1": value1, "param2": "value2"}}'
```

**Web UI** (requires API running):
1. Go to `http://localhost:8000/list.html`
2. Click the calculator name
3. Click "form" link
4. Fill in the form and submit
5. Or go to the GitHub Pages site and select the calculator

---

## Phase 5: Complete Reference — Existing Calculators

### BMI Calculator (`calculators/bmi.py`)

**Inputs**: `unit_system` (Literal), `weight` (float), `height` (float)
**Validation**: Cross-field via `@model_validator(mode="before")` — ranges depend on unit system
**Response**: Uses standard `CalculationResponse`
**Key patterns**:
- Unit conversion before calculation
- Classification function (`_classify_bmi`)
- `working` as dict with `"description"` key
- `tags` field populated

### HbA1c Converter (`calculators/hba1c_converter.py`)

**Inputs**: `value` (float), `input_unit` (Literal)
**Validation**: Cross-field — value range depends on input unit
**Response**: Uses CUSTOM `HbA1cResponse` (not `CalculationResponse`)
**Key patterns**:
- Bidirectional conversion
- Custom response model with extra fields (`result_unit`, `input_value`, `input_unit`)
- `working` as string (not dict) — this works but dict is preferred
- Interpretation function (`_interpret_hba1c`)

**Recommendation**: Follow the BMI pattern (standard `CalculationResponse`, `working` as dict) for maximum compatibility.

---

## Phase 6: TOML Spec for Code Generator (Optional)

The project also has a TOML-based code generator (`core/generator.py`) that can auto-generate calculator code. If the user wants to use this path instead of manual coding:

### TOML Spec Format (for `/generate-calculator` API endpoint)

```toml
[calculator]
name = "snake_case_name"
description = "Clear description of what this calculates"
reference = "Clinical source/guideline"
logic = "result = request.input1 + request.input2; working = {'description': f'Calculation: {result}'}; interpretation = f'Result is {result}'"

[[inputs]]
name = "input1"
type = "number"
description = "First input description"
required = true
min = 0
max = 100

[[inputs]]
name = "input2"
type = "number"
description = "Second input description"
required = true
min = 0
max = 100
```

**TOML rules:**
- `[calculator]` section: `name` (snake_case), `description`, `reference`, `logic` (semicolon-separated Python statements)
- `[[inputs]]` sections: One per input, with `name`, `type`, `description`, `required`, and optional `min`, `max`, `unit`
- `logic` field: Use `request.<field_name>` to access inputs. Must define `result`, `working` (dict), and `interpretation` (string).
- The generator uses `_format_with_black()` to auto-format output

However, the **manual coding approach** (Phases 2-3) produces higher quality, more customisable calculators and is recommended for non-trivial logic.

---

## Phase 7: Dependencies and External Libraries

If the calculator needs external Python packages (e.g., `scipy`, `numpy`):

1. Add a `[dependencies]` section to the module docstring:

```python
"""
# My Calculator

## Description
...

[dependencies]
scipy
numpy>=1.20
"""
```

2. The `core/loader.py` -> `_parse_dependencies_from_doc()` will parse this section
3. `_ensure_dependencies_installed()` will auto-install missing packages via pip before the module is imported
4. This means the calculator file can do `import scipy` at module level — it will be installed automatically on first use

---

## Quick Reference: File Templates

### Calculator File Template

```python
"""
# <Calculator Display Name>

## Description

[Description]
<Brief description of what this calculator does.>
<The formula or algorithm.>

## Configuration

### Inputs

[inputs]
  - name: <field_1>
    type: number
    unit: <unit>
    required: true
    min: <min>
    max: <max>
    description: <Description of field_1>

  - name: <field_2>
    type: string
    enum: ["<option_a>", "<option_b>"]
    required: true
    description: <Description of field_2>

### Outputs

[result]
  type: number
  description: <Main result description>

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  description: Clinical interpretation

[reference]
  type: string
  default: "<Clinical Reference>"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string
    calculator_name: string

## Validation Rules
- <Rule 1>
- <Rule 2>

## Usage (CLI or API)

>**CLI**:
  ```console
    calc run <calculator_name> --params '{"<field_1>": <value>, "<field_2>": "<value>"}'
  ```

>**API**:
```console
  POST /calculate
  {
    "calculator": "<calculator_name>",
    "params": {
      "<field_1>": <value>,
      "<field_2>": "<value>"
    }
  }
  ```
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field, model_validator

from core.metadata import build_metadata
from core.request.request import CalculatorRequest
from core.response.response import CalculationResponse


class <PascalName>Request(CalculatorRequest):
    """Request model for <calculator_name> calculator."""

    <field_1>: float = Field(..., gt=0, description="<description>")
    <field_2>: Literal["<option_a>", "<option_b>"] = Field(
        ..., description="<description>"
    )

    @model_validator(mode="before")
    @classmethod
    def validate_ranges(cls, values):
        # Cross-field validation if needed
        return values


def _interpret_result(<result_param>: float) -> str:
    """Generate clinical interpretation."""
    if <result_param> < <threshold_1>:
        return "<Category 1>"
    elif <result_param> < <threshold_2>:
        return "<Category 2>"
    else:
        return "<Category 3>"


def calculate(params: <PascalName>Request | dict) -> CalculationResponse:
    """Calculate <description>."""
    req = params if isinstance(params, <PascalName>Request) else <PascalName>Request(**params)

    # Calculation logic
    result = <formula using req.field_1, req.field_2>

    # Interpretation
    interp = _interpret_result(result)

    # Working
    working = {
        "description": f"<Step-by-step: {result:.2f}>"
    }

    return CalculationResponse(
        result=result,
        working=working,
        interpretation=interp,
        reference="<Clinical Reference>",
        metadata=build_metadata("<calculator_name>"),
        tags=["<tag1>", "<tag2>"],
    )
```

### Test File Template

```python
from __future__ import annotations

from calculators.<calculator_name> import calculate


def test_basic_calculation():
    """Test basic functionality with typical valid inputs."""
    result = calculate({"<field_1>": <value>, "<field_2>": "<value>"})
    assert abs(result.result - <expected>) < <tolerance>
    assert result.interpretation == "<expected>"
    assert result.metadata["calculator_name"] == "<calculator_name>"


def test_alternative_input():
    """Test with different valid input combination."""
    result = calculate({"<field_1>": <value>, "<field_2>": "<value>"})
    assert abs(result.result - <expected>) < <tolerance>


def test_edge_case_minimum():
    """Test minimum boundary values."""
    result = calculate({"<field_1>": <min_val>, "<field_2>": "<value>"})
    assert result.result is not None


def test_edge_case_maximum():
    """Test maximum boundary values."""
    result = calculate({"<field_1>": <max_val>, "<field_2>": "<value>"})
    assert result.result is not None


def test_invalid_input_out_of_range():
    """Test that out-of-range values are rejected."""
    try:
        calculate({"<field_1>": <invalid_val>, "<field_2>": "<value>"})
        raise AssertionError("Should have raised ValueError")
    except Exception as e:
        assert "<error_substring>" in str(e)


def test_response_structure():
    """Test that response has all required fields."""
    result = calculate({"<field_1>": <value>, "<field_2>": "<value>"})
    assert hasattr(result, "result")
    assert hasattr(result, "working")
    assert hasattr(result, "interpretation")
    assert hasattr(result, "metadata")
    assert hasattr(result, "reference")


def test_metadata_fields():
    """Test that metadata includes required fields."""
    result = calculate({"<field_1>": <value>, "<field_2>": "<value>"})
    assert "timestamp" in result.metadata
    assert "version" in result.metadata
    assert "calculator_name" in result.metadata
    assert result.metadata["calculator_name"] == "<calculator_name>"


def test_working_field():
    """Test that working field shows calculation details."""
    result = calculate({"<field_1>": <value>, "<field_2>": "<value>"})
    assert result.working is not None
    assert "description" in result.working
```

---

## Common Pitfalls

1. **Pydantic v1 syntax**: This project uses Pydantic v2. Do NOT use `root_validator`, `validator`, `.dict()`, `.json()`, or `class Config`. Use `model_validator`, `field_validator`, `.model_dump()`, `.model_dump_json()`, and `model_config` instead.

2. **Calculator name mismatch**: The string passed to `build_metadata()` MUST match the Python module filename (without `.py`). If the file is `calculators/bmi.py`, use `build_metadata("bmi")`.

3. **Missing `calculate()` function**: The function MUST be named exactly `calculate`. The API and CLI load it by name: `mod.calculate(params)`.

4. **Dict acceptance**: The `calculate()` function MUST accept a plain `dict` — the API and CLI always pass dicts, not typed request objects.

5. **Docstring `[inputs]` format**: The web UI parses this section to auto-generate forms. If the format is wrong, the form will be empty or broken. Each input MUST start with `- name: <field_name>` on its own line.

6. **Working field type**: Use `dict` (e.g., `{"description": "..."}`) for `CalculationResponse.working`, not a plain string. The `CalculationResponse` model defines `working` as `dict[str, Any] | None`.

7. **Import from core**: Always use `from core.request.request import CalculatorRequest` and `from core.response.response import CalculationResponse`. Note the nested module paths (`core.request.request`, not `core.request`).

8. **Tags**: Optional but helpful. Used for searchability. Provide as a list of lowercase strings.

9. **Formatting**: Run Black before committing. The project uses line-length 88 and targets Python 3.11.

10. **Test file location**: Tests MUST be in the `tests/` directory (not `core/tests/`). The `core/tests/` directory is for infrastructure tests only.

11. **`@classmethod` decorator**: In Pydantic v2, `@model_validator` and `@field_validator` require the `@classmethod` decorator immediately below them.
