from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import Settings


@dataclass
class LlmResponse:
    text: str
    used_fallback: bool = False


class LlmClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def complete(self, system: str, prompt: str) -> LlmResponse:
        provider = self.settings.llm_provider.lower()
        try:
            if provider == "ollama":
                return LlmResponse(self._complete_ollama(system, prompt))
            if provider == "openai_compatible":
                return LlmResponse(self._complete_openai_compatible(system, prompt))
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.settings.llm_provider}")
        except (urllib.error.URLError, TimeoutError, ValueError, KeyError, json.JSONDecodeError) as exc:
            return LlmResponse(f"LLM unavailable: {exc}", used_fallback=True)

    def _complete_ollama(self, system: str, prompt: str) -> str:
        url = self.settings.llm_base_url.rstrip("/") + "/api/chat"
        payload = {
            "model": self.settings.llm_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        data = self._post_json(url, payload)
        return data["message"]["content"]

    def _complete_openai_compatible(self, system: str, prompt: str) -> str:
        url = self.settings.llm_base_url.rstrip("/") + "/chat/completions"
        payload = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        data = self._post_json(url, payload)
        return data["choices"][0]["message"]["content"]

    def _post_json(self, url: str, payload: dict) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.settings.llm_api_key:
            headers["Authorization"] = f"Bearer {self.settings.llm_api_key}"

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            return json.loads(response.read().decode("utf-8"))
