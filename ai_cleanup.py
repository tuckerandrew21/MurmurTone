"""
AI-powered text cleanup using local Ollama LLM.
Provides grammar fixes and formality adjustments while staying 100% offline.
"""
import json
import requests
from typing import Optional, List, Callable
from urllib.parse import urlparse


def validate_ollama_url(url: str) -> bool:
    """
    Validate Ollama URL is safe (localhost or private IP only).

    This prevents SSRF attacks by restricting URLs to local/private networks.

    Args:
        url: URL to validate

    Returns:
        True if URL is safe to use, False otherwise
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = parsed.hostname or ""
        # Allow localhost variants
        if host in ("localhost", "127.0.0.1", "::1"):
            return True
        # Allow private IP ranges (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
        if host.startswith(("192.168.", "10.")):
            return True
        # Check 172.16.0.0 - 172.31.255.255 range
        if host.startswith("172."):
            parts = host.split(".")
            if len(parts) >= 2:
                try:
                    second_octet = int(parts[1])
                    if 16 <= second_octet <= 31:
                        return True
                except ValueError:
                    pass
        return False
    except Exception:
        return False


def check_ollama_available(url: str = "http://localhost:11434") -> bool:
    """
    Check if Ollama is running and accessible.

    Args:
        url: Ollama API URL

    Returns:
        True if Ollama is reachable, False otherwise
    """
    # Validate URL before making request (prevents SSRF)
    if not validate_ollama_url(url):
        return False

    try:
        response = requests.get(f"{url}/api/tags", timeout=2)
        return response.status_code == 200
    except (requests.RequestException, Exception):
        return False


def get_available_models(url: str = "http://localhost:11434") -> List[str]:
    """
    Query Ollama for list of installed models.

    Args:
        url: Ollama API URL

    Returns:
        List of model names, empty list if Ollama unavailable
    """
    # Validate URL before making request (prevents SSRF)
    if not validate_ollama_url(url):
        return []

    try:
        response = requests.get(f"{url}/api/tags", timeout=2)
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get("models", []):
                name = model.get("name", "")
                if name:
                    models.append(name)
            return models
        return []
    except (requests.RequestException, Exception):
        return []


def _build_cleanup_prompt(text: str, mode: str, formality_level: str) -> str:
    """
    Build appropriate prompt for text cleanup.

    Args:
        text: Text to clean up
        mode: "grammar", "formality", or "both"
        formality_level: "casual", "professional", or "formal"

    Returns:
        Formatted prompt for Ollama
    """
    if mode == "grammar":
        prompt = f"""Fix any grammar, spelling, and punctuation errors in the following text. Preserve the original tone and style. Only output the corrected text, nothing else.

Text: {text}

Corrected:"""
    elif mode == "formality":
        level_desc = {
            "casual": "casual and conversational",
            "professional": "professional and polished",
            "formal": "formal and academic"
        }.get(formality_level, "professional")

        prompt = f"""Rewrite the following text to be {level_desc} while preserving the core message. Only output the rewritten text, nothing else.

Text: {text}

Rewritten:"""
    else:  # both
        level_desc = {
            "casual": "casual and conversational",
            "professional": "professional and polished",
            "formal": "formal and academic"
        }.get(formality_level, "professional")

        prompt = f"""Fix any grammar, spelling, and punctuation errors, and rewrite to be {level_desc}. Preserve the core message. Only output the improved text, nothing else.

Text: {text}

