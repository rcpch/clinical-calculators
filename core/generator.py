"""
Calculator code generator from TOML/Markdown specifications.

This module generates calculator Python code from user-provided TOML specifications.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _format_with_black(code: str) -> str:
    """Format Python code using isort, Black, and Ruff."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_path = f.name

        # Run isort first to sort imports
        subprocess.run(
            ["isort", "--quiet", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Run Black to format
        subprocess.run(
            ["black", "--quiet", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Run Ruff to fix any linting issues
        subprocess.run(
            ["ruff", "check", "--fix", "--quiet", temp_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Read the formatted code
        with open(temp_path) as f:
            formatted_code = f.read()

        # Clean up
        Path(temp_path).unlink()

        return formatted_code
    except Exception:
        # If formatting fails, return original code
        return code


@dataclass
class ValidationError:
    """Represents a validation error with context."""

    field: str
    message: str
    severity: str = "error"  # error, warning


@dataclass
class GeneratedCalculator:
    """Result of calculator generation."""

    name: str
    python_code: str
    test_code: str
    validation_errors: list[ValidationError]
    is_valid: bool


def parse_toml_spec(spec: str) -> dict[str, Any]:
    """
    Parse TOML specification from docstring format.

    Args:
        spec: TOML specification string (can include markdown)

    Returns:
        Parsed specification dictionary

    Raises:
        ValueError: If TOML is invalid or required sections missing
    """
    try:
        import tomli
    except ImportError:
        import tomllib as tomli

    # Extract TOML sections from markdown if present
    toml_content = _extract_toml_from_markdown(spec)

    try:
        parsed = tomli.loads(toml_content)
    except Exception as e:
        raise ValueError(f"Invalid TOML format: {e}") from e

    # Validate required sections
    _validate_required_sections(parsed)

    return parsed


def _extract_toml_from_markdown(content: str) -> str:
    """Extract TOML content from markdown, handling sections."""
    lines = content.strip().split("\n")
    toml_lines = []
    in_section = False

    for line in lines:
        stripped = line.strip()
        # Check for TOML section headers
        if stripped.startswith("[") and stripped.endswith("]"):
            in_section = True
            toml_lines.append(line)
        elif in_section and (
            stripped.startswith("-") or "=" in stripped or stripped == ""
        ):
            toml_lines.append(line)
        elif stripped.startswith("#") or stripped == "":
            # Keep comments and blank lines
            if in_section:
                toml_lines.append(line)

    return "\n".join(toml_lines)


def _validate_required_sections(spec: dict[str, Any]) -> None:
    """Validate that required TOML sections are present."""
    required_sections = ["calculator", "inputs"]

    for section in required_sections:
        if section not in spec:
            raise ValueError(f"Missing required section: [{section}]")

    # Validate calculator metadata
    calc = spec["calculator"]
    required_fields = ["name", "description"]
    for field in required_fields:
        if field not in calc:
            raise ValueError(f"Missing required field in [calculator]: {field}")

    # Validate at least one input
    if not spec["inputs"]:
        raise ValueError("At least one input is required in [inputs] section")


def validate_calculator_spec(spec: dict[str, Any]) -> list[ValidationError]:
    """
    Validate calculator specification and return any errors/warnings.

    Args:
        spec: Parsed TOML specification

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Validate calculator name
    name = spec.get("calculator", {}).get("name", "")
    if not re.match(r"^[a-z][a-z0-9_]*$", name):
        errors.append(
            ValidationError(
                field="calculator.name",
                message="Name must start with lowercase letter and contain only lowercase letters, numbers, and underscores",
                severity="error",
            )
        )

    # Validate inputs
    inputs = spec.get("inputs", [])
    for i, inp in enumerate(inputs):
        if "name" not in inp:
            errors.append(
                ValidationError(
                    field=f"inputs[{i}]",
                    message="Input missing 'name' field",
                    severity="error",
                )
            )
        if "type" not in inp:
            errors.append(
                ValidationError(
                    field=f"inputs[{i}]",
                    message="Input missing 'type' field",
                    severity="error",
                )
            )

        # Validate input name format
        if "name" in inp and not re.match(r"^[a-z][a-z0-9_]*$", inp["name"]):
            errors.append(
                ValidationError(
                    field=f"inputs[{i}].name",
                    message="Input name must start with lowercase letter and contain only lowercase letters, numbers, and underscores",
                    severity="error",
                )
            )

    # Validate calculation logic if provided
    calc_logic = spec.get("calculator", {}).get("logic", "")
    if not calc_logic:
        errors.append(
            ValidationError(
                field="calculator.logic",
                message="No calculation logic provided",
                severity="error",
            )
        )

    return errors


def generate_calculator_code(spec: dict[str, Any]) -> str:
    """
    Generate Python calculator code from specification.

    Args:
        spec: Validated TOML specification

    Returns:
        Generated Python code as string
    """
    calc = spec["calculator"]
    name = calc["name"]
    description = calc["description"]
    inputs = spec["inputs"]
    logic = calc.get("logic", "")
    reference = calc.get("reference", "")

    # Build imports
    imports = [
        "from __future__ import annotations",
        "",
        "from pydantic import Field",
        "",
        "from core.metadata import build_metadata",
        "from core.request.request import CalculatorRequest",
        "from core.response.response import CalculationResponse",
    ]

    # Build docstring
    docstring = f'"""\n# {name.replace("_", " ").title()}\n\n{description}\n'

    # Add TOML spec to docstring
    docstring += "\n## 📂 Configuration\n\n[calculator]\n"
    docstring += f'name = "{name}"\n'
    docstring += f'description = "{description}"\n'
    if reference:
        docstring += f'reference = "{reference}"\n'

    docstring += "\n[inputs]\n"
    for inp in inputs:
        docstring += f'- name: {inp["name"]}\n'
        docstring += f'  type: {inp["type"]}\n'
        if "description" in inp:
            docstring += f'  description: {inp["description"]}\n'
        if "required" in inp:
            docstring += f'  required: {inp["required"]}\n'
        if "min" in inp:
            docstring += f'  min: {inp["min"]}\n'
        if "max" in inp:
            docstring += f'  max: {inp["max"]}\n'
        docstring += "\n"

    docstring += '"""\n'

    # Build Request class
    class_name = "".join(word.capitalize() for word in name.split("_")) + "Request"
    request_class = [
        f"class {class_name}(CalculatorRequest):",
        '    """Request model for calculator."""',
        "",  # Blank line after docstring per Black
    ]

    for inp in inputs:
        field_name = inp["name"]
        field_type = _python_type_from_spec(inp["type"])
        field_desc = inp.get("description", "")

        # Build Field with validation
        field_args = []
        if inp.get("required", True):
            field_args.append("...")
        else:
            field_args.append("None")

        if "min" in inp:
            field_args.append(f'ge={inp["min"]}')
        if "max" in inp:
            field_args.append(f'le={inp["max"]}')

        # Handle long descriptions
        if field_desc:
            field_args.append(f'description="{field_desc}"')

        # Build field definition - use multiline if it would be too long
        single_line = f"    {field_name}: {field_type} = Field({', '.join(field_args)})"

        if len(single_line) > 88:
            # Break into multiple lines - let Black handle the formatting
            request_class.append(f"    {field_name}: {field_type} = Field(")
            for arg in field_args:
                request_class.append(f"        {arg},")
            request_class.append("    )")
        else:
            request_class.append(single_line)

    # Build calculate function
    calculate_func = [
        "",
        "",
        "def calculate(params: dict) -> CalculationResponse:",
        f'    """Calculate {name.replace("_", " ")}."""',
        f"    request = {class_name}(**params)",
        "",
        "    # Extract input values",
    ]

    # Extract variables from request for direct use in logic
    for inp in inputs:
        field_name = inp["name"]
        calculate_func.append(f"    {field_name} = request.{field_name}")

    calculate_func.append("")
    calculate_func.append("    # Calculation logic")

    # Add user's logic (properly indented)
    # Logic comes as semicolon-separated statements from TOML
    logic_statements = [stmt.strip() for stmt in logic.split(";") if stmt.strip()]
    for stmt in logic_statements:
        calculate_func.append(f"    {stmt}")

    # Build response
    calculate_func.extend(
        [
            "",
            "    return CalculationResponse(",
            "        result=result,",
            "        working=working,",
            "        interpretation=interpretation,",
            f'        reference="{reference}",',
            f'        metadata=build_metadata("{name}"),',
            "    )",
        ]
    )

    # Combine all parts with proper spacing per PEP 8
    # Note: "\n".join() does NOT add trailing newline, so sections end with content
    imports_section = "\n".join(imports)
    class_section = "\n".join(request_class)
    function_section = "\n".join(calculate_func)

    # Two blank lines = 3 newline characters (\n\n\n)
    # Between: imports-docstring, docstring-class, class-function
    return f"{imports_section}\n\n\n{docstring}\n\n\n{class_section}\n\n\n{function_section}\n"


def _python_type_from_spec(type_str: str) -> str:
    """Convert TOML type specification to Python type hint."""
    type_map = {
        "number": "float",
        "integer": "int",
        "string": "str",
        "boolean": "bool",
    }
    return type_map.get(type_str.lower(), "Any")


def generate_test_code(spec: dict[str, Any]) -> str:
    """
    Generate basic test code for calculator.

    Args:
        spec: Calculator specification

    Returns:
        Generated test code as string
    """
    name = spec["calculator"]["name"]
    inputs = spec["inputs"]

    # Build test template
    test_code = [
        "from __future__ import annotations",
        "",
        f"from calculators.{name} import calculate",
        "",
        "",
        "def test_basic_calculation():",
        '    """Test basic calculator functionality."""',
        "    result = calculate({",
    ]

    # Add sample inputs
    for inp in inputs:
        sample_value = _get_sample_value(inp)
        test_code.append(f'        "{inp["name"]}": {sample_value},')

    test_code.extend(
        [
            "    })",
            "    assert result.result is not None",
            "    assert result.metadata is not None",
            "",
            "",
            "def test_response_structure():",
            '    """Test that response has required fields."""',
            "    result = calculate({",
        ]
    )

    # Add sample inputs again
    for inp in inputs:
        sample_value = _get_sample_value(inp)
        test_code.append(f'        "{inp["name"]}": {sample_value},')

    test_code.extend(
        [
            "    })",
            '    assert hasattr(result, "result")',
            '    assert hasattr(result, "working")',
            '    assert hasattr(result, "interpretation")',
            '    assert hasattr(result, "metadata")',
            '    assert hasattr(result, "reference")',
        ]
    )

    return "\n".join(test_code) + "\n"


def _get_sample_value(inp: dict[str, Any]) -> str:
    """Get a sample value for an input based on its type and constraints."""
    type_str = inp.get("type", "number")

    if type_str == "number" or type_str == "integer":
        if "min" in inp:
            return str(inp["min"] + 1)
        return "10.0" if type_str == "number" else "10"
    elif type_str == "boolean":
        return "True"
    else:  # string
        return '"test"'


def validate_generated_code(
    python_code: str, test_code: str, name: str
) -> list[ValidationError]:
    """
    Validate generated code using linting tools.

    Args:
        python_code: Generated calculator code
        test_code: Generated test code
        name: Calculator name

    Returns:
        List of validation errors
    """
    errors = []

    # Create temporary files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        calc_file = tmp_path / f"{name}.py"
        test_file = tmp_path / f"test_{name}.py"

        calc_file.write_text(python_code)
        test_file.write_text(test_code)

        # Run black check
        try:
            result = subprocess.run(
                ["black", "--check", str(calc_file), str(test_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                errors.append(
                    ValidationError(
                        field="formatting",
                        message="Code formatting issues detected",
                        severity="warning",
                    )
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Run ruff check
        try:
            result = subprocess.run(
                ["ruff", "check", str(calc_file), str(test_file)],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                errors.append(
                    ValidationError(
                        field="linting",
                        message=f"Linting issues: {result.stdout[:200]}",
                        severity="warning",
                    )
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    return errors


def generate_calculator(spec_input: str) -> GeneratedCalculator:
    """
    Main function to generate calculator from specification.

    Args:
        spec_input: TOML/Markdown specification string

    Returns:
        GeneratedCalculator with code and validation results
    """
    validation_errors = []

    try:
        # Parse spec
        spec = parse_toml_spec(spec_input)
        name = spec["calculator"]["name"]

        # Validate spec
        spec_errors = validate_calculator_spec(spec)
        validation_errors.extend(spec_errors)

        if any(e.severity == "error" for e in validation_errors):
            return GeneratedCalculator(
                name=name,
                python_code="",
                test_code="",
                validation_errors=validation_errors,
                is_valid=False,
            )

        # Generate code
        python_code = generate_calculator_code(spec)
        test_code = generate_test_code(spec)

        # Format with Black
        python_code = _format_with_black(python_code)
        test_code = _format_with_black(test_code)

        # Validate generated code
        code_errors = validate_generated_code(python_code, test_code, name)
        validation_errors.extend(code_errors)

        return GeneratedCalculator(
            name=name,
            python_code=python_code,
            test_code=test_code,
            validation_errors=validation_errors,
            is_valid=True,
        )

    except ValueError as e:
        validation_errors.append(
            ValidationError(field="spec", message=str(e), severity="error")
        )
        return GeneratedCalculator(
            name="",
            python_code="",
            test_code="",
            validation_errors=validation_errors,
            is_valid=False,
        )
    except Exception as e:
        validation_errors.append(
            ValidationError(
                field="generation", message=f"Unexpected error: {e}", severity="error"
            )
        )
        return GeneratedCalculator(
            name="",
            python_code="",
            test_code="",
            validation_errors=validation_errors,
            is_valid=False,
        )
