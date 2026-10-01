from rules import PracticeSignals, classify_practice, onboarding_state, adoption_health, upsell_readiness, recurring_issue_summary


def test_public_signal_rules_are_transparent():
    tags = classify_practice(PracticeSignals(35, 72, 70, 18000, phone_median=65, digital_median=65, list_q75=15000))
    assert "Phone access friction" in tags
    assert "Digital-ready / phone constrained" in tags
    assert "Large registered population" in tags


def test_no_signal_fallback():
    assert classify_practice(PracticeSignals(80, 80, 80, 5000)) == ["No strong public-data signal"]


def test_onboarding_stall():
    assert onboarding_state(8, False, False) == "Amber"
    assert onboarding_state(15, False, False) == "Red"
    assert onboarding_state(2, True, False) == "Green"


def test_adoption_health():
    assert adoption_health(True, .8, 2, False) == "Green"
    assert adoption_health(True, .6, 2, False) == "Amber"
    assert adoption_health(True, .3, 2, False) == "Red"


def test_upsell_readiness():
    state, reasons = upsell_readiness(.82, True, 2, False)
    assert state == "Ready for discovery"
    assert reasons
    state, _ = upsell_readiness(.82, True, 2, True)
    assert state == "Not ready"


def test_recurring_summary():
    out = recurring_issue_summary(["A","A","A","B","B"], 3)
    assert out == [("A", 3)]
