import os

from ai_layer import draft_account_brief, draft_upsell_message, extract_product_ticket


def main() -> None:
    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("GEMINI_API_KEY is required for this live verification")

    brief = draft_account_brief(
        {
            "practice_name": "Synthetic test practice",
            "phone_easy_pct": 41.0,
            "website_easy_pct": 68.0,
            "app_easy_pct": 71.0,
        },
        ["Phone access friction", "Digital-ready / phone constrained"],
    )
    assert len(brief.strip()) > 30
    print("DISCOVERY BRIEF OK")

    outreach = draft_upsell_message(
        {"demo_customer_id": "DEMO-TEST", "existing_adoption_ratio": .82, "synthetic_goal": "Reduce access friction"},
        ["Phone access friction"],
    )
    assert len(outreach.strip()) > 30
    print("OUTREACH DRAFT OK")

    ticket = extract_product_ticket(
        "Practice manager: New reception staff are unclear on the routing workflow and keep asking the super-user for help."
    )
    required = {"problem", "category", "severity", "evidence", "suggested_outcome", "confidence"}
    assert required.issubset(ticket)
    print("FEEDBACK → TICKET OK")


if __name__ == "__main__":
    main()
