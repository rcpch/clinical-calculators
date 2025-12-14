# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on

WORKDIR /app

# System deps (optional: build tools if needed for deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip

# Copy project files for dependency installation
COPY pyproject.toml setup.py ./
COPY calculators ./calculators
COPY core ./core
COPY cli ./cli
COPY api ./api

# Install package with dependencies
RUN pip install -e .

# Copy rest of project (tests, docs, etc.)
COPY . .

EXPOSE 8000

# Default to running the API; override command for CLI usage
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# Test stage (optional): build and run tests
FROM base AS test
RUN pip install -e .[dev]
