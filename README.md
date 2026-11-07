# Practice / Signal — GP Practice Adoption & Operations

**Live:** https://gp-practice-adoption.streamlit.app/  
**Project:** An independent interactive exploration of GP access signals and simulated customer-operations decisions.

The first screen is a guided case, not a generic analytics dashboard: choose an evidence problem, make an operational decision, inspect the explanation, and open the corresponding working module. The palette and visual approach are original to this project; the live Streamlit operations tool remains available behind the narrative.

## Start with the difference between a fact and an assumption

- **Public evidence:** The 2026 GP Patient Survey provides practice-level measures for phone, website and NHS App access. Where available, the app displays sourced practice-level context. Survey results do **not** identify a software supplier, a genuine customer or commercial intent.
- **Simulated account operations:** Twelve seeded fictional customer profiles demonstrate readiness, activation risks, adoption, customer feedback and follow-up. Practice names used as public context are **not** evidence of a supplier/customer relationship.
- **Real application behaviour:** Deterministic rules identify cases requiring attention. Interactive next-action examples show why operators should verify evidence rather than make unsupported claims. These choices are educational and **do not modify** customer records.
- **Optional AI drafting:** Server-side Gemini integration can generate draft discovery briefs, reviewable outreach and product-issue tickets. Humans approve external communications, commercial decisions and backlog changes. No automatic send, CRM write or clinical action is performed.

## Recruiter / reviewer journey

1. Open **Start here**. Read the evidence distinction and observed survey-data summary.
2. Change the scenario between **Public access**, **Rollout risk** and **Customer feedback**. Choose a next action and inspect the rationale.
3. Open **Practices** for survey evidence and filtering. No fabricated source counts appear if the feed is unavailable.
4. Open **Accounts**, **Adoption** and **Feedback** to inspect simulated operations, real rule logic and human-owned follow-up.
5. Open **Playbook** to see how recurring fictional customer friction informs a repeatable improvement process.

## Underlying workspaces

| Workspace | What is implemented |
| --- | --- |
| Today | Rule-driven prioritisation of synthetic account issues and opportunities |
| Practices | Real public GP Patient Survey data and transparent access-signal labels |
| Accounts | Synthetic customer status, activation and product-readiness logic |
| Adoption | Fictional usage, time-to-value and value-review observations |
| Feedback | Fictional notes, recurring-theme aggregation and reviewable AI-assisted ticket drafts |
| Playbook | Onboarding and support-process improvement suggestions |

## Design and architecture

- Streamlit 1.64, Python, Pandas and custom responsive HTML/CSS for the opening case narrative.
- Pure scenario-decision explanations tested in `tests/test_story.py`; existing workflow rules remain in `rules.py`.
- The 2026 GPPS summary constructs “easy access” from the published **Very easy + Fairly easy** percentages. Data-source descriptions and limitations appear in [DATA_SOURCES.md](DATA_SOURCES.md).
- Fixed synthetic fixtures in `synthetic.py`. No patient-level or clinical records enter the app.
- Gemini credential resolution uses a server-side environment variable or Streamlit secrets; keys must **not** be placed in GitHub or browser code. There is no expectation of paid services to browse the demonstration.

## Limitations

This is not a real implementation of SystmOne, a clinical data-migration tool, an NHS client delivery, or an audited service-quality intervention. The survey data is public and descriptive; the customer relationships and commercial outcomes are entirely fictional. Predicted savings, adoption measurements, onboarding phases and feedback transcripts are examples, not outcomes achieved with real practices.

An available free-tier API key does not guarantee unlimited no-cost inference. Review Google's project-level quotas and terms before enabling model-backed drafting.

## Run and verify

```bash
pip install -r requirements.txt
streamlit run app.py

pytest -q
python -m py_compile app.py workspace.py story.py rules.py synthetic.py data_pipeline.py ai_layer.py
```

The repository includes GitHub Actions tests and a headless Streamlit health check. Tests using simulated model responses do not prove a live provider call; public-data availability is a separate check.

## Development note

Developed with AI-assisted programming and iterative testing. The code demonstrates an independent technical exercise, not unaided coding proficiency or real client implementation experience.
