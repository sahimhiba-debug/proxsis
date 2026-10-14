import json

import httpx

from proxsis.llm.base import FakeLLM, OpenAICompatibleProvider, provider_from_env

SCHEMA = {"type": "object", "properties": {"a": {"type": "integer"}}, "required": ["a"], "additionalProperties": False}


def test_fake_llm_is_deterministic():
    f = FakeLLM(lambda user, name: {"a": len(user)})
    assert f.extract("s", "abc", SCHEMA, "x").data == {"a": 3}
    assert f.extract("s", "abc", SCHEMA, "x").data == {"a": 3}


def test_openai_compatible_structured_output_request_and_parse():
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(req.content)
        seen["auth"] = req.headers["authorization"]
        return httpx.Response(
            200, json={"choices": [{"message": {"content": '{"a": 7}'}}], "usage": {"total_tokens": 5}}
        )

    p = OpenAICompatibleProvider(
        "https://api.example/v1", "secret", "apertus-test", transport=httpx.MockTransport(handler)
    )
    r = p.extract("sys", "user", SCHEMA, "demo")
    assert r.data == {"a": 7}
    assert seen["auth"] == "Bearer secret"
    assert seen["body"]["response_format"]["type"] == "json_schema"
    assert seen["body"]["temperature"] == 0


def test_openai_compatible_falls_back_to_tool_call():
    calls = []

    def handler(req: httpx.Request) -> httpx.Response:
        body = json.loads(req.content)
        calls.append(body)
        if "response_format" in body:
            return httpx.Response(400, json={"error": "unsupported"})
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"tool_calls": [{"function": {"name": "demo", "arguments": '```json\n{"a": 2}\n```'}}]}}
                ]
            },
        )

    p = OpenAICompatibleProvider("https://api.example/v1", "k", "m", transport=httpx.MockTransport(handler))
    assert p.extract("s", "u", SCHEMA, "demo").data == {"a": 2}
    assert calls[1]["tool_choice"]["function"]["name"] == "demo"


def test_provider_from_env_defaults_to_fake(monkeypatch):
    monkeypatch.delenv("PROXSIS_LLM_PROVIDER", raising=False)
    assert provider_from_env(lambda u, n: {}).name == "fake"
    monkeypatch.setenv("PROXSIS_LLM_PROVIDER", "apertus")
    monkeypatch.delenv("PUBLICAI_API_KEY", raising=False)
    assert provider_from_env(lambda u, n: {}).name == "fake"  # pas de clé -> faux fournisseur


def test_user_agent_header_is_sent_public_ai_requires_it():
    seen = {}

    def handler(req: httpx.Request) -> httpx.Response:
        seen["ua"] = req.headers.get("user-agent", "")
        return httpx.Response(200, json={"choices": [{"message": {"content": '{"a": 1}'}}]})

    p = OpenAICompatibleProvider("https://api.example/v1", "k", "m", transport=httpx.MockTransport(handler))
    p.extract("s", "u", SCHEMA, "demo")
    assert seen["ua"].startswith("Proxsis/") and "python-httpx" not in seen["ua"]


def test_api_key_never_leaks_in_repr_or_errors():
    secret = "sk-TRES-SECRET-123"

    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"detail": "bad key"})

    p = OpenAICompatibleProvider("https://api.example/v1", secret, "m", transport=httpx.MockTransport(handler))
    assert secret not in repr(p) and secret not in str(vars(p).get("model"))
    try:
        p.extract("s", "u", SCHEMA, "demo")
    except httpx.HTTPStatusError as exc:
        assert secret not in str(exc)
    else:
        raise AssertionError("401 attendu")


def test_api_key_from_env_then_keychain(monkeypatch):
    from proxsis.llm import secrets

    monkeypatch.setenv("PUBLICAI_API_KEY", "from-env")
    assert secrets.publicai_api_key() == "from-env"
    monkeypatch.delenv("PUBLICAI_API_KEY")
    calls = []

    def fake_run(cmd, **kw):
        calls.append(cmd)

        class R:
            returncode = 0
            stdout = "from-keychain\n"

        return R()

    monkeypatch.setattr(secrets.subprocess, "run", fake_run)
    monkeypatch.setattr(secrets.sys, "platform", "darwin")
    assert secrets.publicai_api_key() == "from-keychain"
    assert calls[0][:3] == ["security", "find-generic-password", "-s"]
    assert secrets.KEYCHAIN_SERVICE in calls[0]


def test_api_key_absent_returns_none(monkeypatch):
    from proxsis.llm import secrets

    monkeypatch.delenv("PUBLICAI_API_KEY", raising=False)
    monkeypatch.setattr(secrets.sys, "platform", "linux")
    assert secrets.publicai_api_key() is None


def test_default_apertus_model_is_the_documented_one(monkeypatch):
    monkeypatch.setenv("PROXSIS_LLM_PROVIDER", "apertus")
    monkeypatch.setenv("PUBLICAI_API_KEY", "k")
    monkeypatch.delenv("APERTUS_MODEL", raising=False)
    p = provider_from_env(lambda u, n: {})
    assert p.name == "apertus" and p.model == "swiss-ai/apertus-v1.5-8b"


def test_one_rule_chooses_the_text_provider_and_a_key_alone_is_not_a_choice(monkeypatch):
    # review 1 (I10): the export used Apertus as soon as a key was present, even with PROXSIS_LLM_PROVIDER=fake
    import proxsis.llm.base as base

    monkeypatch.setattr(base, "publicai_api_key", lambda: "k-test")  # never the keychain in a test
    monkeypatch.setenv("PUBLICAI_API_KEY", "k-test")
    monkeypatch.delenv("APERTUS_MODEL", raising=False)
    for choice in (None, "fake"):
        if choice:
            monkeypatch.setenv("PROXSIS_LLM_PROVIDER", choice)
        else:
            monkeypatch.delenv("PROXSIS_LLM_PROVIDER", raising=False)
        assert base.chosen_provider() is None  # the deterministic text model
    monkeypatch.setenv("PROXSIS_LLM_PROVIDER", "apertus")
    p = base.chosen_provider()
    assert p is not None and p.name == "apertus" and p.model == base.DEFAULT_APERTUS_MODEL
