from __future__ import annotations
import json
import os
import re

import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


def _generate(prompt: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"thinkingConfig": {"thinkingLevel": "low"}},
    }
    response = requests.post(url, json=payload, timeout=45)
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates") or []
    if not candidates:
        raise RuntimeError("Gemini returned no candidate output")
    parts = candidates[0].get("content", {}).get("parts", [])
    text_parts = [part.get("text", "") for part in parts if part.get("text")]
    if not text_parts:
        raise RuntimeError("Gemini returned no text output")
    return "\n".join(text_parts).strip()


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
    required = {"problem", "category", "severity", "evidence", "suggested_outcome", "confidence"}
    missing = required.difference(payload)
    if missing:
        raise ValueError("Ticket output missing fields: " + ", ".join(sorted(missing)))
    if payload["severity"] not in {"Low", "Medium", "High"}:
        raise ValueError("Ticket severity was outside the allowed set")
    if payload["confidence"] not in {"Low", "Medium", "High"}:
        raise ValueError("Ticket confidence was outside the allowed set")
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
No patient data is present. Do not invent facts.
Return STRICT JSON with keys: problem, category, severity, evidence, suggested_outcome, confidence.
Severity must be Low, Medium, or High. Confidence must be Low, Medium, or High.
Transcript: {transcript}
"""
    return _parse_ticket_json(_generate(prompt))
