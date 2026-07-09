import json
import httpx

# If using Ollama, uncomment below and make sure it matches your Ollama backend:
# OLLAMA_ENDPOINT = "http://localhost:11434/v1/chat/completions"


VLLM_ENDPOINT = "http://127.0.0.1:2242/v1"
REQUEST_TIMEOUT = 120.0

# Change 'endpoint: str = VLLM_ENDPOINT' to 'OLLAMA_ENDPOINT' if using Ollama

class InferenceClient:
    def __init__(self, endpoint: str = VLLM_ENDPOINT, timeout: float = REQUEST_TIMEOUT):
        self.endpoint = endpoint
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def complete(self, model: str, messages: list, runtime_params: dict) -> dict:
        payload = {
            "model": model,
            "messages": messages,
            **runtime_params
        }
        try:
            response = await self._client.post(self.endpoint, json=payload)
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            print(f"[INFERENCE CLIENT] Connection failed: {exc}")
            raise

        if response.status_code != 200:
            body = response.text
            if any(kw in body.lower() for kw in ("out of memory", "oom", "context length", "context window")):
                print("[VRAM WARNING] Allocation metrics exceeding VRAM limits. "
                      "Consider reducing model size, lowering max_tokens, or offloading layers.")
                print(f"[VRAM WARNING] Endpoint: {self.endpoint}")
            response.raise_for_status()

        return response.json()

    async def close(self):
        await self._client.aclose()