Improved:"""

    return prompt


def cleanup_text(
    text: str,
    mode: str = "grammar",
    formality_level: str = "professional",
    model: str = "llama3.2:3b",
    url: str = "http://localhost:11434",
    timeout: int = 30
) -> Optional[str]:
    """
    Send text to Ollama for cleanup and return improved version.

    Args:
        text: Text to clean up
        mode: "grammar", "formality", or "both"
        formality_level: "casual", "professional", or "formal"
        model: Ollama model to use
        url: Ollama API URL
        timeout: Request timeout in seconds

    Returns:
        Cleaned up text, or None if cleanup failed
    """
    if not text or not text.strip():
        return None

    # Validate URL before making request (prevents SSRF)
    if not validate_ollama_url(url):
        return None

    try:
        # Build prompt
        prompt = _build_cleanup_prompt(text, mode, formality_level)

        # Send request to Ollama
        response = requests.post(
            f"{url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent output
                    "top_p": 0.9,
                }
            },
            timeout=timeout
        )

        if response.status_code == 200:
            data = response.json()
            cleaned = data.get("response", "").strip()

            # Basic validation - ensure we got something back
            if cleaned and len(cleaned) > 0:
                return cleaned
            else:
                return None
        else:
            return None

    except (requests.RequestException, Exception):
        return None


def test_ollama_connection(model: str, url: str = "http://localhost:11434") -> tuple[bool, str]:
    """
    Test connection to Ollama and verify model availability.

    Args:
        model: Model name to test
        url: Ollama API URL

    Returns:
        Tuple of (success, message)
    """
    # Check if Ollama is running
    if not check_ollama_available(url):
        return False, "Ollama is not running or not accessible."

    # Check if model is available
    models = get_available_models(url)
    if not models:
        return False, "Could not retrieve model list from Ollama."

    # Check if requested model is installed
    model_base = model.split(":")[0]  # Handle versions like "llama3.2:3b"
    if not any(model_base in m for m in models):
        return False, f"Model '{model}' is not installed. Available models: {', '.join(models)}"

    # Try a simple test (60s timeout to allow for first-time model loading)
    test_result = cleanup_text(
        "test",
        mode="grammar",
        model=model,
        url=url,
        timeout=60
    )

    if test_result is not None:
        return True, f"Connection successful! Using model: {model}"
    else:
        return False, "Connection succeeded but model did not respond correctly."


def pull_ollama_model(
    model: str = "llama3.2:3b",
    url: str = "http://localhost:11434",
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> tuple[bool, str]:
    """
    Pull (download) an Ollama model with progress tracking.

    Args:
        model: Model name to pull (e.g., "llama3.2:3b")
        url: Ollama API URL
        progress_callback: Optional callback(percent: int, status: str)
            - percent: 0-100 for determinate progress, -1 for indeterminate
            - status: Human-readable status message

    Returns:
        Tuple of (success, message)
    """
    if not validate_ollama_url(url):
        return False, "Invalid Ollama URL"

    try:
        response = requests.post(
            f"{url}/api/pull",
            json={"model": model, "stream": True},
            stream=True,
            timeout=1800  # 30 min timeout for large models
        )

        if response.status_code != 200:
            return False, f"HTTP {response.status_code}: {response.text}"

        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode())
                except json.JSONDecodeError:
                    continue

                status = data.get("status", "")
                error = data.get("error", "")

                if error:
                    return False, error

                # Calculate progress percentage
                if "completed" in data and "total" in data:
                    total = data["total"]
                    completed = data["completed"]
                    if total > 0:
                        percent = int((completed / total) * 100)
                        mb_done = completed / (1024 * 1024)
                        mb_total = total / (1024 * 1024)
                        if progress_callback:
                            progress_callback(percent, f"Downloading: {mb_done:.1f} / {mb_total:.1f} MB")
                elif status == "success":
                    if progress_callback:
                        progress_callback(100, "Download complete!")
                    return True, f"Model {model} downloaded successfully"
                elif progress_callback:
                    # Indeterminate progress for status messages
                    progress_callback(-1, status)

        return True, f"Model {model} pulled successfully"

    except requests.Timeout:
        return False, "Download timed out"
    except requests.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


def delete_ollama_model(
    model: str,
    url: str = "http://localhost:11434"
) -> tuple[bool, str]:
    """
    Delete an Ollama model to free disk space.

    Args:
        model: Model name to delete (e.g., "llama3.2:3b")
        url: Ollama API URL

    Returns:
        Tuple of (success, message)
    """
    if not validate_ollama_url(url):
        return False, "Invalid Ollama URL"

    if not model or not model.strip():
        return False, "Model name is required"

    try:
        response = requests.delete(
            f"{url}/api/delete",
            json={"model": model},
            timeout=30
        )

        if response.status_code == 200:
            return True, f"Model {model} deleted successfully"
        elif response.status_code == 404:
            return False, f"Model {model} not found"
        else:
            return False, f"HTTP {response.status_code}: {response.text}"

    except requests.RequestException as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


def get_ollama_models_with_sizes(url: str = "http://localhost:11434") -> List[dict]:
    """
    Get list of installed Ollama models with their sizes.

    Args:
        url: Ollama API URL

    Returns:
        List of dicts with 'name', 'size', and 'modified' keys
    """
    if not validate_ollama_url(url):
        return []

    try:
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = []
            for m in data.get("models", []):
                models.append({
                    "name": m.get("name", ""),
                    "size": m.get("size", 0),
                    "modified": m.get("modified_at", "")
                })
            return models
        return []
    except (requests.RequestException, Exception):
        return []
