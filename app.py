from __future__ import annotations

import pandas as pd
import streamlit as st

from ai_layer import available as drafting_available, draft_account_brief, draft_upsell_message, extract_product_ticket
from data_pipeline import load_public_context
from rules import (
    PracticeSignals,
    adoption_health,
    classify_practice,
    onboarding_state,
    recurring_issue_summary,
    upsell_readiness,
)
from synthetic import customer_accounts, transcripts


st.set_page_config(
    page_title="Practice Growth & Adoption",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1240px; padding-top: 2rem; padding-bottom: 4rem;}
      [data-testid="stSidebar"] {border-right: 1px solid rgba(49, 51, 63, 0.12);}
      [data-testid="stMetric"] {
        border: 1px solid rgba(49, 51, 63, 0.10);
        border-radius: 10px;
        padding: 14px 16px;
        background: rgba(255, 255, 255, 0.55);
      }
      [data-testid="stMetricLabel"] {font-size: 0.78rem; letter-spacing: 0.02em;}
      div.stButton > button {border-radius: 8px; font-weight: 600;}
      .eyebrow {font-size: 0.75rem; letter-spacing: .10em; text-transform: uppercase; opacity: .62; margin-bottom: .35rem;}
      .page-title {font-size: 2.05rem; font-weight: 720; letter-spacing: -.025em; margin: 0 0 .3rem 0;}
      .page-copy {max-width: 760px; opacity: .78; margin-bottom: 1.4rem;}
      .section-note {
        border-left: 3px solid rgba(49, 51, 63, .35);
        padding: .65rem .9rem;
        background: rgba(49, 51, 63, .035);
        border-radius: 0 8px 8px 0;
        margin: .4rem 0 1.2rem 0;
      }
      .small-muted {font-size: .84rem; opacity: .68;}
      .stDataFrame {border: 1px solid rgba(49, 51, 63, 0.08); border-radius: 10px; overflow: hidden;}
      h2, h3 {letter-spacing: -.015em;}
    </style>
    """,
    unsafe_allow_html=True,
)


def page_header(label: str, title: str, copy: str) -> None:
    st.markdown(f'<div class="eyebrow">{label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-copy">{copy}</div>', unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_public() -> pd.DataFrame:
    return load_public_context()


try:
    with st.spinner("Refreshing public practice context..."):
        public = get_public()
    public_error = None
except Exception as exc:
    public = pd.DataFrame(
        columns=[
            "practice_code",
            "practice_name",
            "ics_name",
            "phone_easy_pct",
            "website_easy_pct",
            "app_easy_pct",
            "list_size",
        ]
    )
    public_error = str(exc)

phone_median = float(public["phone_easy_pct"].median()) if not public.empty else 50.0
digital_series = pd.concat(
    [
        public.get("website_easy_pct", pd.Series(dtype=float)),
        public.get("app_easy_pct", pd.Series(dtype=float)),
    ]
)
digital_median = (
    float(pd.to_numeric(digital_series, errors="coerce").median())
    if not digital_series.empty
    else 50.0
)
list_q75 = (
    float(pd.to_numeric(public.get("list_size", pd.Series(dtype=float)), errors="coerce").quantile(0.75))
    if not public.empty and "list_size" in public
    else 12000
)


def tags_for(row) -> list[str]:
    return classify_practice(
        PracticeSignals(
            row.get("phone_easy_pct"),
            row.get("website_easy_pct"),
            row.get("app_easy_pct"),
            int(row["list_size"]) if pd.notna(row.get("list_size")) else None,
            phone_median,
            digital_median,
            list_q75,
        )
    )


if not public.empty:
    public = public.copy()
    public["signals"] = public.apply(lambda r: "; ".join(tags_for(r)), axis=1)

accounts = customer_accounts(public if not public.empty else None)


def account_tags(row) -> list[str]:
    if public.empty or not row.get("public_practice_code"):
        return ["Public context unavailable"]
    match = public[public.practice_code == row["public_practice_code"]]
    if match.empty:
        return ["Public context unavailable"]
    return tags_for(match.iloc[0])


accounts["public_tags"] = accounts.apply(account_tags, axis=1)
accounts["public_signal_count"] = accounts["public_tags"].apply(
    lambda xs: len(
        [
            x
            for x in xs
            if x not in {"No strong public-data signal", "Public context unavailable"}
        ]
    )
)
accounts[["upsell_state", "upsell_reasons"]] = accounts.apply(
    lambda r: pd.Series(
        upsell_readiness(
            r.existing_adoption_ratio,
            bool(r.stakeholder_engaged),
            int(r.public_signal_count),
            bool(r.critical_support_issue),
        )
    ),
    axis=1,
)
accounts["onboarding_health"] = accounts.apply(
    lambda r: onboarding_state(
        int(r.days_since_setup),
        bool(r.activation_complete),
        bool(r.critical_support_issue),
    ),
    axis=1,
)
accounts["adoption_health"] = accounts.apply(
    lambda r: adoption_health(
        bool(r.activation_complete),
        float(r.usage_ratio),
        float(r.four_week_change_pct),
        bool(r.critical_support_issue),
    ),
    axis=1,
)


st.sidebar.markdown("### Practice Growth OS")
st.sidebar.caption("Customer adoption, rollout and product-operations prototype")
section = st.sidebar.radio(
    "Workspace",
    [
        "Overview",
        "Practice signals",
        "Growth pipeline",
        "Adoption & value",
        "Customer insights",
        "Operating playbook",
    ],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("DATA BOUNDARY")
st.sidebar.markdown(
    "**Public:** NHS practice context  \n"
    "**Simulated:** customer state, usage, ROI and calls  \n"
    "**Excluded:** patient-level or clinical data"
)
with st.sidebar.expander("Automation boundary"):
    st.write("Rules calculate lifecycle states, readiness, risk and KPIs.")
    st.write("Drafting assistance prepares briefs, outreach and issue drafts.")
    st.write("People approve external communication, prioritisation and product actions.")
    st.caption("Drafting service: " + ("connected" if drafting_available() else "local fallback"))

if public_error:
    st.sidebar.warning("Public-data refresh unavailable in this session. Synthetic operations modules remain usable.")


if section == "Overview":
    page_header(
        "Operations console",
        "GP practice growth & adoption",
        "A portfolio operating system for moving from public practice context to customer growth, onboarding, adoption, value evidence and product feedback — without treating model output as ground truth.",
    )

    ready_count = int((accounts.upsell_state == "Ready for discovery").sum())
    active_count = int(accounts.activation_complete.sum())
    red_count = int((accounts.adoption_health == "Red").sum())
    recurring_count = len(recurring_issue_summary(transcripts().category, min_count=3))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Discovery-ready accounts", ready_count)
    c2.metric("Activated accounts", active_count)
    c3.metric("Adoption risks", red_count)
    c4.metric("Recurring issue themes", recurring_count)

    st.subheader("Operating flow")
    st.markdown(
        """
        **1. Observe** public access context → **2. Qualify** expansion readiness → **3. Activate** through onboarding →
        **4. Prove value** through usage and 90-day measures → **5. Learn** from customer feedback → **6. Improve** product and playbook.
        """
    )

    left, right = st.columns([1.15, 0.85])
    with left:
        st.subheader("Portfolio snapshot")
        overview = accounts[
            [
                "demo_customer_id",
                "public_practice_name",
                "current_product",
                "upsell_state",
                "onboarding_health",
                "adoption_health",
            ]
        ].copy()
        st.dataframe(overview, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Design principles")
        st.markdown(
            """
            - Public data creates **discovery signals**, not customer-fit scores.
            - Internal customer and usage fields are **synthetic and labelled**.
            - Workflow states and KPIs are **deterministic**.
            - Drafting assistance never sends or prioritises autonomously.
            - No patient-level data is required anywhere in the prototype.
            """
        )


elif section == "Practice signals":
    page_header(
        "Market context",
        "Practice signals",
        "Use real practice-level public data as a discovery starting point. Signals are transparent rules, not a hidden propensity score and not evidence of a commercial relationship.",
    )
    if public.empty:
        st.info("Public dataset is unavailable in this session. Refresh the deployment later to retry the NHS sources.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Practices loaded", f"{len(public):,}")
        c2.metric("Median easy phone access", f"{phone_median:.0f}%")
        c3.metric("Median digital access", f"{digital_median:.0f}%")
        c4.metric("Upper-quartile list size", f"{list_q75:,.0f}")

        f1, f2 = st.columns([1.3, 1])
        with f1:
            filter_text = st.text_input("Find practice or ICS", placeholder="Start typing a name...")
        with f2:
            signal_filter = st.selectbox(
                "Signal",
                [
                    "All",
                    "Phone access friction",
                    "Digital access friction",
                    "Digital-ready / phone constrained",
                    "Large registered population",
                    "No strong public-data signal",
                ],
            )
        view = public.copy()
        if filter_text:
            mask = view["practice_name"].str.contains(filter_text, case=False, na=False) | view[
                "ics_name"
            ].str.contains(filter_text, case=False, na=False)
            view = view[mask]
        if signal_filter != "All":
            view = view[view["signals"].str.contains(signal_filter, regex=False)]

        st.dataframe(
            view[
                [
                    "practice_code",
                    "practice_name",
                    "ics_name",
                    "list_size",
                    "phone_easy_pct",
                    "website_easy_pct",
                    "app_easy_pct",
                    "signals",
                ]
            ].head(500),
            use_container_width=True,
            hide_index=True,
        )

        selected_name = st.selectbox(
            "Open practice context",
            view["practice_name"].head(500).tolist() if not view.empty else [],
        )
        if selected_name:
            row = view[view.practice_name == selected_name].iloc[0]
            tags = tags_for(row)
            st.markdown('<div class="section-note"><strong>Observed signals</strong><br>' + " · ".join(tags) + "</div>", unsafe_allow_html=True)
            if st.button("Prepare discovery brief", type="primary"):
                st.markdown("#### Discovery brief")
                st.write(draft_account_brief(row.to_dict(), tags))
                st.caption("Draft for operator review. Public data does not establish product need or customer status.")


elif section == "Growth pipeline":
    page_header(
        "Customer growth",
        "Upsell readiness & onboarding",
        "A simulated existing-customer portfolio showing how expansion readiness and onboarding risk can be made explicit before a team scales outreach.",
    )
    st.caption("Customer-state fields are synthetic. Any real practice name shown is a public-context overlay only and does not imply a Healthtech-1 relationship.")

    display = accounts[
        [
            "demo_customer_id",
            "public_practice_name",
            "current_product",
            "existing_adoption_ratio",
            "stakeholder_engaged",
            "upsell_state",
            "onboarding_health",
        ]
    ].copy()
    st.dataframe(display, use_container_width=True, hide_index=True)

    aid = st.selectbox("Open demo account", accounts.demo_customer_id.tolist())
    a = accounts[accounts.demo_customer_id == aid].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Existing adoption", f"{a.existing_adoption_ratio:.0%}")
    c2.metric("Expansion state", a.upsell_state)
    c3.metric("Onboarding health", a.onboarding_health)
    c4.metric("Days since setup", int(a.days_since_setup))

    left, right = st.columns([1, 1])
    with left:
        st.markdown("#### Decision evidence")
        for reason in a.upsell_reasons:
            st.write("• " + reason)
        st.caption("Expansion state is rules-based. A person still decides whether and how to engage the account.")
    with right:
        st.markdown("#### Account context")
        st.write("**Current product:**", a.current_product)
        st.write("**Demo objective:**", a.synthetic_goal)
        st.write("**Public signals:**", ", ".join(a.public_tags))

    if st.button("Prepare outreach draft", type="primary"):
        st.text_area(
            "Draft — review before external use",
            draft_upsell_message(a.to_dict(), list(a.public_tags)),
            height=170,
        )


elif section == "Adoption & value":
    page_header(
        "Customer adoption",
        "Activation, usage & 90-day value",
        "Synthetic product-usage data demonstrates how a customer team could make activation risk, time-to-value and value evidence visible before the 90-day review.",
    )
    health_counts = accounts.adoption_health.value_counts().reindex(["Green", "Amber", "Red"]).fillna(0).astype(int)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Healthy", int(health_counts.get("Green", 0)))
    c2.metric("Needs attention", int(health_counts.get("Amber", 0)))
    c3.metric("At risk", int(health_counts.get("Red", 0)))
    c4.metric("Median time to first value", f"{accounts.time_to_first_value_days.median():.0f} days")

    adoption_view = accounts[
        [
            "demo_customer_id",
            "public_practice_name",
            "adoption_health",
            "usage_ratio",
            "four_week_change_pct",
            "weekly_requests",
            "automated_or_routed_pct",
            "time_to_first_value_days",
            "staff_minutes_saved_weekly",
        ]
    ]
    st.dataframe(adoption_view, use_container_width=True, hide_index=True)
    st.caption("Usage, routed %, time-to-value and staff-minutes-saved fields are synthetic demonstration measures, not Healthtech-1 performance claims.")

    selected = st.selectbox("Inspect adoption detail", accounts.demo_customer_id.tolist(), key="adoption-account")
    a = accounts[accounts.demo_customer_id == selected].iloc[0]
    left, right = st.columns(2)
    with left:
        st.markdown("#### Adoption evidence")
        st.progress(min(max(float(a.usage_ratio), 0.0), 1.0), text=f"Usage vs expected level: {a.usage_ratio:.0%}")
        st.write(f"Four-week change: **{a.four_week_change_pct:+.1f}%**")
        st.write(f"Weekly requests: **{int(a.weekly_requests):,}**")
    with right:
        st.markdown("#### Value evidence")
        st.write(f"Time to first value: **{int(a.time_to_first_value_days)} days**")
        st.write(f"Automated or routed: **{a.automated_or_routed_pct:.1f}%**")
        st.write(f"Illustrative staff time released: **{int(a.staff_minutes_saved_weekly)} min/week**")


elif section == "Customer insights":
    page_header(
        "Voice of customer",
        "Feedback → product action",
        "Synthetic customer-call excerpts show how unstructured feedback can be turned into reviewable product or operations issues while preserving the evidence behind the draft.",
    )
    t = transcripts()
    recurring = recurring_issue_summary(t.category, min_count=3)
    if recurring:
        cols = st.columns(min(len(recurring), 5))
        for idx, (cat, count) in enumerate(recurring[:5]):
            cols[idx].metric(cat, count)

    call = st.selectbox("Select synthetic customer call", t.call_id.tolist())
    row = t[t.call_id == call].iloc[0]
    st.caption(f"Theme: {row.category}")
    st.text_area("Customer note", row.transcript, height=120)
    if st.button("Create draft issue", type="primary"):
        ticket = extract_product_ticket(row.transcript)
        c1, c2 = st.columns([1.25, 0.75])
        with c1:
            st.markdown("#### Problem")
            st.write(ticket.get("problem", ""))
            st.markdown("#### Evidence")
            st.write(ticket.get("evidence", ""))
            st.markdown("#### Suggested outcome")
            st.write(ticket.get("suggested_outcome", ""))
        with c2:
            st.markdown("#### Triage")
            st.write("**Category:**", ticket.get("category", ""))
            st.write("**Severity:**", ticket.get("severity", ""))
            st.write("**Confidence:**", ticket.get("confidence", ""))
        st.caption("Draft only. Product/Operations should validate evidence, scope and priority before backlog creation.")


elif section == "Operating playbook":
    page_header(
        "Process design",
        "Onboarding & adoption playbook",
        "A repeatable customer journey that keeps objectives, launch readiness, early adoption, value evidence and feedback connected rather than treating onboarding as a one-off setup call.",
    )
    steps = [
        ("01", "Pre-onboarding", "Confirm objective, stakeholder owner, baseline workflow, success metric and dependencies."),
        ("02", "Discovery", "Map the current access/request flow and where staff effort or uncertainty occurs."),
        ("03", "Configuration", "Confirm access, appointment/service configuration, roles, data and launch readiness."),
        ("04", "Training", "Train core users and leave role-specific quick-reference guidance for later joiners."),
        ("05", "Activation", "Confirm first successful live use and capture launch blockers immediately."),
        ("06", "Early adoption", "Check usage, staff confidence, stalled workflows and support patterns after seven days."),
        ("07", "Value / ROI", "Compare the agreed baseline with 30/60/90-day operational measures; do not invent savings."),
        ("08", "Feedback", "Run structured customer check-ins and convert validated recurring friction into tickets."),
        ("09", "Risk escalation", "Define owner, evidence, urgency and next action for support or adoption risks."),
        ("10", "Expansion", "Only discuss expansion when existing adoption and customer outcomes support it."),
    ]
    for number, name, text in steps:
        st.markdown(f"**{number} · {name}**  \\n{text}")
        st.divider()

    recurring = recurring_issue_summary(transcripts().category, min_count=3)
    if recurring:
        st.markdown("### Suggested playbook changes")
        st.caption("Generated from recurring themes in the synthetic feedback set; changes still require an operator decision.")
        mapping = {
            "Onboarding / training": "Add a one-page workflow guide and a second training path for staff who join after launch.",
            "Configuration": "Add a mandatory pre-launch configuration check and a one-week post-launch review.",
            "Reporting / ROI": "Agree 30/60/90-day value measures before go-live and provide a simple evidence template.",
            "Workflow / UX": "Capture repeated workflow ambiguity with evidence and route validated patterns to Product.",
            "Support": "Standardise escalation evidence: screenshot, expected behaviour, urgency, owner and impact.",
        }
        for cat, count in recurring:
            st.write(f"**{cat} ({count} calls)** — {mapping.get(cat, 'Review recurring evidence and update the relevant playbook step.')}")


st.divider()
st.caption("Independent portfolio prototype. Healthtech-1 is not affiliated with or responsible for this project.")
