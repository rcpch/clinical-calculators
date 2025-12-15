# Calculator Generator - Automated Workflow

This feature provides an automated workflow for creating clinical calculators with AI-enhanced tests and automatic PR submission.

## Features

1. **Web-Based Calculator Generator** - User-friendly form interface
2. **AI-Enhanced Test Generation** - Uses Ollama to generate comprehensive tests
3. **Automated PR Submission** - One-click branch creation, testing, and PR

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
