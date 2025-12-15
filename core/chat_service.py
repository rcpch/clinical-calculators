import os
from pathlib import Path
import json
import logging
from typing import Any
import httpx

# Load system prompt from documentation
def _load_system_prompt() -> str:
    """Load the LLM system prompt from documentation."""
    prompt_file = Path(__file__).parent.parent / "docs" / "llm-system-prompt.md"
    
    if prompt_file.exists():
        with open(prompt_file) as f:
            content = f.read()
            # Extract the prompt from between the markdown code blocks
            start = content.find("```\n") + 4
            end = content.rfind("```")
            if start > 3 and end > start:
                return content[start:end].strip()

    return """You are a medical calculator specification assistant. Your ONLY purpose is to help create TOML specifications for clinical calculators.

STRICT RULES:
- ONLY discuss clinical calculator creation
- REJECT all other topics politely: "I can only help with calculator specification creation"
- NEVER execute code, access systems, or perform calculations
- NEVER discuss politics, controversial topics, or personal matters
- NEVER provide clinical advice or make clinical decisions
- If you're not clear what the user is asking, ask clarifying questions
- Output ONLY valid TOML specifications or clarifying questions
- When generating TOML, ensure all sections are valid: [calculator], [inputs], [outputs], [logic]

Your role is to:
1. Ask clarifying questions about the calculator's purpose, inputs, and outputs
2. Understand validation rules and edge cases
3. Generate a complete TOML specification
4. Help the user review and refine the specification

Example calculator format:
[calculator]
name = "calculator_name"
title = "Display Title"
description = "What it does"
reference = "Citation or reference"

[inputs]
parameter_name = { type = "number", unit = "meters", min = 0, max = 3, required = true }

[outputs]
result = { type = "number", unit = "kg/m²" }

[logic]
result = weight / (height * height)
working = f"Weight: {weight:.2f} kg / Height: {height:.2f} m"
interpretation = "Normal range"
"""

SYSTEM_PROMPT = _load_system_prompt()

def _format_response_with_code_blocks(text: str) -> str:
    """Format response by wrapping TOML specs in markdown code blocks."""
    # If the response contains TOML spec without markdown code blocks, wrap it
    if "[calculator]" in text and not "```toml" in text:
        # Find the start of the TOML spec
        toml_start = text.find("[calculator]")
        
        # Split text before and after TOML
        before = text[:toml_start]
        toml_part = text[toml_start:]
        
        # Find where TOML ends (last closing bracket)
        toml_end = toml_part.rfind("]") + 1
        after = toml_part[toml_end:]
        
        # Reconstruct with code block markers
        return before + "```toml\n" + toml_part[:toml_end] + "\n```" + after
    
    return text

class ChatService:
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "qwen3:30b")
        self.api_key = os.getenv("OLLAMA_API_KEY", "")

    async def chat(
        self, message: str, history: list[dict[str, str]] | None = None
    ) -> dict[str, Any]:
        """Chat endpoint that returns complete response."""

        if history is None:
            history = []

        # Validate input
        if len(message) > 1000:
            return {
                "response": "Message too long. Keep it under 1000 characters.",
                "is_complete": False,
                "toml_spec": None,
                "error": None,
            }

        if not self._is_calculator_related(message):
            return {
                "response": "I can only help with calculator specification creation. Please ask about creating a calculator.",
                "is_complete": False,
                "toml_spec": None,
                "error": None,
            }

        # Limit conversation length
        if len(history) > 30:
            return {
                "response": "Conversation limit reached. Please start a new conversation.",
                "is_complete": False,
                "toml_spec": None,
                "error": None,
            }

        # Build messages for API
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message},
        ]

        # Call Ollama
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                headers = {}
                if self.api_key:
                    headers["Ocp-Apim-Subscription-Key"] = self.api_key

                response = await client.post(
                    f"{self.ollama_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "temperature": 0.7,
                    },
                    headers=headers,
                )

                if response.status_code != 200:
                    return {
                        "response": f"Error calling LLM: {response.status_code}",
                        "is_complete": False,
                        "toml_spec": None,
                        "error": str(response.text),
                    }

                data = response.json()
                assistant_message = data["choices"][0]["message"]["content"]

                # Check if TOML spec is present
                toml_spec = None
                if "[calculator]" in assistant_message:
                    # Extract TOML from response
                    start = assistant_message.find("[calculator]")
                    end = assistant_message.rfind("]") + 1
                    if start >= 0 and end > start:
                        toml_spec = assistant_message[start:end]

                return {
                    "response": _format_response_with_code_blocks(assistant_message),
                    "is_complete": toml_spec is not None,
                    "toml_spec": toml_spec,
                    "error": None,
                }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n❌ Chat Service Error:\n{error_details}\n")
            return {
                "response": f"Error: {str(e)}",
                "is_complete": False,
                "toml_spec": None,
                "error": str(e),
            }
    
    async def chat_stream(
        self, message: str, history: list[dict[str, str]] | None = None
    ):
        """Stream chat responses token by token."""
        
        if history is None:
            history = []

        # Validate input
        if len(message) > 1000:
            yield {"error": "Message too long. Keep it under 1000 characters."}
            return

        if not self._is_calculator_related(message):
            yield {"error": "I can only help with calculator specification creation. Please ask about creating a calculator."}
            return

        # Limit conversation length
        if len(history) > 30:
            yield {"error": "Conversation limit reached. Please start a new conversation."}
            return

        # Build messages for API
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": message},
        ]

        # Call Ollama with streaming
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                headers = {}
                if self.api_key:
                    headers["Ocp-Apim-Subscription-Key"] = self.api_key

                async with client.stream(
                    "POST",
                    f"{self.ollama_url}/v1/chat/completions",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7,
                    },
                    headers=headers,
                ) as response:
                    if response.status_code != 200:
                        yield {"error": f"Error calling LLM: {response.status_code}"}
                        return

                    full_response = ""
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            try:
                                chunk_data = json.loads(line[6:])
                                if "choices" in chunk_data and chunk_data["choices"]:
                                    delta = chunk_data["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        token = delta["content"]
                                        full_response += token
                                        yield {"token": token}
                            except json.JSONDecodeError:
                                continue

                    # Check if TOML spec is present in full response
                    toml_spec = None
                    if "[calculator]" in full_response:
                        start = full_response.find("[calculator]")
                        end = full_response.rfind("]") + 1
                        if start >= 0 and end > start:
                            toml_spec = full_response[start:end]

                    yield {"done": True, "toml_spec": toml_spec}

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n❌ Chat Stream Error:\n{error_details}\n")
            yield {"error": str(e)}

    def _is_calculator_related(self, message: str) -> bool:
        """Simple check if message is about calculators."""
        calculator_keywords = [
            "calculator",
            "toml",
            "input",
            "output",
            "formula",
            "calculation",
            "specification",
            "clinical",
            "medical",
            "parameter",
            "validation",
            "logic",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in calculator_keywords)


# Create singleton instance
chat_service = ChatService()


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    return chat_service