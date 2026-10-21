import io
import json

import pytest

import llm_proxy


def test_external_ai_disabled_without_both_settings(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert not llm_proxy.is_configured()
    with pytest.raises(llm_proxy.LlmUnavailable, match="deaktiviert"):
        llm_proxy.ask_synthetic("Was ist überfällig?")


def test_proxy_sends_only_question_and_built_in_synthetic_records(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self, _limit):
            return json.dumps({"output": [{"type": "message", "content": [
                {"type": "output_text", "text": "Bitte INV-1035 zuerst prüfen."}
            ]}]}).encode()

    seen = {}

    def fake_urlopen(request, timeout):
        seen["url"] = request.full_url
        seen["headers"] = dict(request.header_items())
        seen["timeout"] = timeout
        seen["payload"] = json.loads(request.data)
        return Response()

    monkeypatch.setattr(llm_proxy, "urlopen", fake_urlopen)
    assert "INV-1035" in llm_proxy.ask_synthetic("Welche Rechnung ist am längsten überfällig?")
    assert seen["url"] == "https://api.openai.com/v1/responses"
    assert seen["timeout"] == 20
    assert seen["payload"]["store"] is False
    assert "fictional demo records" in seen["payload"]["instructions"].lower()
    assert "INV-1035" in seen["payload"]["input"]
    assert "Welche Rechnung" in seen["payload"]["input"]
    assert "test-secret" not in json.dumps(seen["payload"])
    assert "Authorization" in seen["headers"]


@pytest.mark.parametrize("question", ["", "x" * 501, None])
def test_proxy_rejects_invalid_question_before_network(question, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr(llm_proxy, "urlopen", lambda *_args, **_kwargs: pytest.fail("unexpected network call"))
    with pytest.raises(ValueError):
        llm_proxy.ask_synthetic(question)
