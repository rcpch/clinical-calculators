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
            # Look for the System Prompt section and extract everything until Security Constraints
            system_prompt_start = content.find("## System Prompt")
            if system_prompt_start == -1:
                logging.warning("System Prompt section not found in LLM system prompt file.")
                return None
            
            # Start after the "## System Prompt" header
            start_pos = content.find("\n", system_prompt_start) + 1
            
            # Find where it ends (at Security Constraints section or end of file)
            end_pos = content.find("\n## ", start_pos)
            if end_pos == -1:
                end_pos = len(content)
            
            prompt_text = content[start_pos:end_pos].strip()
            
            if prompt_text:
                return prompt_text
            
            logging.warning("Could not extract system prompt from file.")
            return None
    else:
        logging.warning("LLM system prompt file not found.")
        return None

SYSTEM_PROMPT = _load_system_prompt()

if not SYSTEM_PROMPT:
    logging.error("SYSTEM_PROMPT is None or empty - chat will fail!")
    print("❌ ERROR: System prompt failed to load")

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
                                        # Check if TOML spec is present in full response
                    toml_spec = None
                    if "[calculator]" in full_response:
                        start = full_response.find("[calculator]")
                        # Look for the next section marker or end of TOML
                        # TOML sections start with [, so we look for a line that starts with [
                        # that's not part of the content
                        remaining = full_response[start:]
                        
                        # Split by lines and find the end of TOML
                        lines = remaining.split('\n')
                        toml_lines = []
                        last_toml_line_idx = -1
                        
                        for idx, line in enumerate(lines):
                            stripped = line.strip()
                            
                            # TOML lines contain: sections ([...], [[...]]), key-value pairs (key = value), or are empty/comments
                            is_toml_line = (
                                not stripped  # empty line
                                or stripped.startswith('#')  # comment
                                or stripped.startswith('[')  # section header
                                or '=' in stripped  # key-value pair
                            )
                            
                            if is_toml_line:
                                toml_lines.append(line)
                                if stripped:  # Track last non-empty TOML line
                                    last_toml_line_idx = len(toml_lines) - 1
                            else:
                                # Non-TOML content encountered - check if we've seen enough TOML
                                if last_toml_line_idx >= 0:
                                    # We've collected some TOML, stop here
                                    break
                                # Otherwise this might be before the TOML starts, skip it
                        
                        # Trim trailing empty lines
                        if last_toml_line_idx >= 0:
                            toml_lines = toml_lines[:last_toml_line_idx + 1]
                        
                        toml_spec = '\n'.join(toml_lines).strip()
                        
                        # Validate it looks like complete TOML
                        if toml_spec and '[calculator]' in toml_spec:
                            # Make sure it has at least the basic sections
                            if '[[inputs]]' not in toml_spec:
                                toml_spec = None  # Incomplete
                        else:
                            toml_spec = None

                    yield {"done": True, "toml_spec": toml_spec}

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"\n❌ Chat Stream Error:\n{error_details}\n")
            yield {"error": str(e)}


# Create singleton instance
chat_service = ChatService()


def get_chat_service() -> ChatService:
    """Get chat service instance."""
    return chat_service