# RCPCH Clinical Calculators

A standardised collection of clinical calculators for healthcare professionals, provided by the Royal College of Paediatrics and Child Health (RCPCH).

This project provides clinical calculators as:

- **RESTful API** with FastAPI
- **Python package** for integration into Python projects
- **Command-line interface (CLI)** for terminal usage
- **Web interface** built with DaisyUI for browser access

## Available Calculators

Currently includes:

- **BMI Calculator** - Calculate Body Mass Index with weight category classification
- **HbA1c Converter** - Convert HbA1c between percentage (DCCT) and mmol/mol (IFCC)

## Quick Start

### Docker (Recommended)

```bash
# Start the API server
./s/dev up

# Access the API at http://localhost:8000
# Interactive docs at http://localhost:8000/docs
```

### Python Package

```python
from calculators.hba1c_converter import calculate

result = calculate({"input_unit": "percentage", "value": 7.0})
print(result)
```

### Command Line

```bash
calc run hba1c_converter --params '{"input_unit": "percentage", "value": 7.0}'
```

## Documentation

Complete documentation is available at:

📚 **[https://rcpch.github.io/clinical-calculators/docs.html](https://rcpch.github.io/clinical-calculators/docs.html)**

Or browse the documentation locally in the [docs/](docs/) folder:

- [Setup and Usage](docs/setup.md) - Installation, Docker, API, CLI, and Python package usage
- [Development Guide](docs/development.md) - How to contribute and create calculators
- [API Reference](docs/api-reference.md) - Complete API documentation
- [Calculator Specifications](docs/calculator-specs.md) - Guide for creating new calculators

## Web Interface

Try the calculators in your browser:

🌐 **[https://rcpch.github.io/clinical-calculators/](https://rcpch.github.io/clinical-calculators/)**

## Project Structure

## Technology Stack

- **Backend**: Python 3.11, FastAPI, Pydantic
- **Frontend**: DaisyUI, Tailwind CSS, Vanilla JavaScript
- **Testing**: pytest
- **Deployment**: Docker, GitHub Pages
- **Documentation**: Markdown with marked.js

## Repository Structure

```text
clinical-calculators/
│
├── calculators/                    # One file per calculator (e.g., bmi.py, hba1c_converter.py)
│   ├── __init__.py
│   ├── bmi.py
│   ├── hba1c_converter.py
│   └── ...
│
├── core/                          # Shared logic
│   ├── calculator.py             # Base class with config loading
│   ├── loader.py                 # Load by name, read config
│   └── metadata.py               # Versioning, metadata handling
│
├── cli/                          # CLI entry point
│   ├── main.py
│   └── templates/               # CLI templates (optional)
│
├── api/                         # FastAPI server
│   ├── main.py
│   └── schemas/                 # Pydantic models (auto-generated from config)
│
├── tests/                       # Unit & integration tests
│   ├── test_bmi.py
│   ├── test_hba1c_converter.py
│   └── ...
│
├── site/                        # GitHub Pages web client
│   ├── index.html              # Main calculator interface
│   ├── docs.html               # Documentation viewer
│   ├── app.js                  # Web client logic
│   ├── config.js               # API configuration
│   └── favicon.ico             # RCPCH logo
│
├── docs/                        # Documentation (markdown)
│   ├── index.md                # Documentation menu
│   ├── overview.md             # Project overview
│   ├── development.md          # Development guide
│   ├── api-reference.md        # API documentation
│   ├── calculator-specs.md     # Calculator creation guide
│   └── colors.md               # RCPCH brand colors
│
├── static/                      # Static assets for API
│   └── favicon.ico
│
├── s/                          # Development scripts
│   └── dev                  # Docker helper script
│
├── .github/
│   └── workflows/
│       └── deploy-pages.yml    # GitHub Pages deployment
│
├── pyproject.toml
├── setup.py
└── README.md
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- How to report issues
- Creating new calculators
- Development workflow
- Coding standards
- Submitting pull requests

## License

This project is licensed under the terms specified in [LICENSE](LICENSE).

## Support

- **Documentation**: [https://rcpch.github.io/clinical-calculators/docs.html](https://rcpch.github.io/clinical-calculators/docs.html)
- **Contributing**: [Contributing Guide](CONTRIBUTING.md)
- **Issues**: [GitHub Issues](https://github.com/rcpch/clinical-calculators/issues)
- **RCPCH**: [https://www.rcpch.ac.uk/](https://www.rcpch.ac.uk/)

---

**Royal College of Paediatrics and Child Health (RCPCH)**  
Providing clinical tools for healthcare professionals.
