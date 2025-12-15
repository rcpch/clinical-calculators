#!/usr/bin/env python3
"""Test script to query the Ollama API and identify the model."""

import json
import os

try:
    import httpx
except ImportError:
    httpx = None

try:
    import pytest
except ImportError:
    pytest = None

API_KEY = os.getenv("OLLAMA_API_KEY", "9bcb8412b18847a7863ae7a4611be49c")
BASE_URL = os.getenv(
    "OLLAMA_BASE_URL", "https://api.rcpch.ac.uk/ollama/v1/chat/completions"
)


def is_ollama_available():
    """Check if Ollama service is configured and available."""
    if not httpx or not BASE_URL or not API_KEY:
        return False

    try:
        # Quick health check
        with httpx.Client(timeout=5.0) as client:
            response = client.get(
                BASE_URL.replace("/v1/chat/completions", "/health"),
                headers={"Ocp-Apim-Subscription-Key": API_KEY},
            )
            return response.status_code < 500
    except Exception:
        return False


if pytest:

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not is_ollama_available(), reason="Ollama API not available or not configured"
    )
    async def test_model_detection():
        """Test the Ollama API with different models."""
        await _query_ollama_models()


async def _query_ollama_models():
    """Test the API with different models."""

    models_to_try = ["llama2", "llama3", "mistral", "qwen2.5", "deepseek-r1"]

    headers = {"Ocp-Apim-Subscription-Key": API_KEY, "Content-Type": "application/json"}

    for model in models_to_try:
        print(f"\nTrying model: {model}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    BASE_URL,
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "user",
                                "content": "Say 'Hello, I am working!' and nothing else.",
                            }
                        ],
                        "max_tokens": 20,
                        "temperature": 0.1,
                    },
                    headers=headers,
                )

                print(f"Status: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Success with {model}!")
                    print(f"Response: {json.dumps(result, indent=2)}")
                    return model
                else:
                    print(f"❌ Error: {response.text}")

        except Exception as e:
            print(f"❌ Exception: {e}")

    return None


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(_query_ollama_models())
    if result:
        print(f"\n✅ Working model found: {result}")
    else:
        print("\n❌ No working model found")
