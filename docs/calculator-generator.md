# Calculator Generator

The calculator generator provides a web-based interface for creating new clinical calculators without writing code directly. It automates the entire process from specification to pull request.

## Overview

The generator allows contributors to:
- Define calculator specifications using a simple form
- Automatically generate Python code and tests
- Submit pull requests with one click via GitHub Actions
- Optionally enhance tests with AI
- Include attribution information

## Quick Start

1. **Open the Generator:** Navigate to `/site/generator.html`
2. **Fill in the Form:** Provide calculator details, inputs, and logic
3. **Generate Code:** Click "Generate Calculator" to create Python code and tests
4. **Submit PR:** Click "Submit PR" to automatically create a pull request

## Features

1. **Web-Based Interface** - No coding required, form-based calculator creation
2. **Automatic Code Generation** - Generates production-ready Python code and tests
3. **GitHub Actions Integration** - One-click PR creation via workflow automation
4. **User Attribution** - Optional GitHub username or name/affiliation fields
5. **AI Test Enhancement** - Coming soon: AI-generated comprehensive test cases

## How It Works

1. User fills in calculator specification form
2. Generator validates input and creates Python code
3. User clicks "Submit PR"
4. API triggers GitHub Actions workflow
5. Workflow creates branch, commits files, runs tests, and creates PR
6. PR appears in repository for review

For detailed workflow documentation, see [PR Automation Workflow](pr-automation-workflow.md).

## Setup

### Prerequisites

1. **GitHub CLI** - Install `gh` command-line tool:
   ```bash
   brew install gh
   gh auth login
   ```

2. **Ollama Service** - Hosted Ollama instance with API access

3. **Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file with your Ollama configuration:

```bash
OLLAMA_BASE_URL=https://your-ollama-instance.com
OLLAMA_MODEL=llama2
```

Or set environment variables:

```bash
export OLLAMA_BASE_URL=https://your-ollama-instance.com
export OLLAMA_MODEL=llama2
```

## Usage

### 1. Generate Calculator

1. Open `/site/generator.html` in browser
2. Fill in calculator details:
   - Description (auto-generates calculator name)
   - Clinical reference
   - Input parameters (name, type, description)
   - Calculation logic (result, working, interpretation)
3. Click "Generate"

### 2. Enhance Tests (Optional)

Click "Enhance Tests with AI" to use Ollama to generate:
- Edge case tests
- Validation tests
- Clinical scenario tests
- Boundary condition tests

### 3. Submit PR

Click "Submit PR" to automatically:
1. Create branch: `calculator/{name}`
2. Write files: `calculators/{name}.py` and `tests/test_{name}.py`
3. Run pytest to verify
4. Commit with descriptive message
5. Push to GitHub
6. Create pull request

## API Endpoints

### POST /generate-calculator
Generates calculator code from TOML specification.

**Request:**
```json
{
  "spec": "TOML specification string"
}
```

**Response:**
```json
{
  "success": true,
  "name": "calculator_name",
  "python_code": "...",
  "test_code": "...",
  "validation_errors": []
}
```

### POST /generate-enhanced-tests
Uses Ollama to generate comprehensive tests.

**Rate Limit:** 5 requests/minute

**Request:**
```json
{
  "spec": { "calculator": {...}, "inputs": [...] },
  "calculator_code": "..."
}
```

**Response:**
```json
{
  "success": true,
  "test_code": "..."
}
```

### POST /submit-calculator
Creates PR with calculator and tests.

**Rate Limit:** 3 requests/minute

**Request:**
```json
{
  "name": "calculator_name",
  "calculator_code": "...",
  "test_code": "...",
  "spec": {...}
}
```

**Response:**
```json
{
  "success": true,
  "branch": "calculator/name",
  "pr_url": "https://github.com/...",
  "test_results": "pytest output",
  "calculator_file": "calculators/name.py",
  "test_file": "tests/test_name.py"
}
```

## Troubleshooting

### Ollama Connection Issues

Check your Ollama service is accessible:
```bash
curl ${OLLAMA_BASE_URL}/api/tags
```

## Local Testing

Before submitting a calculator via PR, you can test it locally using the `s/test-generator` script. This validates that the generated code passes all checks (Black, isort, Ruff, pytest).

### Usage

1. Create a TOML specification file:
```toml
[calculator]
name = "my_calculator"
description = "My Calculator"
reference = "Reference citation"
logic = "result = input1 + input2"

[[inputs]]
name = "input1"
type = "number"
description = "First input"
required = true
min = 0
max = 100
```

2. Run the test script:
```bash
./s/test-generator my_calculator.toml
```

3. The script will:
   - Generate calculator and test code
   - Run Black formatter
   - Run isort import sorter
   - Run Ruff linter
   - Run pytest
   - Report any issues

4. If all checks pass, you'll see:
```
✅ All checks passed!

Files created:
  - calculators/my_calculator.py
  - tests/test_my_calculator.py

To clean up test files, run:
  rm calculators/my_calculator.py tests/test_my_calculator.py
```

### Note on Long Descriptions

Black formatter allows long string literals in function arguments. If you see very long description strings in `Field()` definitions, this is intentional and compliant with Black's formatting rules. The code will pass all checks.

Example of correct formatting:
```python
my_field: float = Field(
    ...,
    ge=0,
    le=100,
    description="This is a very long description that exceeds 88 characters but is allowed by Black when inside function arguments",
)
```

### GitHub CLI Not Authenticated

Run:
```bash
gh auth status
gh auth login
```

### Tests Failing

The PR service runs pytest before creating the PR. If tests fail, the PR will not be created. Check:
- All input variables are used in logic
- Logic syntax is valid Python
- All required response fields are present

## Architecture

### Services

- **OllamaService** (`core/ollama_service.py`) - Interfaces with Ollama API
- **GitHubPRService** (`core/pr_service.py`) - Handles Git operations and PR creation
- **Generator** (`core/generator.py`) - Generates calculator code from spec

### Frontend

- **generator.html** - Web interface with form-based calculator creation
- Reactive form with auto-generated variable names
- Real-time validation
- Action buttons for AI enhancement and PR submission

## Development

Run the API server:
```bash
uvicorn api.main:app --reload --port 8000
```

Open the generator UI:
```bash
open site/generator.html
```

## Future Enhancements

- [ ] OAuth for GitHub authentication
- [ ] Calculator preview/sandbox
- [ ] Version control for calculator edits
- [ ] Batch calculator generation
- [ ] Custom test templates
