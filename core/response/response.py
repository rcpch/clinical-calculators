from typing import Any

from pydantic import BaseModel, Field


class CalculationResponse(BaseModel):
    result: Any = Field(..., description="The main result of the calculation.")
    working: dict[str, Any] | None = Field(
        None, description="Intermediate calculation steps or details."
    )
    interpretation: str | None = Field(
        None, description="Interpretation of the result."
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata about the calculation."
    )
    reference: str | None = Field(
        None, description="Reference or source for the calculation."
    )
    tags: list | None = Field(None, description="Tags associated with the calculation.")
