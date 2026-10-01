# Data sources

Research checked 2 October 2026.

## GP Patient Survey 2026 — verified live core feed

Practice-level GP Patient Survey results are published by Ipsos on behalf of NHS England. The project uses practice code/name, ICS name, and the 2026 ease-of-contact measures for phone, website and NHS App.

The live CSV schema was verified in GitHub Actions against the current 2026 publication: **6,166 practices loaded successfully**. In the published practice CSV, the relevant variables are stored as separate response options (for example `localgpservicesphone_2.pct` and `_3.pct`); the project calculates the published-style **Easy** measure as **Very easy + Fairly easy** rather than relying on an invented combined field.

Sources:
- https://www.gp-patient.co.uk/latest-survey/results
- https://www.gp-patient.co.uk/reporting-2026

## Patients Registered at a GP Practice — optional enrichment

NHS England publishes practice-level registered-patient totals. The project attempts to join the September 2026 totals to the GPPS practice data by practice code.

Source:
- https://digital.nhs.uk/data-and-information/publications/statistical/patients-registered-at-a-gp-practice/september-2026

**Cloud-access limitation:** the NHS England publication page currently returns HTTP 403 to GitHub-hosted automated requests. The application therefore treats registered list size as an optional enrichment: if the source cannot be fetched, list size remains blank and no large-population signal is inferred. The verified GPPS access measures continue to load and the customer-operations workflow remains usable.

## Healthtech-1 public product context

Bookable Search is publicly described as supporting new-patient discovery/booking, while Bookable Navigator is positioned around helping existing patients reach an appropriate service or appointment. Product references in this independent prototype are contextual only; no private Healthtech-1 data or integration is used.

Source:
- https://www.healthtech1.uk/bookable

## Data boundary

Public datasets do **not** reveal Healthtech-1's actual customer list, account status, product usage, pricing, churn, ROI, onboarding history or internal feedback. Those layers are synthetic in this portfolio project. A real GP practice name shown beside a demo account is only a public-context overlay and does not imply that the practice is a Healthtech-1 customer, prospect or user.

No patient-level or clinical data is used anywhere in the project.
