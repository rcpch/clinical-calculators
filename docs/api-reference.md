# API Reference

The RCPCH Clinical Calculators API provides a RESTful interface for accessing clinical calculation tools.

## Base URL

- **Production**: `https://api.rcpch.ac.uk/clinical-calculators/v1`
- **Development**: `http://localhost:8000`

## Endpoints

### List Calculators

Get a list of all available calculators.

**Endpoint**: `GET /list`

**Response**:
```json
{
  "calculators": [
    {
      "name": "bmi",
      "title": "Body Mass Index (BMI) Calculator",
      "description": "Calculate BMI from height and weight"
    }
  ]
}
```

### Get Calculator Documentation

Retrieve the documentation for a specific calculator.

**Endpoint**: `GET /{calculator_name}/doc`

**Parameters**:
- `calculator_name` (path parameter): Name of the calculator (e.g., "bmi", "hba1c")

**Response**: Plain text documentation in a structured format including:
- Calculator description
- Input parameters with types and descriptions
- Output parameters with types and descriptions
- Example usage

### Calculate

Execute a calculation using a specific calculator.

**Endpoint**: `POST /calculate`

**Request Body**:
```json
{
  "calculator_name": "bmi",
  "inputs": {
    "height_m": 1.75,
    "weight_kg": 70
  }
}
```

**Response**:
```json
{
  "bmi": 22.86,
  "category": "Normal weight",
  "healthy_weight_range_kg": "56.7 - 76.6"
}
```

**Error Response**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Available Calculators

### BMI Calculator

Calculate Body Mass Index and weight category.

**Calculator Name**: `bmi`

**Inputs**:
- `height_m` (float): Height in meters
- `weight_kg` (float): Weight in kilograms

**Outputs**:
- `bmi` (float): Calculated BMI value
- `category` (string): Weight category (Underweight, Normal weight, Overweight, Obese)
- `healthy_weight_range_kg` (string): Recommended weight range

### HbA1c Converter

Convert HbA1c between percentage and mmol/mol units.

**Calculator Name**: `hba1c`

**Inputs** (provide one):
- `hba1c_percentage` (float): HbA1c as percentage (e.g., 6.5)
- `hba1c_mmol_mol` (float): HbA1c in mmol/mol (e.g., 48)

**Outputs**:
- `hba1c_percentage` (float): HbA1c as percentage
- `hba1c_mmol_mol` (float): HbA1c in mmol/mol
- `interpretation` (string): Clinical interpretation

## CORS

The API supports Cross-Origin Resource Sharing (CORS) and can be accessed from web applications.

**Allowed Origins**: `*` (all origins)

**Allowed Methods**: `GET`, `POST`, `OPTIONS`

## Error Handling

The API uses standard HTTP status codes:

- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid input or missing required parameters
- `404 Not Found`: Calculator not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, there are no rate limits on the API, but this may change in production deployments.

## Examples

### Python

```python
import requests

# List calculators
response = requests.get('https://api.rcpch.ac.uk/clinical-calculators/v1/list')
calculators = response.json()

# Calculate BMI
response = requests.post(
    'https://api.rcpch.ac.uk/clinical-calculators/v1/calculate',
    json={
        'calculator_name': 'bmi',
        'inputs': {
            'height_m': 1.75,
            'weight_kg': 70
        }
    }
)
result = response.json()
print(f"BMI: {result['bmi']}, Category: {result['category']}")
```

### JavaScript

```javascript
// List calculators
const response = await fetch('https://api.rcpch.ac.uk/clinical-calculators/v1/list');
const data = await response.json();

// Calculate HbA1c
const result = await fetch(
    'https://api.rcpch.ac.uk/clinical-calculators/v1/calculate',
    {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            calculator_name: 'hba1c',
            inputs: { hba1c_percentage: 6.5 }
        })
    }
);
const conversion = await result.json();
console.log(`${conversion.hba1c_percentage}% = ${conversion.hba1c_mmol_mol} mmol/mol`);
```

### cURL

```bash
# List calculators
curl https://api.rcpch.ac.uk/clinical-calculators/v1/list

# Calculate BMI
curl -X POST https://api.rcpch.ac.uk/clinical-calculators/v1/calculate \
  -H "Content-Type: application/json" \
  -d '{"calculator_name":"bmi","inputs":{"height_m":1.75,"weight_kg":70}}'
```
