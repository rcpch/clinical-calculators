"""
# ADHD Adult Self-Report Scale (ASRS-v1.1)

## Description

[Description]
The Adult ADHD Self-Report Scale (ASRS-v1.1) is an 18-item self-report questionnaire
developed by the WHO Composite International Diagnostic Interview (WMH-CIDI) to screen
for Attention Deficit Hyperactivity Disorder (ADHD) symptoms in adults aged 18 and over.

Part A (Questions 1-6) is the validated screener. A positive Part A result is highly
consistent with adult ADHD and should prompt further clinical evaluation by a qualified
clinician.

Part B (Questions 7-18) provides additional symptom detail used during a full clinical
assessment to supplement Part A findings.

Each question is answered on the following frequency scale:
  Never (0) / Rarely (1) / Sometimes (2) / Often (3) / Very Often (4)

Part A scoring thresholds (the "shaded boxes" on the paper form):
  - Questions 1-3: positive if the response is Sometimes, Often, or Very Often (score ≥ 2)
  - Questions 4-6: positive if the response is Often or Very Often (score ≥ 3)
  Positive screen = 4 or more of the 6 Part A items meeting their threshold.

This tool is intended to support, not replace, clinical judgement. A positive screen
indicates that ADHD symptoms are clinically significant and a full diagnostic assessment
is warranted; it is not a diagnosis of ADHD.

## Configuration

### Inputs

[inputs]
  - name: q1
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q1 (Part A): How often do you have trouble wrapping up the final details of a project, once the challenging parts have been done?"

  - name: q2
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q2 (Part A): How often do you have difficulty getting things in order when you have to do a task that requires organisation?"

  - name: q3
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q3 (Part A): How often do you have problems remembering appointments or obligations?"

  - name: q4
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q4 (Part A): When you have a task that requires a lot of thought, how often do you avoid or delay getting started?"

  - name: q5
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q5 (Part A): How often do you fidget or squirm with your hands or feet when you have to sit down for a long time?"

  - name: q6
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q6 (Part A): How often do you feel overly active and compelled to do things, like you were driven by a motor?"

  - name: q7
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q7 (Part B): How often do you make careless mistakes when you have to work on a boring or difficult project?"

  - name: q8
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q8 (Part B): How often do you have difficulty keeping your attention when you are doing boring or repetitive work?"

  - name: q9
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q9 (Part B): How often do you have difficulty concentrating on what people say to you, even when they are speaking to you directly?"

  - name: q10
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q10 (Part B): How often do you misplace or have difficulty finding things at home or at work?"

  - name: q11
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q11 (Part B): How often are you distracted by activity or noise around you?"

  - name: q12
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q12 (Part B): How often do you leave your seat in meetings or other situations in which you are expected to remain seated?"

  - name: q13
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q13 (Part B): How often do you feel restless or fidgety?"

  - name: q14
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q14 (Part B): How often do you have difficulty unwinding and relaxing when you have time to yourself?"

  - name: q15
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q15 (Part B): How often do you feel overly active and compelled to do things, like you were driven by a motor?"

  - name: q16
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q16 (Part B): How often do you find yourself talking too much when you are in social situations?"

  - name: q17
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q17 (Part B): When you are in a conversation, how often do you find yourself finishing the sentences of the people you are talking to, before they can finish them themselves?"

  - name: q18
    type: string
    enum: ["never", "rarely", "sometimes", "often", "very_often"]
    required: true
    description: "Q18 (Part B): How often do you have difficulty waiting your turn in situations when turn taking is required?"

### Outputs

[result]
  type: integer
  description: Number of Part A items meeting the frequency threshold (0–6). A score of 4 or more indicates a positive ADHD screen.

[working]
  type: string
  description: Detailed scoring breakdown including Part A item-by-item results, Part A total, Part B total, and overall total score (0–72).

[interpretation]
  type: string
  description: Clinical interpretation of the ASRS-v1.1 result with recommendation.

[reference]
  type: string
  default: "Kessler RC et al. (2005). The World Health Organization Adult ADHD Self-Report Scale (ASRS). Psychol Med. 35(2):245-56."

[metadata]
  type: object

## Validation Rules
- All 18 questions (q1–q18) are required.
- Each question must be one of: never, rarely, sometimes, often, very_often.
- This tool is validated for adults aged 18 years and over.
- A positive result is not a diagnosis; formal clinical assessment is required.

## Usage (CLI or API)

>**CLI**:
  ```console
    calc run asrs_screener --params '{"q1":"often","q2":"sometimes","q3":"often","q4":"very_often","q5":"often","q6":"rarely","q7":"sometimes","q8":"often","q9":"sometimes","q10":"often","q11":"often","q12":"never","q13":"often","q14":"sometimes","q15":"rarely","q16":"never","q17":"rarely","q18":"sometimes"}'
  ```

>**API**:
```console
  POST /calculate
  {
    "calculator": "asrs_screener",
    "params": {
      "q1": "often",
      "q2": "sometimes",
      "q3": "often",
      "q4": "very_often",
      "q5": "often",
      "q6": "rarely",
      "q7": "sometimes",
      "q8": "often",
      "q9": "sometimes",
      "q10": "often",
      "q11": "often",
      "q12": "never",
      "q13": "often",
      "q14": "sometimes",
      "q15": "rarely",
      "q16": "never",
      "q17": "rarely",
      "q18": "sometimes"
    }
  }
  ```
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from core.metadata import build_metadata
from core.request.request import CalculatorRequest
from core.response.response import CalculationResponse

# Maps each string frequency label to its numeric score (0–4)
_SCORE_MAP: dict[str, int] = {
    "never": 0,
    "rarely": 1,
    "sometimes": 2,
    "often": 3,
    "very_often": 4,
}

FrequencyValue = Literal["never", "rarely", "sometimes", "often", "very_often"]

# Human-readable labels for working output
_LABEL_MAP: dict[str, str] = {
    "never": "Never (0)",
    "rarely": "Rarely (1)",
    "sometimes": "Sometimes (2)",
    "often": "Often (3)",
    "very_often": "Very Often (4)",
}


class ASRSScreenerRequest(CalculatorRequest):
    """Request model for the ASRS-v1.1 ADHD screener."""

    # Part A — Screener (Questions 1–6)
    q1: FrequencyValue = Field(
        ..., description="Q1 (Part A): Trouble finishing final details of a project"
    )
    q2: FrequencyValue = Field(
        ..., description="Q2 (Part A): Difficulty organising tasks"
    )
    q3: FrequencyValue = Field(
        ..., description="Q3 (Part A): Problems remembering appointments or obligations"
    )
    q4: FrequencyValue = Field(
        ...,
        description="Q4 (Part A): Avoiding or delaying tasks requiring sustained thought",
    )
    q5: FrequencyValue = Field(
        ...,
        description="Q5 (Part A): Fidgeting or squirming when seated for a long time",
    )
    q6: FrequencyValue = Field(
        ..., description="Q6 (Part A): Feeling overly active or driven by a motor"
    )

    # Part B (Questions 7–18)
    q7: FrequencyValue = Field(
        ..., description="Q7 (Part B): Careless mistakes on boring or difficult tasks"
    )
    q8: FrequencyValue = Field(
        ..., description="Q8 (Part B): Difficulty sustaining attention on boring work"
    )
    q9: FrequencyValue = Field(
        ..., description="Q9 (Part B): Difficulty concentrating on what people say"
    )
    q10: FrequencyValue = Field(
        ..., description="Q10 (Part B): Misplacing or losing things"
    )
    q11: FrequencyValue = Field(
        ..., description="Q11 (Part B): Being distracted by activity or noise"
    )
    q12: FrequencyValue = Field(
        ..., description="Q12 (Part B): Leaving seat when expected to remain seated"
    )
    q13: FrequencyValue = Field(
        ..., description="Q13 (Part B): Feeling restless or fidgety"
    )
    q14: FrequencyValue = Field(
        ..., description="Q14 (Part B): Difficulty unwinding or relaxing"
    )
    q15: FrequencyValue = Field(
        ..., description="Q15 (Part B): Feeling overly active or driven by a motor"
    )
    q16: FrequencyValue = Field(
        ..., description="Q16 (Part B): Talking too much in social situations"
    )
    q17: FrequencyValue = Field(
        ..., description="Q17 (Part B): Finishing others' sentences before they can"
    )
    q18: FrequencyValue = Field(
        ..., description="Q18 (Part B): Difficulty waiting your turn"
    )


def _part_a_item_positive(question_index: int, score: int) -> bool:
    """Determine whether a Part A item meets its clinical frequency threshold.

    Questions 1-3 (index 0-2): positive if score >= 2 (Sometimes/Often/Very Often).
    Questions 4-6 (index 3-5): positive if score >= 3 (Often/Very Often only).
    """
    if question_index < 3:
        return score >= 2
    return score >= 3


def _interpret_asrs(part_a_positive_count: int) -> str:
    """Generate a clinical interpretation based on the Part A screener result."""
    if part_a_positive_count >= 4:
        return (
            f"Positive screen: {part_a_positive_count}/6 Part A items meet the "
            "frequency threshold. These symptoms are highly consistent with adult "
            "ADHD. A formal diagnostic assessment by a qualified clinician is "
            "recommended. This result is not a diagnosis of ADHD."
        )
    return (
        f"Negative screen: {part_a_positive_count}/6 Part A items meet the "
        "frequency threshold (4 required for a positive screen). Reported symptoms "
        "are less consistent with adult ADHD, though clinical judgement should "
        "always be applied. If clinical concern persists, further assessment "
        "is warranted."
    )


def calculate(params: ASRSScreenerRequest | dict) -> CalculationResponse:
    """Score the ASRS-v1.1 questionnaire and return screening result."""
    req = (
        params
        if isinstance(params, ASRSScreenerRequest)
        else ASRSScreenerRequest(**params)
    )

    part_a_responses: list[FrequencyValue] = [
        req.q1,
        req.q2,
        req.q3,
        req.q4,
        req.q5,
        req.q6,
    ]
    part_b_responses: list[FrequencyValue] = [
        req.q7,
        req.q8,
        req.q9,
        req.q10,
        req.q11,
        req.q12,
        req.q13,
        req.q14,
        req.q15,
        req.q16,
        req.q17,
        req.q18,
    ]

    part_a_scores = [_SCORE_MAP[v] for v in part_a_responses]
    part_b_scores = [_SCORE_MAP[v] for v in part_b_responses]

    part_a_positive_count = sum(
        1 for i, score in enumerate(part_a_scores) if _part_a_item_positive(i, score)
    )

    part_a_total = sum(part_a_scores)
    part_b_total = sum(part_b_scores)
    total_score = part_a_total + part_b_total
    screen_result = "POSITIVE" if part_a_positive_count >= 4 else "NEGATIVE"

    working = {
        "description": (
            f"Part A screen: {screen_result} "
            f"({part_a_positive_count}/6 items above threshold). "
            f"Part A total: {part_a_total}/24. "
            f"Part B total: {part_b_total}/48. "
            f"Overall total score: {total_score}/72."
        ),
        "part_a_screen_result": screen_result,
        "part_a_positive_item_count": part_a_positive_count,
        "part_a_total_score": part_a_total,
        "part_b_total_score": part_b_total,
        "total_score": total_score,
        "part_a_items": {
            f"q{i + 1}": {
                "response": _LABEL_MAP[part_a_responses[i]],
                "score": part_a_scores[i],
                "positive": _part_a_item_positive(i, part_a_scores[i]),
            }
            for i in range(6)
        },
    }

    return CalculationResponse(
        result=part_a_positive_count,
        working=working,
        interpretation=_interpret_asrs(part_a_positive_count),
        reference=(
            "Kessler RC, Adler L, Ames M, et al. (2005). The World Health "
            "Organization Adult ADHD Self-Report Scale (ASRS): A short screening "
            "scale for use in the general population. Psychol Med. 35(2):245-56. "
            "doi:10.1017/S0033291704002892"
        ),
        metadata=build_metadata("asrs_screener"),
        tags=[
            "adhd",
            "asrs",
            "screening",
            "adult",
            "attention",
            "self-report",
            "psychiatry",
            "neurodevelopmental",
            "who",
        ],
    )
