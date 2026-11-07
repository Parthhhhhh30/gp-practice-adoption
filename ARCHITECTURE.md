# System architecture and decision boundaries

## Two applications, one project

The repository includes two separate interfaces sharing the same underlying Python rules and fictional GP operations model.

**Primary Vercel edition — `web/`**

```text
Browser (HTML/CSS/JavaScript)
   ↓
FastAPI (/api/health, /api/overview, /api/decision,
         /api/practices, /api/ticket)
   ├── 2026 GP Patient Survey public data (on-demand; may be unavailable)
   └── deterministic onboarding / adoption / readiness rules
           └── fixed synthetic account and feedback fixtures
```

The site is responsive and offers a guided case, three explanatory decisions, and a six-part workbench. Rules run on the server and decisions return a rationale. No account mutation or external communication is performed. Ticket drafting is a deterministic template, not AI generation.

**Earlier Streamlit edition — repository root**

`app.py` loads `workspace.py`, `story.py`, `data_pipeline.py`, `rules.py` and `synthetic.py`. It also supports optional Gemini-assisted drafting in `ai_layer.py` when a key is configured securely in the runtime. That integration has not been migrated to Vercel.

## What is observed versus simulated

- **Public observations:** practice-level GP Patient Survey access measures, practice codes/names and ICS context where available.
- **Simulated:** account relationships, onboarding progress, activation, product use, support issues, adoption, feedback, time savings, commercial opportunity and all outcomes.
- **Human-owned:** contact with a real practice, any product priority, customer action, commercial decision or clinical judgement.

These categories must not be conflated. A low reported access score is a reason to investigate, not evidence of a software fault or an established customer need.

## Graceful degradation

- If the official survey feed cannot be reached, public information is marked unavailable. No synthetic substitute is silently inserted.
- Fictional account and rule demonstrations remain accessible without a live survey feed.
- The primary Vercel application requires no AI provider or API key.
- The Streamlit edition's optional AI-drafting flow has a local fallback; drafts do not constitute completed actions.
- All API inputs use bounded models or parameters; public cases are educational and cannot change real records.

## Operational limitations

This is not an authenticated multi-user customer system and does not persist real customer state. It does not connect to NHS clinical software, store patient-level information, prove commercial ROI, or provide a compliance or fairness assessment. Real deployments would require authorised customer data, user identity and access controls, audit records, security reviews, clinical governance where applicable, and carefully defined success criteria.

## Verification

`web/tests/test_api.py` checks the API contract using fictional fixtures. Root-level tests cover deterministic rules, data parsing and the earlier Streamlit app. See GitHub Actions for the actual results; source-availability tests and provider-backed generation should not be confused with mocked or deterministic tests.
