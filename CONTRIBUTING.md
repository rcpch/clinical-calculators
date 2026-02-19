# Contributing to RCPCH Clinical Calculators

We welcome contributions to the RCPCH Clinical Calculators project! This guide will help you get started with contributing.

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion for improvement:

1. Check if the issue already exists in [GitHub Issues](https://github.com/rcpch/clinical-calculators/issues)
2. If not, create a new issue with:
   - A clear, descriptive title
   - Detailed description of the problem or suggestion
   - Steps to reproduce (for bugs)
   - Expected vs actual behavior
   - Your environment details (OS, Python version, etc.)

### Contributing Code

#### Prerequisites

Before you start, make sure you have:

- Git installed and configured
- Docker and Docker Compose installed
- Python 3.11+ (for local development without Docker)
- A GitHub account

#### Getting Started

1. **Fork the repository**
   - Visit [https://github.com/rcpch/clinical-calculators](https://github.com/rcpch/clinical-calculators)
   - Click the "Fork" button in the top right

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/clinical-calculators.git
   cd clinical-calculators
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/rcpch/clinical-calculators.git
   ```

4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Workflow

1. **Start the development environment**
   ```bash
   ./s/dev up
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Write or update tests as needed
   - Update documentation if required

3. **Run linting checks**
   ```bash
   ./s/lint
   ```
   
   Or inside Docker:
   ```bash
   docker compose run --rm api ./s/lint
   ```
   
   The linter runs three tools:
   - **Black**: Code formatter (line length 88)
   - **isort**: Import organizer
   - **Ruff**: Fast Python linter
   
   To auto-fix most issues:
   ```bash
   docker compose run --rm api black calculators core cli api tests
   docker compose run --rm api isort calculators core cli api tests
   docker compose run --rm api ruff check --fix calculators core cli api tests
   ```

4. **Run tests**
   ```bash
   docker compose run --rm api pytest
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Clear, concise commit message describing the change"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Submit a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Select the `live` branch as the base branch
   - Provide a clear title and description
   - Link any related issues

## Creating a New Calculator

To add a new calculator to the project:

### Step 1: Plan Your Calculator

Before coding, consider:

- **Purpose**: What clinical calculation will this perform?
- **Inputs**: What parameters are needed?
- **Outputs**: What results will be returned?
- **Validation**: What input validation is required?
- **References**: What clinical guidelines or literature support this?

### Step 2: Create the Calculator File

1. Create a new Python file in `calculators/` (e.g., `calculators/my_calculator.py`)

2. Add a TOML-formatted docstring at the top describing the calculator

3. Import required dependencies:
   ```python
   from core.request.request import CalculatorRequest
   from core.response.response import CalculationResponse
   from pydantic import Field, field_validator
   ```

4. Define your request model (inheriting from `CalculatorRequest`)

5. Implement the `calculate()` function returning a `CalculationResponse`

See [Calculator Specifications](calculator-specs.md) for detailed guidance.

### Step 3: Write Tests

Create comprehensive tests in `tests/test_my_calculator.py`:

```python
import pytest
from calculators.my_calculator import calculate, MyCalculatorRequest

def test_basic_calculation():
    """Test basic functionality."""
    result = calculate({"param1": value1, "param2": value2})
    assert result.result == expected_value

def test_validation():
    """Test input validation."""
    with pytest.raises(ValueError):
        MyCalculatorRequest(param1=invalid_value)

def test_edge_cases():
    """Test boundary conditions."""
    # Add edge case tests
    pass
```

### Step 4: Update Documentation

1. Your calculator will automatically appear in the API
2. Consider adding examples to the API reference documentation
3. Update the README if this is a major calculator addition

### Step 5: Submit Your Contribution

1. Ensure all tests pass
2. Commit your changes with clear messages
3. Push to your fork
4. Create a Pull Request to the `live` branch

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise

### Validation

- Use Pydantic validators for input validation
- Provide clear error messages
- Validate all clinical safety requirements

### Testing

- Write tests for all new features
- Test normal cases, edge cases, and error conditions
- Aim for high test coverage
- Use descriptive test names

### Documentation

- Update relevant documentation for any changes
- Use clear, concise language
- Include examples where helpful
- Reference clinical guidelines when applicable

## Code Review Process

All contributions go through code review:

1. **Automated Checks**: GitHub Actions will run tests automatically
2. **Peer Review**: A maintainer will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

### What Reviewers Look For

- **Correctness**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow project conventions?
- **Clinical Safety**: Are calculations accurate and validated?

## Types of Contributions

We welcome various types of contributions:

### New Calculators

Add new clinical calculators following the specifications.

### Bug Fixes

Fix bugs in existing calculators or infrastructure.

### Documentation

Improve documentation, add examples, fix typos.

### Tests

Add or improve test coverage.

### Infrastructure

Improve build, deployment, or development tools.

### Web Interface

Enhance the DaisyUI web client.

## Getting Help

If you need help with your contribution:

- **Documentation**: Check our [documentation](https://rcpch.github.io/clinical-calculators/docs.html)
- **Issues**: Ask questions in [GitHub Issues](https://github.com/rcpch/clinical-calculators/issues)
- **Discussions**: Start a discussion on GitHub
- **RCPCH**: Visit [https://www.rcpch.ac.uk/](https://www.rcpch.ac.uk/)

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](../LICENSE)).

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members

## Recognition

Contributors will be recognized in:

- Git commit history
- GitHub contributors list
- Project acknowledgments

Thank you for contributing to RCPCH Clinical Calculators! Your contributions help improve healthcare tools for professionals worldwide.

---

**Questions?** Open an issue or reach out to the RCPCH team.
