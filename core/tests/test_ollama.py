#!/usr/bin/env python3
"""Test script to query the Ollama API and identify the model."""

import httpx
import json

API_KEY = "9bcb8412b18847a7863ae7a4611be49c"
BASE_URL = "https://api.rcpch.ac.uk/ollama/v1/chat/completions"

async def test_model():
    """Test the API with different models."""
    
    models_to_try = ["llama2", "llama3", "mistral", "qwen2.5", "deepseek-r1"]
    
    headers = {
        "Ocp-Apim-Subscription-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    for model in models_to_try:
        print(f"\nTrying model: {model}")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    BASE_URL,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
                        ],
                        "max_tokens": 20,
                        "temperature": 0.1
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
    result = asyncio.run(test_model())
    if result:
        print(f"\n✅ Working model found: {result}")
    else:
        print("\n❌ No working model found")
