import pandas as pd

from rules import PracticeSignals, adoption_health, classify_practice, onboarding_state, recurring_issue_summary, upsell_readiness
from synthetic import customer_accounts, transcripts


def test_demo_operating_flow_from_public_signal_to_customer_action():
    public = pd.DataFrame(
        [
            {
                "practice_code": "A100",
                "practice_name": "Demo Practice",
                "ics_name": "Demo ICS",
                "phone_easy_pct": 35.0,
                "website_easy_pct": 72.0,
                "app_easy_pct": 70.0,
                "list_size": 18000,
            }
        ]
    )
    tags = classify_practice(PracticeSignals(35, 72, 70, 18000, 65, 65, 15000))
    assert "Phone access friction" in tags
    assert "Digital-ready / phone constrained" in tags

    state, reasons = upsell_readiness(.82, True, len(tags), False)
    assert state == "Ready for discovery"
    assert reasons

    assert onboarding_state(8, False, False) == "Amber"
    assert adoption_health(True, .82, 4.0, False) == "Green"


def test_synthetic_customer_layer_is_labelled_and_has_no_patient_fields():
    accounts = customer_accounts(None)
    assert accounts.demo_customer_id.str.startswith("DEMO-").all()
    prohibited = {"patient_name", "nhs_number", "date_of_birth", "diagnosis", "clinical_note"}
    assert prohibited.isdisjoint(set(accounts.columns))


def test_feedback_layer_surfaces_recurring_themes_without_model_scoring():
    calls = transcripts()
    themes = dict(recurring_issue_summary(calls.category, min_count=3))
    assert themes["Onboarding / training"] >= 3
    assert themes["Configuration"] >= 3
    assert themes["Reporting / ROI"] >= 3
