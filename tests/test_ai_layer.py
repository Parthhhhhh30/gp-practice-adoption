import json

import ai_layer


def test_ticket_json_parser_accepts_fenced_json():
    raw = """```json
    {"problem":"Training gap","category":"Onboarding","severity":"Medium","evidence":"Staff ask repeated questions","suggested_outcome":"Add quick guide","confidence":"High"}
    ```"""
    ticket = ai_layer._parse_ticket_json(raw)
    assert ticket["problem"] == "Training gap"
    assert ticket["severity"] == "Medium"
    assert ticket["confidence"] == "High"


def test_ticket_json_parser_rejects_invalid_severity():
    raw = json.dumps(
        {
            "problem": "x",
            "category": "y",
            "severity": "Critical",
            "evidence": "z",
            "suggested_outcome": "a",
            "confidence": "High",
        }
    )
    try:
        ai_layer._parse_ticket_json(raw)
    except ValueError as exc:
        assert "severity" in str(exc).lower()
    else:
        raise AssertionError("invalid severity should fail validation")


def test_api_key_prefers_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "environment-key")
    assert ai_layer._api_key() == "environment-key"
    assert ai_layer.available()


def test_generate_uses_header_auth_low_thinking_and_no_legacy_sampling(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "draft output"}]},
                    }
                ]
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return Response()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(ai_layer.requests, "post", fake_post)

    assert ai_layer._generate("hello") == "draft output"
    assert captured["url"].endswith("/gemini-3.8-flash:generateContent")
    assert "?key=" not in captured["url"]
    assert captured["headers"]["x-goog-api-key"] == "test-key"
    config = captured["json"]["generationConfig"]
    assert config["thinkingConfig"]["thinkingLevel"] == "low"
    assert "temperature" not in config


def test_generate_adds_structured_output_schema(monkeypatch):
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": '{"problem":"x"}'}]},
                    }
                ]
            }

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["json"] = json
        return Response()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(ai_layer.requests, "post", fake_post)
    ai_layer._generate("hello", response_schema=ai_layer.TICKET_SCHEMA)

    fmt = captured["json"]["generationConfig"]["responseFormat"]["text"]
    assert fmt["mimeType"] == "application/json"
    assert fmt["schema"]["properties"]["severity"]["enum"] == ["Low", "Medium", "High"]
