# GP Practice Adoption & Growth OS

Independent portfolio prototype inspired by Healthtech-1's Special Projects Associate role.

The project demonstrates a joined-up operating system for the customer journey:

**public NHS practice context → transparent access signals → synthetic upsell/onboarding workflow → adoption & ROI tracking → customer feedback → draft product tickets → playbook improvements**

## Live operating principle

The interface is intentionally designed as a healthtech operations console rather than an "AI dashboard". Automation is embedded inside the workflow: deterministic rules own states and KPIs, drafting assistance prepares reviewable content, and people retain control over external communication, prioritisation and product decisions.

## Evidence boundary

- Public practice context: real practice-level NHS / GP Patient Survey data when the live refresh succeeds.
- Customer relationship, onboarding, product usage, ROI and call transcripts: synthetic demo data because Healthtech-1 internal data is not public.
- Real practice names/codes, if overlaid on a synthetic demo account, do **not** imply that the practice is a Healthtech-1 customer or prospect.
- No patient-level or clinical data is used.
- Drafting assistance supports wording and structure only; deterministic rules own states, KPI calculations and risk flags; humans approve external or product actions.

## Why this architecture

The role is centred on onboarding, adoption, upsell, product rollout, operational process-building, AI-enabled follow-up, customer insight and usage/churn tracking. The project therefore prioritises those workflows rather than treating the role as a generic outbound-sales job.

## Public data

The live data layer is designed around:

- 2026 GP Patient Survey practice-level data: phone, website and NHS App ease-of-contact measures.
- NHS registered-patient practice totals for list-size context.

The data creates **signal tags**, not an opaque practice score. Tags are starting points for discovery, not claims that a practice needs a product.

## App modules

1. Overview - operating flow and portfolio snapshot.
2. Practice signals - public NHS context and deterministic tags.
3. Growth pipeline - synthetic existing-customer portfolio, transparent upsell readiness and onboarding risk.
4. Adoption & value - synthetic usage, activation, time-to-value and 90-day value evidence.
5. Customer insights - synthetic transcripts converted into draft product/operations issues.
6. Operating playbook - versioned onboarding/adoption workflow and evidence-based suggested improvements.

## Drafting assistance

Optional Gemini integration is used for:

- discovery briefs
- human-review outreach drafts
- feedback-to-ticket drafting

Without an API key, the app uses a deterministic fallback so the core workflow remains testable. No automated send or backlog write occurs.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optional live drafting assistance:

```bash
export GEMINI_API_KEY="..."
```

## Test

```bash
pytest -q
python -m py_compile app.py rules.py data_pipeline.py synthetic.py ai_layer.py
```
