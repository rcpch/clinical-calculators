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

## Creating a New Calculator

1. Create a new file in `calculators/` (e.g., `my_calculator.py`)
2. Define request and response Pydantic models
3. Implement the `calculate()` function
4. Add comprehensive tests in `tests/`
5. Document inputs/outputs in the function docstring

See existing calculators for examples.

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
