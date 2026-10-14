"""LLM provider interface. Everything works with ``FakeLLM`` (deterministic,
offline); Apertus (Public AI, OpenAI-compatible API) plugs in behind the same
interface. No identifiable candidate data is ever sent to a provider
(docs/recherche/legal.md).
"""

from __future__ import annotations

import json
import os
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import httpx

from proxsis.llm.secrets import publicai_api_key
from proxsis.netcheck import USER_AGENT

DEFAULT_APERTUS_MODEL = "swiss-ai/apertus-v1.5-8b"


@dataclass
class LLMResult:
    data: dict[str, Any]
    provider: str
    model: str
    latency_s: float
    raw: str = ""
    usage: dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    name: str = "base"
    model: str = "none"

    @abstractmethod
    def extract(self, system: str, user: str, schema: dict[str, Any], schema_name: str) -> LLMResult:
        """Return a JSON object conforming to ``schema`` (JSON Schema)."""


class FakeLLM(LLMProvider):
    """Deterministic stand-in. ``handler(user, schema_name) -> dict`` produces the answer
    (e.g. the rule-based extractor), so the whole product runs offline."""

    name = "fake"
    model = "fake-deterministic"

    def __init__(self, handler: Callable[[str, str], dict[str, Any]]) -> None:
        self.handler = handler

    def extract(self, system: str, user: str, schema: dict[str, Any], schema_name: str) -> LLMResult:
        t = time.perf_counter()
        data = self.handler(user, schema_name)
        return LLMResult(data, self.name, self.model, time.perf_counter() - t, raw=json.dumps(data, ensure_ascii=False))


class OpenAICompatibleProvider(LLMProvider):
    """Generic OpenAI-compatible chat-completions client (used for Apertus via Public AI).

    Uses ``response_format={"type": "json_schema"}`` (structured output); if the
    endpoint rejects it, falls back to a single tool call whose parameters are the
    schema (``tool_choice`` forced).
    """

    name = "openai_compatible"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout_s: float = 60.0,
        transport: httpx.BaseTransport | None = None,
        max_retries: int = 2,
        user_agent: str = USER_AGENT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_retries = max_retries
        self._http = httpx.Client(
            timeout=timeout_s,
            transport=transport,
            # Public AI rejects requests without a User-Agent ("prevent bot spamming").
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                     "User-Agent": user_agent},
        )

    def __repr__(self) -> str:  # never show the key
        return f"{type(self).__name__}(base_url={self.base_url!r}, model={self.model!r})"

    def _post(self, payload: dict[str, Any]) -> httpx.Response:
        last: httpx.Response | None = None
        for attempt in range(self.max_retries + 1):
            last = self._http.post(f"{self.base_url}/chat/completions", json=payload)
            if last.status_code not in (429, 500, 502, 503):
                return last
            time.sleep(min(2.0 * (2**attempt), 20.0))
        assert last is not None
        return last

    def extract(self, system: str, user: str, schema: dict[str, Any], schema_name: str) -> LLMResult:
        t = time.perf_counter()
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": schema_name, "schema": schema, "strict": True},
            },
        }
        resp = self._post(payload)
        if resp.status_code == 400:
            payload.pop("response_format")
            payload["tools"] = [{"type": "function", "function": {"name": schema_name, "parameters": schema}}]
            payload["tool_choice"] = {"type": "function", "function": {"name": schema_name}}
            resp = self._post(payload)
        resp.raise_for_status()
        body = resp.json()
        msg = body["choices"][0]["message"]
        raw = msg["tool_calls"][0]["function"]["arguments"] if msg.get("tool_calls") else (msg.get("content") or "{}")
        data = json.loads(_strip_fences(raw))
        return LLMResult(data, self.name, self.model, time.perf_counter() - t, raw=raw, usage=body.get("usage", {}))


def _strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        s = s.rsplit("```", 1)[0]
    return s.strip()


def apertus_provider() -> LLMProvider | None:
    """Apertus (Public AI) with the key of the environment or of the macOS keychain; None without a key."""
    key = publicai_api_key()
    if not key:
        return None
    p = OpenAICompatibleProvider(
        base_url=os.environ.get("PUBLICAI_BASE_URL", "https://api.publicai.co/v1"),
        api_key=key,
        # Documented id (platform.publicai.co/docs, read on 2026-10-05).
        model=os.environ.get("APERTUS_MODEL", DEFAULT_APERTUS_MODEL),
    )
    p.name = "apertus"
    return p


def chosen_provider() -> LLMProvider | None:
    """The one rule of the whole engine: Apertus only when ``PROXSIS_LLM_PROVIDER=apertus`` AND a key exists;
    otherwise None, and the caller uses its deterministic text model. A key alone is not a choice (review 1, I10)."""
    return apertus_provider() if os.environ.get("PROXSIS_LLM_PROVIDER", "fake") == "apertus" else None


def provider_from_env(fake_handler: Callable[[str, str], dict[str, Any]]) -> LLMProvider:
    """The chosen provider, or FakeLLM."""
    return chosen_provider() or FakeLLM(fake_handler)
