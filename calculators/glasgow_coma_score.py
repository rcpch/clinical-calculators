from __future__ import annotations

from pydantic import Field

from core.metadata import build_metadata
from core.request.request import CalculatorRequest
from core.response.response import CalculationResponse

"""
# Glasgow Coma Score

Glasgow Coma Score

## 📂 Configuration

[calculator]
name = "glasgow_coma_score"
description = "Glasgow Coma Score"
reference = "Teasdale G, Jennett B. Assessment of coma and impaired consciousness. A practical scale. Lancet. 1974 Jul 13;2(7872):81-4. doi: 10.1016/s0140-6736(74)91639-0. PMID: 4136544."

[inputs]
- name: eyes
  type: number
  description: E4 spontaneous eye opening E3 eye opening to voice E2 eye opening to pain E1 no eye opening 0 Not possible to perform
  required: True
  min: 1
  max: 4

- name: voice
  type: number
  description: V5 Oriented in Time, Place and Person | Smiles, coos, babbles V4 Confused speech | Irritable, crying (but consolable) V3 Inappropriate words | Inconsolable crying or crying only in response to pain V2 Incomprehensible sounds | Moans in response to pain V1 No response | No response
  required: True
  min: 1
  max: 5

- name: motor
  type: number
  description: M6 Obeys commands | Normal spontaneous movement M5 Localizes to pain | Withdraws to touch M4 Withdraws from pain (normal flexion) | Withdraws to pain M3 Decorticate posturing (abnormal flexion) | Abnormal flexion to pain (Decorticate response) M2 Decerebrate posturing (extension) | Abnormal extension to pain (Decerebrate response) M1 No response | No response
  required: True
  min: 1
  max: 6

"""


class GlasgowComaScoreRequest(CalculatorRequest):
    """Request model for calculator."""

    eyes: float = Field(
        ...,
        ge=1,
        le=4,
        description="E4 spontaneous eye opening E3 eye opening to voice E2 eye opening to pain E1 no eye opening 0 Not possible to perform",
    )
    voice: float = Field(
        ...,
        ge=1,
        le=5,
        description="V5 Oriented in Time, Place and Person | Smiles, coos, babbles V4 Confused speech | Irritable, crying (but consolable) V3 Inappropriate words | Inconsolable crying or crying only in response to pain V2 Incomprehensible sounds | Moans in response to pain V1 No response | No response",
    )
    motor: float = Field(
        ...,
        ge=1,
        le=6,
        description="M6 Obeys commands | Normal spontaneous movement M5 Localizes to pain | Withdraws to touch M4 Withdraws from pain (normal flexion) | Withdraws to pain M3 Decorticate posturing (abnormal flexion) | Abnormal flexion to pain (Decorticate response) M2 Decerebrate posturing (extension) | Abnormal extension to pain (Decerebrate response) M1 No response | No response",
    )


def calculate(params: dict) -> CalculationResponse:
    """Calculate glasgow coma score."""
    request = GlasgowComaScoreRequest(**params)

    # Extract input values
    eyes = request.eyes
    voice = request.voice
    motor = request.motor

    # Calculation logic
    result = eyes + voice + motor
    working = {"description": f"GCS = eyes + voice + motor = {result:.2f}"}
    interpretation = f"GCS is {result:.2f} / 15 (minimum score is 3)"

    return CalculationResponse(
        result=result,
        working=working,
        interpretation=interpretation,
        reference="Teasdale G, Jennett B. Assessment of coma and impaired consciousness. A practical scale. Lancet. 1974 Jul 13;2(7872):81-4. doi: 10.1016/s0140-6736(74)91639-0. PMID: 4136544.",
        metadata=build_metadata("glasgow_coma_score"),
    )

