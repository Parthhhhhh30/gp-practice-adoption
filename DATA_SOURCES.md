# Data sources and interpretation

## GP Patient Survey 2026

Practice-level GP Patient Survey results are published by Ipsos on behalf of NHS England. The app reads public practice codes, names, relevant ICS context and ease-of-contact measures for telephone, website and the NHS App.

The practice-level publication reports response options separately. The project derives an **easy** percentage from **Very easy + Fairly easy** rather than presenting an invented combined source field. Availability may vary by the source and runtime.

- https://www.gp-patient.co.uk/latest-survey/results
- https://www.gp-patient.co.uk/reporting-2026

The 2026 schema was previously verified using automated source checks. Any current record count or calculated median shown in the application must come from the feed actually retrieved, not a hardcoded number.

## Optional NHS registered-patient counts (Streamlit edition)

The earlier prototype attempts an optional join with NHS England's September 2026 practice-level registered-patient totals by practice code:

https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/september-2026

The source has sometimes rejected automated requests. Missing values remain missing; the application must not infer practice list size from unrelated measures.

## Fixed fictional operations fixtures

`synthetic.py` contains demonstration customer accounts, product readiness, adoption and feedback. These are invented for testing the system. Their account status, performance, time-to-value, commercial potential and savings are not sourced from GP Patient Survey, NHS suppliers or genuine customers.

## Interpretation limits

A public practice name, code, score or ICS label does **not** prove:
- which software supplier the practice uses;
- a customer or prospect relationship;
- the cause of an access problem;
- any patient-level health information;
- demand for any particular technology;
- real adoption, revenue, churn or impact.

The application does not use patient-level clinical data or real customer records. Its purpose is to demonstrate source-aware operational reasoning rather than diagnose practices or make external decisions.
