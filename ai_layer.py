from __future__ import annotations

import json
import os
import re
from typing import Any

import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "problem": {"type": "string"},
        "category": {"type": "string"},
        "severity": {"type": "string", "enum": ["Low", "Medium", "High"]},
        "evidence": {"type": "string"},
        "suggested_outcome": {"type": "string"},
        "confidence": {"type": "string", "enum": ["Low", "Medium", "High"]},
    },
    "required": [
        "problem",
        "category",
        "severity",
        "evidence",
        "suggested_outcome",
        "confidence",
    ],
    "additionalProperties": False,
}


def _api_key() -> str | None:
    """Resolve the key from a normal environment variable or Streamlit secrets."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key

    try:
        import streamlit as st

        secret = st.secrets.get("GEMINI_API_KEY")
        if secret:
            return str(secret)
    except Exception:
        # Outside a Streamlit runtime there may be no secrets file/context.
        pass

    return None


def available() -> bool:
    return bool(_api_key())


def _generate(prompt: str, response_schema: dict[str, Any] | None = None) -> str:
    key = _api_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    url = f"{BASE_URL}/{MODEL}:generateContent"
    generation_config: dict[str, Any] = {
        # These tasks are short drafting/extraction operations. Low thinking reduces
        # latency/cost without moving business decisions into the model.
        "thinkingConfig": {"thinkingLevel": "low"},
    }
    if response_schema is not None:
        generation_config["responseFormat"] = {
            "text": {
                "mimeType": "application/json",
                "schema": response_schema,
            }
        }

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": generation_config,
    }
    response = requests.post(
        url,
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        json=payload,
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidate output")

    finish_reason = candidates[0].get("finishReason")
    if finish_reason and finish_reason not in {"STOP", "MAX_TOKENS"}:
        raise RuntimeError(f"Gemini generation did not complete normally: {finish_reason}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if not text_parts:
        raise RuntimeError("Gemini returned no text output")
    return "\n".join(text_parts).strip()


def connection_check() -> tuple[bool, str]:
    """Small explicit health check for deployment QA; never called automatically."""
    if not available():
        return False, "Drafting key is not configured"
    try:
        text = _generate("Reply with exactly: CONNECTED")
        return ("CONNECTED" in text.upper()), text[:120]
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def draft_account_brief(practice: dict, tags: list[str]) -> str:
    if not available():
        return (
            f"Observed signals for {practice.get('practice_name','this practice')}: "
            + "; ".join(tags)
            + ". Possible relevance should be validated in discovery. Suggested questions: How is demand currently triaged? "
              "Where does reception spend most time? What happens during peak access periods? Which requests are hardest to route?"
        )

    prompt = f"""You are assisting a healthtech operator preparing a GP-practice discovery brief.
Use only the public practice-level facts below. Do not infer clinical need, customer status, or patient-level information.
Use cautious language such as 'possible relevance' and 'worth exploring'.
Return: Observed signals; Possible relevance; 4 discovery questions. Keep under 180 words.
Practice: {practice}
Deterministic signal tags: {tags}
"""
    return _generate(prompt)


def draft_upsell_message(account: dict, tags: list[str]) -> str:
    if not available():
        return (
            "Hi — based on our current account context, it may be useful to review whether your access workflow "
            "could benefit from a Navigator discovery session. "
            f"The demo flags: {', '.join(tags)}. I’d suggest a short call to understand the current workflow "
            "before making any recommendation."
        )

    prompt = f"""Draft a concise B2B customer-success upsell message for a GP practice.
The account/customer fields are synthetic demo data; public signal tags are real-data-derived when available.
Do not claim the practice has a problem, do not make clinical claims, and do not mention patient-level data.
Ask for a discovery conversation, not a purchase. Under 110 words. Return message body only.
Synthetic account context: {account}
Public signal tags: {tags}
"""
    return _generate(prompt)


def _parse_ticket_json(raw: str) -> dict:
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    payload = json.loads(cleaned)

    required = {
        "problem",
        "category",
        "severity",
        "evidence",
        "suggested_outcome",
        "confidence",
    }
    missing = required.difference(payload)
    if missing:
        raise ValueError("Ticket output missing fields: " + ", ".join(sorted(missing)))
    if payload["severity"] not in {"Low", "Medium", "High"}:
        raise ValueError("Ticket severity was outside the allowed set")
    if payload["confidence"] not in {"Low", "Medium", "High"}:
        raise ValueError("Ticket confidence was outside the allowed set")

    # Evidence must stay anchored in the supplied transcript. We allow a concise
    # paraphrase but reject implausibly long/generated evidence fields.
    for field in required:
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError(f"Ticket field {field} must be a non-empty string")
    if len(payload["evidence"]) > 500:
        raise ValueError("Ticket evidence was unexpectedly long")

    return payload


def extract_product_ticket(transcript: str) -> dict:
    if not available():
        return {
            "problem": transcript.split(":", 1)[-1].strip(),
            "category": "Needs review",
            "severity": "Medium",
            "evidence": transcript[:220],
            "suggested_outcome": "Review the workflow with Product/Operations and define the desired user outcome.",
            "confidence": "Low - deterministic fallback",
        }

    prompt = f"""Convert this synthetic GP-practice customer feedback into a product/operations ticket.
No patient data is present. Do not invent facts. Keep the evidence field short and anchored to the supplied transcript.
Transcript: {transcript}
"""
    return _parse_ticket_json(_generate(prompt, response_schema=TICKET_SCHEMA))
