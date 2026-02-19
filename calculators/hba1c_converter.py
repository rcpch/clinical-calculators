"""
# HbA1c Converter

## 📂 Configuration (TOML-style in docstring)

[inputs]
- name: value
  type: number
  required: true
  min: 0.0
  max: 20.0
  description: HbA1c value to convert

- name: input_unit
  type: string
  enum: ["percent", "mmol_mol"]
  required: true
  description: Unit of the input value (percent or mmol_mol)

## 📂 Output (TOML-style)

[result]
  type: number
  description: Converted HbA1c value (rounded to 1 decimal)

[result_unit]
  type: string
  description: Unit of the result value

[input_value]
  type: number
  description: Original input value

[input_unit]
  type: string
  description: Unit of the input value

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  description: Clinical interpretation of HbA1c level

[reference]
  type: string
  default: "IFCC/DCCT standardization"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string (e.g., "1.0")
    calculator_name: string

## 📂 Validation Rules
- Value must be > 0 and ≤ 20 for percentage
- Value must be > 0 and ≤ 200 for mmol/mol
- input_unit must be one of: percent, mmol_mol

## 📂 Usage (CLI or API)

CLI:
  calc hba1c_converter --value 7.5 --input-unit percent

API:
  POST /calculate
  {
    "calculator": "hba1c_converter",
    "params": {
      "value": 7.5,
      "input_unit": "percent"
    }
  }

## 📂 Conversion Formula
- From % to mmol/mol: mmol/mol = (% - 2.15) × 10.929
- From mmol/mol to %: % = (mmol/mol / 10.929) + 2.15

## 📂 Output Example
{
  "result": 58.5,
  "result_unit": "mmol/mol",
  "input_value": 7.5,
  "input_unit": "percent",
  "working": "HbA1c 7.5% → (7.5 - 2.15) × 10.929 = 58.5 mmol/mol",
  "interpretation": "Pre-diabetes range (42-47 mmol/mol or 6.0-6.4%)",
  "reference": "IFCC/DCCT standardization",
  "metadata": {
    "timestamp": "2025-12-14T10:00:00Z",
    "version": "1.0",
    "calculator_name": "hba1c_converter"
  }
}

"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from core.metadata import build_metadata


class HbA1cRequest(BaseModel):
    value: float = Field(..., gt=0)
    input_unit: Literal["percent", "mmol_mol"]

    @model_validator(mode="before")
    @classmethod
    def validate_ranges(cls, values):
        unit = values.get("input_unit")
        val = values.get("value")

        if unit == "percent":
            if val is not None and not (0 < val <= 20):
                raise ValueError("HbA1c percentage must be in (0, 20]")
        elif unit == "mmol_mol":
            if val is not None and not (0 < val <= 200):
                raise ValueError("HbA1c mmol/mol must be in (0, 200]")
        else:
            raise ValueError("input_unit must be one of: percent, mmol_mol")

        return values


class HbA1cResponse(BaseModel):
    result: float
    result_unit: str
    input_value: float
    input_unit: str
    working: str
    interpretation: str
    reference: str = "IFCC/DCCT standardization"
    metadata: dict


def _interpret_hba1c(mmol_mol_value: float) -> str:
    """Provide clinical interpretation based on mmol/mol value."""
    if mmol_mol_value < 42:
        return "Normal range (below 42 mmol/mol or 6.0%)"
    elif mmol_mol_value < 48:
        return "Pre-diabetes range (42-47 mmol/mol or 6.0-6.4%)"
    elif mmol_mol_value < 53:
        return "Diabetes diagnosis threshold (48-52 mmol/mol or 6.5-6.9%)"
    elif mmol_mol_value < 75:
        return "Suboptimal control (53-74 mmol/mol or 7.0-8.9%)"
    else:
        return "Poor control (≥75 mmol/mol or ≥9.0%)"


def calculate(params: HbA1cRequest | dict) -> HbA1cResponse:
    """Convert HbA1c between percentage and mmol/mol.

    Accepts either a HbA1cRequest or a plain dict (which will be validated).

    Conversion formulas:
    - % to mmol/mol: (% - 2.15) × 10.929
    - mmol/mol to %: (mmol/mol / 10.929) + 2.15
    """
    req = params if isinstance(params, HbA1cRequest) else HbA1cRequest(**params)

    if req.input_unit == "percent":
        # Convert from percentage to mmol/mol
        result = round((req.value - 2.15) * 10.929, 1)
        result_unit = "mmol/mol"
        working = (
            f"HbA1c {req.value}% → ({req.value} - 2.15) × 10.929 = {result} mmol/mol"
        )
        mmol_mol_for_interp = result
    else:
        # Convert from mmol/mol to percentage
        result = round((req.value / 10.929) + 2.15, 1)
        result_unit = "percent"
        working = (
            f"HbA1c {req.value} mmol/mol → ({req.value} / 10.929) + 2.15 = {result}%"
        )
        mmol_mol_for_interp = req.value

    interpretation = _interpret_hba1c(mmol_mol_for_interp)

    return HbA1cResponse(
        result=result,
        result_unit=result_unit,
        input_value=req.value,
        input_unit=req.input_unit,
        working=working,
        interpretation=interpretation,
        metadata=build_metadata("hba1c_converter"),
    )
