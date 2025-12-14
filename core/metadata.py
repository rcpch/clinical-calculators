from __future__ import annotations

import os
from datetime import UTC, datetime
from typing import Any

PACKAGE_VERSION = os.environ.get("CLINICAL_CALCULATORS_VERSION", "0.1.0")


def build_metadata(calculator_name: str) -> dict[str, Any]:
    """Return common metadata for responses.

    Includes ISO8601 timestamp (UTC), version, and calculator name.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "version": PACKAGE_VERSION,
        "calculator_name": calculator_name,
    }
