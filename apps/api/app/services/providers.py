from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx

from app.config import Settings
from app.security import UNTRUSTED_EVIDENCE_INSTRUCTION


class ModelProvider(ABC):
    @abstractmethod
    async def generate_json(self, instruction: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class DeterministicProvider(ModelProvider):
    async def generate_json(self, instruction: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {"mode": "deterministic", "instruction": instruction[:80], "input": payload}


class GeminiProvider(ModelProvider):  # pragma: no cover - provider integration test
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_json(self, instruction: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.settings.llm_model}:generateContent?key={self.settings.gemini_api_key}"
        )
        prompt = f"{instruction}\n\n{UNTRUSTED_EVIDENCE_INSTRUCTION}\n\nINPUT JSON:\n{json.dumps(payload)}"
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.2},
        }
        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            response = await client.post(url, json=body)
        response.raise_for_status()
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)


def get_model_provider(settings: Settings) -> ModelProvider:
    if settings.provider_mode == "gemini":
        return GeminiProvider(settings)
    return DeterministicProvider()
