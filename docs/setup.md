# Setup and Usage

This guide covers how to run and use the Clinical Calculators project.

## Run with Docker

### Build the image

```bash
docker build -t clinical-calculators:latest .
```

### Run the API

```bash
docker run --rm -p 8000:8000 clinical-calculators:latest
```

API will be available at <http://localhost:8000> (docs at /docs).

### Run in development with hot reload

```bash
docker compose up --build
```

### Use the CLI inside the container

```bash
docker run --rm clinical-calculators:latest calc list
docker run --rm clinical-calculators:latest calc run bmi --params '{"weight":70,"height":1.75,"unit_system":"metric"}'
```

## Dev Helper Script

To manage Docker in development, use:

```bash
./s/dev up      # build and start in background
./s/dev logs    # follow logs
./s/dev rebuild # rebuild image and restart
./s/dev down    # stop containers
./s/dev sh      # open shell in API container
```

## Using the API

### Make a calculation request

```bash
curl -X POST http://localhost:8000/calculate \
  -H "Content-Type: application/json" \
  -d '{"calculator": "hba1c_converter", "params": {"input_unit": "percentage", "value": 7.0}}'
```

Example result:

```json
{
  "result": 53.01,
  "working": {
    "formula": "IFCC (mmol/mol) = (DCCT (%) - 2.15) × 10.929",
    "calculation": "(7.0 - 2.15) × 10.929 = 53.01 mmol/mol"
  },
  "interpretation": "7.0% = 53.01 mmol/mol",
  "metadata": {
    "timestamp": "2025-12-14T10:00:00Z",
    "version": "0.1.0",
    "calculator_name": "hba1c_converter"
  },
  "reference": "NGSP/IFCC 2023 Guidelines"
}
```

### Interactive API Documentation

Visit <http://localhost:8000/docs> for Swagger UI documentation where you can try out the API endpoints interactively.

### Rate Limiting

The API includes rate limiting to prevent abuse and ensure fair usage:

- **Limit**: 100 requests per minute per IP address
- **Endpoint**: `/calculate` endpoint is rate-limited
- **Response**: When limit is exceeded, you'll receive a `429 Too Many Requests` response

Example rate limit response:
```json
{
  "detail": "Rate limit exceeded: 100 per 1 minute"
}
```

The rate limiting is permissive enough for normal usage but provides protection against automated attacks or excessive requests. If you need higher limits for legitimate use cases, please contact the maintainers.

## Using as a Python Package

Install the package in your Python project:

```python
from calculators.hba1c_converter import calculate

# Convert percentage to mmol/mol
result = calculate({"input_unit": "percentage", "value": 7.0})
print(result)

# Result:
# result=53.01 
# working={'formula': 'IFCC (mmol/mol) = (DCCT (%) - 2.15) × 10.929', ...}
# interpretation='7.0% = 53.01 mmol/mol'
# ...

# Convert mmol/mol to percentage
result = calculate({"input_unit": "mmol_mol", "value": 53.0})
print(result)

# Result:
# result=7.0
# working={'formula': 'DCCT (%) = (IFCC (mmol/mol) / 10.929) + 2.15', ...}
# interpretation='53.0 mmol/mol = 7.0%'
# ...
```

## Using the Command Line Interface (CLI)

### List available calculators

```bash
calc list
```

### Run a calculator

```bash
calc run hba1c_converter --params '{"input_unit": "percentage", "value": 7.0}'
```

Output:

```json
{
  "result": 53.01,
  "working": {
    "formula": "IFCC (mmol/mol) = (DCCT (%) - 2.15) × 10.929",
    "calculation": "(7.0 - 2.15) × 10.929 = 53.01 mmol/mol"
  },
  "interpretation": "7.0% = 53.01 mmol/mol",
  "metadata": {
    "timestamp": "2025-12-14T10:21:42.432281+00:00",
    "version": "0.1.0",
    "calculator_name": "hba1c_converter"
  },
  "reference": "NGSP/IFCC 2023 Guidelines"
}
```

## Web Interface

The project includes a modern web interface built with DaisyUI. 

### Local Development

After starting the API server, open the web interface:

1. Start the API: `./s/dev up`
2. Serve the web client from the repository root:
   ```bash
   python3 -m http.server 3000
   ```
3. Visit <http://localhost:3000/site/>

### Production

The web interface is deployed to GitHub Pages at:
<https://rcpch.github.io/clinical-calculators/>

## View the Documentation

Documentation is served from the web interface at `/site/docs.html` or directly at:
<https://rcpch.github.io/clinical-calculators/docs.html>
