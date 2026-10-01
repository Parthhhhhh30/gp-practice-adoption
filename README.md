# GP Practice Adoption & Growth OS

Independent portfolio prototype inspired by Healthtech-1's Special Projects Associate role.

**Live app:** https://gp-practice-adoption.streamlit.app/

The project demonstrates a joined-up operating system for the customer journey:

**public NHS practice context → transparent access signals → synthetic upsell/onboarding workflow → adoption & value tracking → customer feedback → draft product tickets → playbook improvements**

## Product principle

This is designed as a **customer-operations workspace**, not an "AI dashboard". The interface starts with work that needs attention: account risk, activation, value review, expansion readiness and recurring customer friction.

Automation is intentionally split by responsibility:

- **Deterministic rules:** lifecycle states, readiness, risk, thresholds and KPI calculations.
- **Drafting assistance:** discovery briefs, reviewable customer outreach and feedback-to-ticket drafts.
- **Human decisions:** external communication, account prioritisation, upsell decisions and product/backlog actions.

## Evidence boundary

- **Real public context:** 2026 GP Patient Survey practice-level access measures. The current live CSV schema has been verified in GitHub Actions against **6,166 practices**.
- **Optional public enrichment:** NHS registered-patient totals. The NHS publication page currently blocks some cloud automation with HTTP 403, so list size safely remains blank when unavailable rather than being fabricated.
- **Synthetic:** customer relationship, onboarding state, product usage, value measures, ROI-style evidence and customer-call transcripts.
- A real practice name/code overlaid on a demo account does **not** imply that the practice is a Healthtech-1 customer or prospect.
- **No patient-level or clinical data** is used.

## Why this architecture

The target role centres on onboarding, adoption, upsell, product rollout, operational process-building, AI-assisted follow-up, customer insight and usage/churn tracking. The prototype therefore models those workflows rather than treating the job as a generic outbound-sales role.

## Workspace

- **Today** — operator work queue driven by lifecycle/adoption rules.
- **Practices** — real public practice context and transparent access-signal tags.
- **Accounts** — simulated customer workspace, expansion readiness and onboarding state.
- **Adoption** — synthetic activation, usage trajectory, time-to-value and 90-day value evidence.
- **Feedback** — synthetic customer notes converted into reviewable draft product/operations issues.
- **Playbook** — repeatable onboarding/adoption journey with suggested changes from recurring feedback themes.

## Public-data logic

The project does not create a black-box practice score. The 2026 GP Patient Survey publishes response options separately; the app calculates the **Easy** measure for phone, website and NHS App access as the published positive responses **Very easy + Fairly easy**. Practice tags are explicit rules relative to the observed distribution and are discovery signals only.

See `DATA_SOURCES.md` for the source and limitation log.

## Drafting assistance

Optional Gemini 3.8 Flash integration supports:

- discovery briefs
- human-review outreach drafts
- feedback-to-ticket drafting

The app remains usable without an API key through deterministic/local fallbacks. No automatic send, CRM write or backlog creation occurs.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

Optional live drafting assistance:

```bash
export GEMINI_API_KEY="..."
```

## Quality checks

```bash
pytest -q
python -m py_compile app.py rules.py data_pipeline.py synthetic.py ai_layer.py scripts/verify_live_sources.py
python scripts/verify_live_sources.py
```

GitHub Actions also starts Streamlit headlessly and checks `/_stcore/health`. Live-source verification is separate from core CI so a third-party public-data outage cannot falsely make the application code appear broken.
