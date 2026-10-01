import random
import pandas as pd

PRODUCTS = ["Automated Registrations", "Bookable Search", "Search + Registrations"]


def customer_accounts(public_df: pd.DataFrame | None = None, n: int = 12, seed: int = 17) -> pd.DataFrame:
    rng = random.Random(seed)
    rows = []
    public_rows = []
    if public_df is not None and not public_df.empty:
        public_rows = public_df.dropna(subset=["practice_code"]).head(max(n * 8, n)).to_dict("records")
        rng.shuffle(public_rows)

    for i in range(n):
        context = public_rows[i] if i < len(public_rows) else {}
        rows.append({
            "demo_customer_id": f"DEMO-{i+1:03d}",
            "public_practice_code": context.get("practice_code", ""),
            "public_practice_name": context.get("practice_name", f"Public context unavailable {i+1}"),
            "current_product": PRODUCTS[i % len(PRODUCTS)],
            "existing_adoption_ratio": round(rng.uniform(0.42, 0.96), 2),
            "stakeholder_engaged": rng.random() > 0.25,
            "critical_support_issue": i in {8},
            "days_since_setup": [2, 5, 8, 16, 4, 11, 1, 7, 19, 6, 3, 9][i],
            "activation_complete": i not in {2, 3, 5, 8, 11},
            "usage_ratio": round(rng.uniform(0.28, 1.05), 2),
            "four_week_change_pct": round(rng.uniform(-24, 28), 1),
            "weekly_requests": rng.randint(140, 1200),
            "automated_or_routed_pct": round(rng.uniform(32, 86), 1),
            "time_to_first_value_days": rng.randint(2, 21),
            "staff_minutes_saved_weekly": rng.randint(90, 780),
            "synthetic_goal": rng.choice([
                "Reduce morning access pressure",
                "Improve request routing",
                "Increase digital access adoption",
                "Reduce reception admin",
                "Improve appointment discovery",
            ]),
        })
    return pd.DataFrame(rows)


def transcripts() -> pd.DataFrame:
    rows = [
        ("CALL-001", "Onboarding / training", "Practice manager: Reception staff are not always sure which requests should be handled through Navigator, so they fall back to the old process."),
        ("CALL-002", "Onboarding / training", "Operations lead: The first training session made sense, but new reception staff joining later do not know the routing workflow."),
        ("CALL-003", "Configuration", "Practice manager: We were unclear which appointment types had to be configured before go-live and lost two days checking it internally."),
        ("CALL-004", "Reporting / ROI", "Practice manager: I can see usage, but I need a simple way to show partners whether the change is actually saving reception time."),
        ("CALL-005", "Onboarding / training", "Reception lead: Staff understand the concept but want a one-page guide for what to do when the suggested route does not look right."),
        ("CALL-006", "Configuration", "Operations manager: We changed our appointment template and then discovered the setup no longer matched the slots we wanted to expose."),
        ("CALL-007", "Workflow / UX", "Practice manager: During the morning peak, the team needs the urgent items to stand out more clearly so they know what to pick up first."),
        ("CALL-008", "Reporting / ROI", "PCN manager: The practice wants to compare request volumes and staff time before and after rollout, not just see total activity."),
        ("CALL-009", "Onboarding / training", "Practice manager: One confident super-user is carrying the rollout. Other staff still ask them basic questions every day."),
        ("CALL-010", "Workflow / UX", "Reception lead: Some request descriptions are too broad for staff to immediately understand why a route was suggested."),
        ("CALL-011", "Configuration", "Practice manager: We need a clearer pre-launch checklist because we were still resolving access permissions on launch morning."),
        ("CALL-012", "Reporting / ROI", "Operations lead: Senior partners asked what success should look like after 30, 60 and 90 days and we had not agreed that upfront."),
        ("CALL-013", "Support", "Practice manager: When a workflow issue happens we are not always sure what information to capture before escalating it."),
        ("CALL-014", "Onboarding / training", "Reception lead: The product is being used, but confidence drops when staff encounter a case that was not covered in training."),
        ("CALL-015", "Support", "Practice manager: A standard support template with screenshots, expected behaviour and urgency would make escalation much quicker."),
        ("CALL-016", "Workflow / UX", "Operations manager: We want a clearer way to distinguish requests that need clinical review from those reception can resolve immediately."),
        ("CALL-017", "Configuration", "Practice manager: We would benefit from a short configuration review one week after launch because our real workflow changed after staff started using it."),
        ("CALL-018", "Reporting / ROI", "Practice manager: We can tell the team feels less pressured, but we need evidence we can take into the monthly practice meeting."),
    ]
    return pd.DataFrame(rows, columns=["call_id", "category", "transcript"])
