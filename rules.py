from dataclasses import dataclass
from typing import Iterable


def pct(value):
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v < 0:
        return None
    return v * 100 if 0 <= v <= 1 else v


@dataclass(frozen=True)
class PracticeSignals:
    phone_easy: float | None
    website_easy: float | None
    app_easy: float | None
    list_size: int | None
    phone_median: float | None = None
    digital_median: float | None = None
    list_q75: float | None = None


def classify_practice(s: PracticeSignals) -> list[str]:
    """Transparent public-data signal tags. Not a customer-fit or sales score."""
    tags: list[str] = []
    phone = pct(s.phone_easy)
    web = pct(s.website_easy)
    app = pct(s.app_easy)

    if phone is not None:
        threshold = min(50.0, s.phone_median - 10) if s.phone_median is not None else 50.0
        if phone < threshold:
            tags.append("Phone access friction")

    digital_values = [x for x in (web, app) if x is not None]
    if digital_values:
        avg = sum(digital_values) / len(digital_values)
        threshold = (s.digital_median - 10) if s.digital_median is not None else 50.0
        if avg < threshold:
            tags.append("Digital access friction")
        if phone is not None and phone < 50 and avg >= 60:
            tags.append("Digital-ready / phone constrained")

    if s.list_size is not None:
        large_threshold = s.list_q75 if s.list_q75 is not None else 12000
        if s.list_size >= large_threshold:
            tags.append("Large registered population")

    return tags or ["No strong public-data signal"]


def onboarding_state(days_since_setup: int, activation_complete: bool, critical_blocker: bool) -> str:
    if critical_blocker:
        return "Red"
    if activation_complete:
        return "Green"
    if days_since_setup >= 14:
        return "Red"
    if days_since_setup >= 7:
        return "Amber"
    return "Green"


def adoption_health(
    activation_complete: bool,
    usage_ratio: float,
    four_week_change_pct: float,
    critical_blocker: bool,
) -> str:
    if critical_blocker or (activation_complete and usage_ratio < 0.40):
        return "Red"
    if not activation_complete or usage_ratio < 0.70 or four_week_change_pct <= -10:
        return "Amber"
    return "Green"


def upsell_readiness(
    existing_adoption_ratio: float,
    stakeholder_engaged: bool,
    public_signal_count: int,
    critical_support_issue: bool,
) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if critical_support_issue:
        return "Not ready", ["Resolve critical support issue first"]
    if existing_adoption_ratio >= 0.70:
        reasons.append("Existing product adoption is healthy")
    else:
        reasons.append("Existing adoption needs strengthening")
    if stakeholder_engaged:
        reasons.append("Operational stakeholder engaged")
    else:
        reasons.append("Operational stakeholder not yet engaged")
    if public_signal_count >= 2:
        reasons.append("Multiple public access-friction signals observed")
    elif public_signal_count == 1:
        reasons.append("One public access-friction signal observed")
    else:
        reasons.append("No strong public access-friction signal")

    if existing_adoption_ratio >= 0.70 and stakeholder_engaged and public_signal_count >= 1:
        return "Ready for discovery", reasons
    if existing_adoption_ratio >= 0.50 and (stakeholder_engaged or public_signal_count >= 1):
        return "Develop", reasons
    return "Not ready", reasons


def recurring_issue_summary(categories: Iterable[str], min_count: int = 3) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for category in categories:
        counts[category] = counts.get(category, 0) + 1
    return sorted([(k, v) for k, v in counts.items() if v >= min_count], key=lambda x: (-x[1], x[0]))
