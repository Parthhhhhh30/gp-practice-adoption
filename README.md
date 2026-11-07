# Practice / Signal

**Live application:** https://practice-signal-gp.vercel.app/  
**Operations workbench:** https://practice-signal-gp.vercel.app/workbench  
**Previous Streamlit prototype:** https://gp-practice-adoption.streamlit.app/

Practice / Signal is an independent GP-practice access and customer-operations exercise. It uses 2026 GP Patient Survey practice-level results to explore reported access, then uses deliberately fictional customer records to demonstrate onboarding, support, adoption, and evidence-led follow-up.

The live site is built for Vercel with a custom HTML/CSS/JavaScript interface and a Python FastAPI service. The earlier Streamlit implementation is retained as a separate, functional prototype.

## Explore the live case

1. **Start with the question.** The homepage explains why a survey signal, a customer problem and a technical solution are not interchangeable.
2. **Make a decision.** Select a public-access, rollout or feedback case. The live rules endpoint explains the decision without modifying customer records.
3. **Inspect the source.** Explore reported practice-level GP Patient Survey access data. An unavailable feed is shown as unavailable, not replaced by invented figures.
4. **Investigate operations.** Use the workbench to explore fictional account-readiness, adoption, support and product-feedback cases.
5. **Follow the evidence.** View the reasons behind a rule result and a proposed next step before claiming progress.

## What is implemented

- **Vercel web app:** responsive, custom frontend; FastAPI endpoints for source data, account statuses, decisions and deterministic ticket drafts.
- **Public evidence:** published practice-level GP Patient Survey access results and documented signal calculations.
- **Simulated operations:** twelve fictional account profiles, support issues, usage figures, feedback notes, priority queues and illustrative time-to-value metrics.
- **Rule-based decisions:** onboarding status, adoption health, expansion readiness, priority ordering and decision explanations computed in Python.
- **Earlier Streamlit prototype:** a separate interactive Python workspace with an optional server-side Gemini drafting feature. This feature is **not connected to the Vercel edition**.
- **Tests:** code checks for the Streamlit prototype and a dedicated FastAPI/API test workflow for the Vercel version.

## Boundaries

The public survey does not establish an individual practice's software supplier, commercial intent, customer relationship or need for a particular product. All customer accounts and business outcomes are simulated; no patient-level or clinical records are used.

Neither version is a SystmOne integration, NHS clinical deployment, validated patient migration, production CRM or proven healthcare intervention. The Vercel draft-ticket feature is deterministic and **does not make a Gemini call**. Neither edition automatically sends communications, changes customer systems or makes clinical decisions.

This project was developed with AI-assisted programming and iterative testing. The code is an independent technical exercise, not evidence of unaided software development or completed client implementation work.

## Repository structure

- `web/`: Vercel edition, FastAPI server, static site and API tests.
- `app.py`, `workspace.py`, `story.py`: previous Streamlit interface.
- `rules.py`, `synthetic.py`, `data_pipeline.py`: Python rules, fictional fixtures and GPPS source integration.
- `ai_layer.py`: optional Streamlit Gemini-assisted drafting, requiring server-side credentials.
- `tests/` and `web/tests/`: automated checks.
- `ARCHITECTURE.md` and `DATA_SOURCES.md`: technical design and evidence definitions.

## Run locally

**Vercel edition (from `web/`):**
```sh
cd web
python -m pip install -r requirements.txt uvicorn pytest httpx
uvicorn server:app --reload
# In another terminal:
python -m pytest -q tests
```

**Streamlit prototype (from repository root):**
```sh
python -m pip install -r requirements.txt
streamlit run app.py
python -m pytest -q tests
```

No API key is required to use the Vercel edition. Do not commit private API keys or database credentials. An actual free-tier provider quota is governed by the owner's provider account and settings.
