# Architecture and control design

## Problem framing

The portfolio project is designed to prove four behaviours relevant to a startup operator/customer-growth role:

1. use public evidence without pretending it reveals customer need;
2. build repeatable onboarding/adoption operations;
3. use AI for language and synthesis rather than hidden business logic;
4. turn customer evidence into product and playbook improvements.

## System flow

```text
2026 GP Patient Survey
        ↓
practice-level public context
        ↓
transparent signal rules
        ↓
synthetic customer portfolio
        ↓
upsell readiness + onboarding health
        ↓
operator work queue / account workspace
        ↓
activation + adoption + 90-day value evidence
        ↓
synthetic customer feedback
        ↓
draft product / operations issue
        ↓
recurring-theme counts
        ↓
operator-reviewed playbook change
```

## Application structure

- `app.py` — minimal Streamlit entry point.
- `workspace.py` — customer-operations interface and page orchestration.
- `data_pipeline.py` — public-data fetching, schema parsing and safe enrichment.
- `rules.py` — deterministic signal, readiness, onboarding and adoption rules.
- `synthetic.py` — clearly labelled demo customer, usage/value and feedback data.
- `ai_layer.py` — optional Gemini drafting/extraction layer.
- `tests/` — rule, schema, drafting-contract, queue and end-to-end regression tests.
- `scripts/verify_live_sources.py` — live public-source contract check.
- `scripts/verify_streamlit_session.py` — full Streamlit session smoke check.

## Control boundary

### Deterministic
- public-data signal tags
- upsell readiness state
- onboarding health
- adoption health
- work-queue priority
- KPI calculations
- recurring-issue counts

### AI-assisted
- practice discovery brief
- personalised outreach draft
- transcript-to-ticket draft

### Human-owned
- whether an account should be prioritised
- external communication
- commercial decision / upsell
- final product-ticket scope and priority
- playbook changes
- any clinical, regulatory or patient-safety judgement

## Failure / degradation design

- If the verified GP Patient Survey feed fails, the public-practice explorer reports that the source is unavailable; synthetic customer-operations modules remain usable.
- If the NHS registered-patient enrichment is blocked, list size remains blank and no population-size signal is inferred.
- If no Gemini key is configured, deterministic/local drafting fallbacks keep the workflow demonstrable.
- No customer action, CRM write, outreach send or product-backlog write is automated by the prototype.

## Privacy and evidence boundary

No patient-level health or clinical data is used. Synthetic transcripts contain only practice-operations feedback. Public data is practice-level official survey context. Real practice names/codes do not imply a Healthtech-1 customer or prospect relationship.
