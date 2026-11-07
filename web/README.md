# Practice / Signal — Vercel application

The Vercel web edition is the primary interface for this independent GP-practice access and simulated customer-operations exercise.

**Live:** https://practice-signal-gp.vercel.app/  
**Workbench:** https://practice-signal-gp.vercel.app/workbench

## Routes

- `/`: responsive case introduction and interactive decisions.
- `/workbench`: six simulated operations modules.
- `/api/health`: server status.
- `/api/overview`: rule-derived fictional account priorities and feedback themes.
- `/api/practices`: sourced public GP Patient Survey practice-level exploration.
- `/api/decision`: bounded educational decision explanations, no mutations.
- `/api/ticket`: deterministic draft from a fictional note, no external write or model call.

## Data boundaries

Survey measures are public observations; all customer accounts, adoption figures, savings, transcripts and decisions are simulated. An inaccessible public feed remains explicitly unavailable. No patient-level data, live NHS integration or commercial-customer outcomes are used.

The earlier Streamlit application remains in the repository root with its optional Gemini-assisted drafting. The Vercel application **does not use that provider or require an API key**.

## Local verification

```sh
python -m pip install -r requirements.txt uvicorn pytest httpx
uvicorn server:app --reload
python -m pytest -q tests
```

See the root README for architecture, provenance and the earlier Streamlit implementation.
