"""
Service for interacting with hosted Ollama LLM for test generation.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


class OllamaService:
    """Service for generating tests using Ollama LLM."""

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
        self.api_key = os.getenv("OLLAMA_API_KEY")  # Optional API key
        self.timeout = 120.0  # Longer timeout for test generation

    async def generate_tests(
        self,
        calculator_spec: dict[str, Any],
        generated_code: str,
    ) -> str:
        """
        Generate comprehensive tests for a calculator using LLM.

        Args:
            calculator_spec: The calculator specification
            generated_code: The generated calculator code

        Returns:
            Enhanced test code as string
        """
        prompt = self._build_test_generation_prompt(calculator_spec, generated_code)

        # Build headers - use Ocp-Apim-Subscription-Key for Azure API Management
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Ocp-Apim-Subscription-Key"] = self.api_key

        # Check if using OpenAI-compatible endpoint (v1/chat/completions)
        is_openai_format = "/v1/chat/completions" in self.base_url

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if is_openai_format:
                # OpenAI-compatible format
                response = await client.post(
                    self.base_url,
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a medical software test engineer.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                    },
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                # Standard Ollama format
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

    def _build_test_generation_prompt(
        self,
        spec: dict[str, Any],
        code: str,
    ) -> str:
        """Build prompt for LLM to generate comprehensive tests."""
        calc_name = spec["calculator"]["name"]
        description = spec["calculator"]["description"]
        inputs = spec["inputs"]

        # Build input documentation
        input_docs = []
        for inp in inputs:
            input_docs.append(
                f"- {inp['name']} ({inp['type']}): {inp.get('description', '')}"
            )
            if "min" in inp:
                input_docs.append(f"  Min: {inp['min']}")
            if "max" in inp:
                input_docs.append(f"  Max: {inp['max']}")

        prompt = f"""You are a medical software test engineer. Generate comprehensive pytest tests for this clinical calculator.

CALCULATOR: {calc_name}
DESCRIPTION: {description}

INPUTS:
{chr(10).join(input_docs)}

GENERATED CODE:
```python
{code}
```

Generate a complete test file with the following test functions:
1. test_basic_calculation() - Test with typical values
2. test_edge_cases() - Test boundary conditions (min/max values)
3. test_invalid_inputs() - Test validation (out of range, wrong types)
4. test_response_structure() - Verify all response fields are present
5. test_clinical_scenarios() - 3-5 realistic clinical scenarios with known outcomes

Requirements:
- Use pytest syntax
- Include docstrings explaining each test
- Use realistic clinical values
- Test all validation rules (min/max)
- Include assertions for result, working, interpretation
- Follow existing test patterns

Output ONLY the Python code, no explanations. Start with imports."""

        return prompt


# Singleton instance
ollama_service = OllamaService()
