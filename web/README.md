# Practice / Signal — Vercel edition

A standalone recruiter-facing experience using the original GP Practice Adoption
domain logic. The existing Streamlit app is preserved; this project is the new
primary presentation and operations workbench.

### Source boundaries
- Public: practice-level results fetched on demand from 2026 GP Patient Survey;
  unavailable data is shown as unavailable, never replaced with fictional figures.
- Synthetic: twelve customer accounts, usage, adoption, feedback, time saved,
  expansion, tickets and all outcomes.
- No patient/clinical records, NHS integrations, external outreach or automated
  commercial actions.

### Routes
- `/`: guided story with real interactive decision API.
- `/workbench`: six operational modules.
- `/api/overview`: rule-derived synthetic accounts and feedback.
- `/api/practices`: public GPPS query with source and missing-data handling.
- `/api/ticket`: deterministic simulated ticket draft; **not** a real AI call.

### Operating limits
No API key or paid plan is required. The original Streamlit repository retains
its optional Gemini integration; it is **not** silently enabled on Vercel.
There is no persistent authenticated customer database; case studies use
fixed, deterministic synthetic data. Decisions are explanatory, not mutations.

### Run locally
```sh
pip install -r requirements.txt
pip install uvicorn pytest httpx
uvicorn server:app --reload
pytest -q tests/
```

### Visual language
An original case-study identity with ink violet, lavender/cobalt, mint and
warm melon. Interaction quality is benchmarked against LaunchLab, not its
colours, copy, hierarchy or illustrated layout.
