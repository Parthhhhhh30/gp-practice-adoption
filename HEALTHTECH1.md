# Healthtech-1 role alignment

This is an independent portfolio project built after studying the public Special Projects Associate role. It is not a Healthtech-1 product or integration.

## What the project demonstrates

The role spans onboarding, adoption, upsell, product rollout, process building, AI-assisted follow-up, customer feedback and usage/churn tracking. This prototype turns that operating problem into one joined-up workspace:

**practice context → customer growth → onboarding → adoption/value → feedback → product issue → playbook improvement**

## 90-second demo path

1. **Today** — start with the operator work queue. Red onboarding/adoption states take priority over expansion.
2. **Practices** — open a real GP practice from the 2026 GP Patient Survey. Show transparent phone/website/NHS App access signals; no opaque lead score.
3. **Accounts** — open a synthetic customer account. Explain why expansion readiness is deterministic and why an active support issue blocks upsell.
4. **Adoption** — show synthetic activation, usage trend, time-to-value and 90-day value evidence. Explain that these are demonstration measures, not Healthtech-1 claims.
5. **Feedback** — open a synthetic customer-call note and create a reviewable draft product/operations issue while preserving the evidence.
6. **Playbook** — show how recurring feedback themes produce suggested process changes, still requiring operator approval.

## Safe claims

- Working Streamlit customer-operations workspace.
- Live 2026 GP Patient Survey practice-level integration; current schema verified against 6,166 practices.
- Deterministic practice signals, upsell readiness, onboarding health, adoption health and queue priority.
- Synthetic customer/adoption/value layer with explicit labelling.
- Optional Gemini 3.8 Flash drafting/extraction layer with human review boundaries.
- Automated regression tests, Python compile checks, Streamlit runtime smoke test, live-source check and full Streamlit-session check.

## Claims not to make

Do not say that the project:

- uses Healthtech-1 internal data;
- identifies actual Healthtech-1 prospects or customers;
- measures real Bookable Navigator ROI, churn or adoption;
- contains patient-level data;
- makes clinical or regulatory decisions;
- proves that a named practice needs Healthtech-1;
- automatically sends outreach or writes product priorities.

## Production additions

A real deployment would replace the synthetic layer with authorised customer/product data, CRM history, onboarding milestones, actual usage events, support cases and agreed value baselines. It would also require proper authentication, role-based access, audit controls and the organisation's data-governance/security review before handling any sensitive operational information.
