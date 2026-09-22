"""LLM providers used by the agent.

Only the Python standard library is used, so the agent adds no dependencies.

Providers
---------
anthropic  Anthropic Messages API (needs ANTHROPIC_API_KEY).
openai     Any OpenAI-compatible Chat Completions API (needs OPENAI_API_KEY).
           OPENAI_BASE_URL lets you point it at other compatible servers,
           for example a local Ollama server: http://localhost:11434/v1
replay     Replays responses saved by an earlier run (no network, no cost).
           Useful for reproducible demos and for testing the agent itself.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LLMResponse:
    text: str
    input_tokens: int = 0
    output_tokens: int = 0


class LLMError(RuntimeError):
    pass


def _post_json(url: str, payload: dict, headers: dict, timeout: int = 180) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    for key, value in headers.items():
        request.add_header(key, value)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:1000]
        raise LLMError(f"HTTP {exc.code} from {url}: {body}") from exc
    except urllib.error.URLError as exc:
        raise LLMError(f"Cannot reach {url}: {exc.reason}") from exc


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, model: str | None):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise LLMError("Set the ANTHROPIC_API_KEY environment variable.")
        self.model = model or "claude-sonnet-5"

    def complete(self, system: str, messages: list[dict]) -> LLMResponse:
        result = _post_json(
            "https://api.anthropic.com/v1/messages",
            {"model": self.model, "max_tokens": 8000, "system": system, "messages": messages},
            {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"},
        )
        text = "".join(block.get("text", "") for block in result.get("content", []))
        usage = result.get("usage", {})
        return LLMResponse(text, usage.get("input_tokens", 0), usage.get("output_tokens", 0))


class OpenAICompatibleProvider:
    name = "openai"

    def __init__(self, model: str | None):
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key and "localhost" not in self.base_url and "127.0.0.1" not in self.base_url:
            raise LLMError("Set OPENAI_API_KEY (or OPENAI_BASE_URL for a local server).")
        if not model:
            raise LLMError("Pass --model for the openai provider (for example --model qwen2.5-coder).")
        self.model = model

    def complete(self, system: str, messages: list[dict]) -> LLMResponse:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        result = _post_json(
            f"{self.base_url}/chat/completions",
            {"model": self.model, "messages": [{"role": "system", "content": system}, *messages]},
            headers,
        )
        text = result["choices"][0]["message"]["content"] or ""
        usage = result.get("usage", {})
        return LLMResponse(text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))


class ReplayProvider:
    """Returns previously recorded responses (NN.txt files) in order."""

    name = "replay"

    def __init__(self, replay_dir: str | None):
        if not replay_dir:
            raise LLMError("Pass --replay-dir pointing at a folder with recorded responses.")
        self.files = sorted(Path(replay_dir).glob("*.txt"))
        if not self.files:
            raise LLMError(f"No recorded *.txt responses in {replay_dir}.")
        self.model = f"replay:{replay_dir}"
        self.index = 0

    def complete(self, system: str, messages: list[dict]) -> LLMResponse:
        if self.index >= len(self.files):
            raise LLMError("Replay responses exhausted.")
        text = self.files[self.index].read_text(encoding="utf-8")
        self.index += 1
        return LLMResponse(text)


def make_provider(name: str, model: str | None, replay_dir: str | None = None):
    if name == "anthropic":
        return AnthropicProvider(model)
    if name == "openai":
        return OpenAICompatibleProvider(model)
    if name == "replay":
        return ReplayProvider(replay_dir)
    raise LLMError(f"Unknown provider: {name}")
