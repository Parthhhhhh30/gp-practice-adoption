from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from ai_layer import available as drafting_available
from ai_layer import draft_account_brief, draft_upsell_message, extract_product_ticket
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


STYLE = """
<style>
:root{--ink:#18251f;--muted:#65726b;--line:#dde5e0;--surface:#fff;--soft:#f5f8f6;--accent:#2f6b59;--accentsoft:#e8f1ed;--warn:#f7f0df;--risk:#f8e9e8}
.stApp{background:#f7f9f8}.block-container{max-width:1320px;padding-top:1.1rem;padding-bottom:4rem}[data-testid="stSidebar"]{display:none}[data-testid="stHeader"]{background:transparent}
h1,h2,h3,p,li,label{color:var(--ink)}h1,h2,h3{letter-spacing:-.02em}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.35rem 0 1rem;border-bottom:1px solid var(--line);margin-bottom:.85rem}.brandline{display:flex;align-items:center;gap:.75rem}.brandmark{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:var(--ink);color:#fff;font-weight:750}.brandname{font-size:1rem;font-weight:730}.brandsub,.topmeta,.muted{font-size:.8rem;color:var(--muted)}.topmeta{text-align:right}
.page-kicker{font-size:.72rem;text-transform:uppercase;letter-spacing:.11em;color:var(--accent);font-weight:760;margin-bottom:.35rem}.page-title{font-size:2.1rem;line-height:1.05;font-weight:760;letter-spacing:-.035em}.page-copy{max-width:790px;color:var(--muted);margin:.5rem 0 1.2rem;font-size:.98rem}
.card,.queue-card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:.95rem 1rem;margin-bottom:.65rem}.queue-head{display:flex;align-items:center;justify-content:space-between;gap:1rem}.queue-title{font-weight:720}.queue-sub{color:var(--muted);font-size:.84rem;margin-top:.25rem}.pill{display:inline-flex;align-items:center;border-radius:999px;padding:.24rem .58rem;font-size:.72rem;font-weight:700;border:1px solid var(--line);background:var(--soft);white-space:nowrap}.pill.good{background:var(--accentsoft);border-color:#d4e5dd;color:#245745}.pill.warn{background:var(--warn);border-color:#eadfbe;color:#785f1f}.pill.risk{background:var(--risk);border-color:#efd5d3;color:#8a3f3a}
.rail{display:grid;grid-template-columns:repeat(6,1fr);gap:.35rem;margin:.75rem 0 1.2rem}.rail-step{padding:.7rem .55rem;border-radius:10px;border:1px solid var(--line);background:var(--surface);font-size:.75rem;font-weight:680;text-align:center;color:var(--muted)}.rail-step.active{border-color:#aac9bd;background:var(--accentsoft);color:#245745}.status-row{display:flex;flex-wrap:wrap;gap:.4rem;margin-top:.75rem}.note{border:1px solid var(--line);border-radius:12px;background:var(--soft);padding:.8rem .9rem;font-size:.9rem}.score{border-top:1px solid var(--line);padding-top:.8rem;margin-top:.6rem}.score-label{color:var(--muted);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em}.score-value{font-size:1.35rem;font-weight:760;margin-top:.1rem}
[data-testid="stMetric"]{background:transparent;border:none;padding:0}[data-testid="stMetricLabel"]{color:var(--muted);font-size:.72rem}[data-testid="stMetricValue"]{color:var(--ink);font-size:1.35rem}div.stButton>button{border-radius:10px;font-weight:680;min-height:2.45rem}.stDataFrame{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}[data-testid="stSegmentedControl"] button{border-radius:999px!important;font-size:.84rem!important}
@media(max-width:900px){.rail{grid-template-columns:repeat(3,1fr)}.topmeta{display:none}}
</style>
"""


def safe(value) -> str:
    return html.escape(str(value if value is not None else ""))


def pill(text: str, tone: str = "") -> str:
    return f'<span class="pill {tone}">{safe(text)}</span>'


def tone_for(value: str) -> str:
    value = str(value).lower()
    if any(x in value for x in ("red", "risk", "blocked", "not ready")):
        return "risk"
    if any(x in value for x in ("amber", "develop", "attention", "monitor")):
        return "warn"
    if any(x in value for x in ("green", "ready", "healthy", "activated")):
        return "good"
    return ""


def header(kicker: str, title: str, copy: str) -> None:
    st.markdown(f'<div class="page-kicker">{safe(kicker)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{safe(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-copy">{safe(copy)}</div>', unsafe_allow_html=True)


def rail(active: int) -> None:
    names = ["Discover", "Configure", "Train", "Activate", "Prove value", "Expand"]
    blocks = [f'<div class="rail-step{" active" if i <= active else ""}">{safe(name)}</div>' for i, name in enumerate(names)]
    st.markdown('<div class="rail">' + "".join(blocks) + "</div>", unsafe_allow_html=True)


@st.cache_data(ttl=86400, show_spinner=False)
def get_public() -> pd.DataFrame:
    return load_public_context()


def prepare_data():
    try:
        public = get_public()
        error = None
    except Exception as exc:
        public = pd.DataFrame(columns=["practice_code", "practice_name", "ics_name", "phone_easy_pct", "website_easy_pct", "app_easy_pct", "list_size"])
        error = str(exc)

    phone_median = float(pd.to_numeric(public.get("phone_easy_pct", pd.Series(dtype=float)), errors="coerce").median()) if not public.empty else 50.0
    digital = pd.concat([public.get("website_easy_pct", pd.Series(dtype=float)), public.get("app_easy_pct", pd.Series(dtype=float))])
    digital_median = float(pd.to_numeric(digital, errors="coerce").median()) if not digital.empty else 50.0
    list_series = pd.to_numeric(public.get("list_size", pd.Series(dtype=float)), errors="coerce")
    list_available = bool(list_series.notna().any())
    list_q75 = float(list_series.quantile(.75)) if list_available else None

    def tags(row):
        return classify_practice(
            PracticeSignals(
                row.get("phone_easy_pct"), row.get("website_easy_pct"), row.get("app_easy_pct"),
                int(row["list_size"]) if pd.notna(row.get("list_size")) else None,
                phone_median, digital_median, list_q75,
            )
        )

    if not public.empty:
        public = public.copy()
        public["signals"] = public.apply(lambda r: "; ".join(tags(r)), axis=1)

    accounts = customer_accounts(public if not public.empty else None)

    def account_tags(row):
        if public.empty or not row.get("public_practice_code"):
            return ["Public context unavailable"]
        match = public[public.practice_code == row["public_practice_code"]]
        return tags(match.iloc[0]) if not match.empty else ["Public context unavailable"]

    accounts["public_tags"] = accounts.apply(account_tags, axis=1)
    accounts["public_signal_count"] = accounts.public_tags.apply(lambda xs: len([x for x in xs if x not in {"No strong public-data signal", "Public context unavailable"}]))
    accounts[["upsell_state", "upsell_reasons"]] = accounts.apply(
        lambda r: pd.Series(upsell_readiness(r.existing_adoption_ratio, bool(r.stakeholder_engaged), int(r.public_signal_count), bool(r.critical_support_issue))), axis=1
    )
    accounts["onboarding_health"] = accounts.apply(lambda r: onboarding_state(int(r.days_since_setup), bool(r.activation_complete), bool(r.critical_support_issue)), axis=1)
    accounts["adoption_health"] = accounts.apply(lambda r: adoption_health(bool(r.activation_complete), float(r.usage_ratio), float(r.four_week_change_pct), bool(r.critical_support_issue)), axis=1)
    return public, accounts, tags, phone_median, digital_median, list_available, list_q75, error


def queue_item(a) -> dict | None:
    if a.onboarding_health == "Red" or a.adoption_health == "Red":
        return {"priority": 0, "label": "Customer risk", "tone": "risk", "action": "Review blocker, confirm owner and schedule customer check-in"}
    if a.upsell_state == "Ready for discovery":
        return {"priority": 1, "label": "Expansion review", "tone": "good", "action": "Validate the expansion case and prepare a discovery conversation"}
    if a.onboarding_health == "Amber" or a.adoption_health == "Amber":
        return {"priority": 2, "label": "Check-in", "tone": "warn", "action": "Check activation or adoption friction before it becomes a retention issue"}
    return None


def render_today(accounts):
    header("Customer operations", "Today’s work queue", "Start from accounts that need a decision, check-in or launch action rather than from a generic KPI dashboard.")
    items = []
    for _, a in accounts.iterrows():
        base = queue_item(a)
        if base:
            base |= {"title": a.public_practice_name, "sub": f"{a.demo_customer_id} · {a.current_product} · onboarding {a.onboarding_health} · adoption {a.adoption_health}"}
            items.append(base)
    items.sort(key=lambda x: x["priority"])

    left, right = st.columns([1.35, .65], gap="large")
    with left:
        st.markdown("### Priority queue")
        for item in items[:7]:
            st.markdown(f'<div class="queue-card"><div class="queue-head"><div class="queue-title">{safe(item["title"])}</div>{pill(item["label"], item["tone"])}</div><div class="queue-sub">{safe(item["sub"])}</div><div style="margin-top:.55rem;font-size:.88rem"><strong>Next action:</strong> {safe(item["action"])}</div></div>', unsafe_allow_html=True)
    with right:
        ready = int((accounts.upsell_state == "Ready for discovery").sum())
        risks = int(((accounts.onboarding_health == "Red") | (accounts.adoption_health == "Red")).sum())
        recurring = len(recurring_issue_summary(transcripts().category, 3))
        st.markdown("### This cycle")
        st.markdown(f'<div class="card"><div class="score"><div class="score-label">Expansion reviews</div><div class="score-value">{ready}</div></div><div class="score"><div class="score-label">Activated accounts</div><div class="score-value">{int(accounts.activation_complete.sum())}</div></div><div class="score"><div class="score-label">Customer risks</div><div class="score-value">{risks}</div></div><div class="score"><div class="score-label">Recurring themes</div><div class="score-value">{recurring}</div></div></div>', unsafe_allow_html=True)
        st.markdown("### Operating boundary")
        st.markdown('<div class="note">Rules own lifecycle states and KPIs. Drafting assistance prepares reviewable content. People approve external communication, prioritisation and product decisions.</div>', unsafe_allow_html=True)


def render_practices(public, tags_for, phone_median, digital_median, list_available, list_q75):
    header("Public market context", "Practice explorer", "Use real practice-level access results as discovery context. Signals are explicit rules, not a hidden sales-propensity score.")
    if public.empty:
        st.info("The public GP Patient Survey feed is unavailable in this session.")
        return

    f1, f2 = st.columns([1.4, 1])
    with f1:
        text = st.text_input("Find a practice or ICS", placeholder="Search name or system...")
    signal_options = ["All", "Phone access friction", "Digital access friction", "Digital-ready / phone constrained"]
    if list_available:
        signal_options.append("Large registered population")
    signal_options.append("No strong public-data signal")
    with f2:
        signal = st.selectbox("Observed signal", signal_options)

    view = public.copy()
    if text:
        view = view[view.practice_name.str.contains(text, case=False, na=False) | view.ics_name.str.contains(text, case=False, na=False)]
    if signal != "All":
        view = view[view.signals.str.contains(signal, regex=False)]

    if view.empty:
        st.info("No practices match the current filters.")
        return

    name = st.selectbox("Open practice", view.practice_name.head(500).tolist())
    row = view[view.practice_name == name].iloc[0]
    tags = tags_for(row)
    st.markdown(f'<div class="card"><div class="queue-title">{safe(row.practice_name)}</div><div class="queue-sub">{safe(row.ics_name)} · {safe(row.practice_code)}</div><div class="status-row">{"".join(pill(x, tone_for(x)) for x in tags)}</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Registered list", f"{int(row.list_size):,}" if list_available and pd.notna(row.list_size) else "Unavailable")
    c2.metric("Easy phone access", f"{row.phone_easy_pct:.0f}%" if pd.notna(row.phone_easy_pct) else "—")
    c3.metric("Easy website access", f"{row.website_easy_pct:.0f}%" if pd.notna(row.website_easy_pct) else "—")
    c4.metric("Easy NHS App access", f"{row.app_easy_pct:.0f}%" if pd.notna(row.app_easy_pct) else "—")
    if not list_available:
        st.caption("Registered-list enrichment is unavailable from this cloud session; no population-size signal is inferred.")

    if st.button("Prepare discovery brief", type="primary"):
        try:
            st.write(draft_account_brief(row.to_dict(), tags))
        except Exception as exc:
            st.error(f"Drafting service error: {exc}")
        st.caption("Review before use. Public data does not establish product need or customer status.")

    with st.expander("Browse source data"):
        cols = ["practice_code", "practice_name", "ics_name", "phone_easy_pct", "website_easy_pct", "app_easy_pct", "signals"]
        if list_available:
            cols.insert(3, "list_size")
        st.dataframe(view[cols].head(500), use_container_width=True, hide_index=True)
        context = f"Loaded {len(public):,} practices · phone median {phone_median:.0f}% · digital median {digital_median:.0f}%"
        if list_available and list_q75 is not None:
            context += f" · upper-quartile list size {list_q75:,.0f}"
        st.caption(context)


def account_selector(accounts, key: str):
    aid = st.selectbox("Account", accounts.demo_customer_id.tolist(), key=key, format_func=lambda x: f"{x} — {accounts.loc[accounts.demo_customer_id == x, 'public_practice_name'].iloc[0]}")
    return accounts[accounts.demo_customer_id == aid].iloc[0]


def render_accounts(accounts):
    header("Customer growth", "Account workspace", "Open one simulated account, understand why it is ready or at risk, and move from evidence to a human-owned next action.")
    st.caption("Customer state is synthetic. A real practice name is a public-context overlay only and does not imply a Healthtech-1 relationship.")
    a = account_selector(accounts, "account-workspace")
    st.markdown(f'<div class="card"><div class="queue-title">{safe(a.public_practice_name)}</div><div class="queue-sub">{safe(a.demo_customer_id)} · current product: {safe(a.current_product)}</div><div class="status-row">{pill(a.upsell_state,tone_for(a.upsell_state))}{pill(a.onboarding_health,tone_for(a.onboarding_health))}{pill(a.adoption_health,tone_for(a.adoption_health))}</div></div>', unsafe_allow_html=True)

    active = 2 if not a.activation_complete and a.days_since_setup <= 7 else 1 if not a.activation_complete else 3 if a.usage_ratio < .75 else 5 if a.upsell_state == "Ready for discovery" else 4
    rail(active)
    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown("### Decision evidence")
        for reason in a.upsell_reasons:
            st.write("• " + reason)
        st.write("**Demo objective:**", a.synthetic_goal)
        st.write("**Public signals:**", ", ".join(a.public_tags))
    with right:
        c1, c2 = st.columns(2)
        c1.metric("Existing adoption", f"{a.existing_adoption_ratio:.0%}")
        c2.metric("Days since setup", int(a.days_since_setup))
        st.markdown('<div class="note"><strong>Operator decision</strong><br>Resolve active support or activation risk first. Consider expansion only when current adoption and customer outcomes support it.</div>', unsafe_allow_html=True)

    if st.button("Prepare outreach draft", type="primary"):
        try:
            st.text_area("Draft — review before external use", draft_upsell_message(a.to_dict(), list(a.public_tags)), height=170)
        except Exception as exc:
            st.error(f"Drafting service error: {exc}")

    with st.expander("Open portfolio list"):
        st.dataframe(accounts[["demo_customer_id","public_practice_name","current_product","existing_adoption_ratio","upsell_state","onboarding_health","adoption_health"]], use_container_width=True, hide_index=True)


def render_adoption(accounts):
    header("Customer value", "Adoption review", "Review activation, usage trajectory and value evidence for one simulated customer before retention or expansion decisions.")
    a = account_selector(accounts, "adoption-workspace")
    st.markdown(f'<div class="card"><div class="queue-head"><div><div class="queue-title">{safe(a.public_practice_name)}</div><div class="queue-sub">90-day value review · synthetic usage data</div></div>{pill(a.adoption_health,tone_for(a.adoption_health))}</div></div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, .9], gap="large")
    with left:
        st.markdown("### Adoption trajectory")
        st.progress(min(max(float(a.usage_ratio), 0), 1), text=f"Usage vs expected level: {a.usage_ratio:.0%}")
        st.write(f"Four-week usage change: **{a.four_week_change_pct:+.1f}%**")
        st.write(f"Weekly requests: **{int(a.weekly_requests):,}**")
        st.markdown('<div class="note">Health is rules-based from activation, usage, recent trend and critical-support status — not an AI sentiment score.</div>', unsafe_allow_html=True)
    with right:
        c1, c2 = st.columns(2)
        c1.metric("Time to first value", f"{int(a.time_to_first_value_days)} days")
        c2.metric("Automated / routed", f"{a.automated_or_routed_pct:.1f}%")
        st.metric("Illustrative staff time released", f"{int(a.staff_minutes_saved_weekly)} min/week")
        st.caption("Synthetic demonstration measures, not Healthtech-1 performance claims.")


def render_feedback():
    header("Voice of customer", "Feedback inbox", "Preserve the original customer evidence, identify recurring friction and create a reviewable issue without silently setting product priority.")
    data = transcripts()
    recurring = recurring_issue_summary(data.category, 3)
    left, right = st.columns([.9,1.1], gap="large")
    with left:
        st.markdown("### Recurring themes")
        for category, count in recurring:
            st.markdown(f'<div class="queue-card"><div class="queue-head"><div class="queue-title">{safe(category)}</div>{pill(str(count)+" calls","warn")}</div></div>', unsafe_allow_html=True)
        call = st.selectbox("Customer call", data.call_id.tolist())
        row = data[data.call_id == call].iloc[0]
        st.caption(f"Synthetic transcript · {row.category}")
        st.text_area("Customer note", row.transcript, height=170)
    with right:
        st.markdown("### Draft issue")
        st.markdown('<div class="note">The draft never writes to a backlog automatically. Product/Operations still validates evidence, scope and priority.</div>', unsafe_allow_html=True)
        if st.button("Create draft issue", type="primary"):
            try:
                ticket = extract_product_ticket(row.transcript)
                st.markdown("#### Problem"); st.write(ticket.get("problem",""))
                st.markdown("#### Evidence"); st.write(ticket.get("evidence",""))
                st.markdown("#### Suggested outcome"); st.write(ticket.get("suggested_outcome",""))
                st.markdown('<div class="status-row">'+pill(ticket.get("category",""))+pill(ticket.get("severity",""),tone_for(ticket.get("severity","")))+pill("Confidence: "+str(ticket.get("confidence","")))+'</div>', unsafe_allow_html=True)
            except Exception as exc:
                st.error(f"Drafting service error: {exc}")


def render_playbook():
    header("Process design", "Onboarding & adoption playbook", "A repeatable journey from discovery to expansion, with suggested changes driven by recurring synthetic feedback rather than by model intuition.")
    steps = [
        ("01","Pre-onboarding","Confirm objective, stakeholder owner, baseline workflow, success metric and dependencies."),
        ("02","Discovery","Map the current access/request flow and where staff effort or uncertainty occurs."),
        ("03","Configuration","Confirm access, appointment/service configuration, roles, data and launch readiness."),
        ("04","Training","Train core users and leave role-specific quick-reference guidance for later joiners."),
        ("05","Activation","Confirm first successful live use and capture launch blockers immediately."),
        ("06","Early adoption","Check usage, staff confidence, stalled workflows and support patterns after seven days."),
        ("07","Value / ROI","Compare the agreed baseline with 30/60/90-day operational measures; do not invent savings."),
        ("08","Feedback","Run structured customer check-ins and convert validated recurring friction into tickets."),
        ("09","Risk escalation","Define owner, evidence, urgency and next action for support or adoption risks."),
        ("10","Expansion","Discuss expansion only when existing adoption and customer outcomes support it."),
    ]
    mapping = {
        "Onboarding / training":"Add a one-page workflow guide and a second training path for staff who join after launch.",
        "Configuration":"Add a pre-launch configuration check and a one-week post-launch review.",
        "Reporting / ROI":"Agree 30/60/90-day value measures before go-live and use a simple evidence template.",
        "Workflow / UX":"Capture repeated workflow ambiguity with evidence and route validated patterns to Product.",
        "Support":"Standardise escalation evidence: screenshot, expected behaviour, urgency, owner and impact.",
    }
    left, right = st.columns([1.1,.9], gap="large")
    with left:
        st.markdown("### Journey")
        for number,name,text in steps:
            st.markdown(f'<div class="queue-card"><div class="queue-title">{number} · {safe(name)}</div><div class="queue-sub">{safe(text)}</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown("### Suggested changes")
        for category,count in recurring_issue_summary(transcripts().category,3):
            st.markdown(f'<div class="queue-card"><div class="queue-head"><div class="queue-title">{safe(category)}</div>{pill(str(count)+" calls","warn")}</div><div class="queue-sub">{safe(mapping.get(category,"Review recurring evidence and update the relevant step."))}</div></div>', unsafe_allow_html=True)


def run():
    st.markdown(STYLE, unsafe_allow_html=True)
    public, accounts, tags_for, phone_median, digital_median, list_available, list_q75, public_error = prepare_data()

    st.markdown('<div class="topbar"><div class="brandline"><div class="brandmark">+</div><div><div class="brandname">Practice Growth Workspace</div><div class="brandsub">Adoption, rollout and product operations</div></div></div><div class="topmeta">Independent portfolio prototype<br>Public NHS context + simulated customer operations</div></div>', unsafe_allow_html=True)
    section = st.segmented_control("Workspace", ["Today","Practices","Accounts","Adoption","Feedback","Playbook"], default="Today", label_visibility="collapsed") or "Today"
    if public_error:
        st.warning("Public GP Patient Survey refresh is unavailable in this session. Synthetic customer-operations modules remain usable.")

    if section == "Today": render_today(accounts)
    elif section == "Practices": render_practices(public, tags_for, phone_median, digital_median, list_available, list_q75)
    elif section == "Accounts": render_accounts(accounts)
    elif section == "Adoption": render_adoption(accounts)
    elif section == "Feedback": render_feedback()
    else: render_playbook()

    st.divider()
    left,right = st.columns(2)
    with left: st.caption("Independent portfolio prototype. Healthtech-1 is not affiliated with or responsible for this project.")
    with right: st.caption(f"Drafting service: {'connected' if drafting_available() else 'local fallback'} · No patient-level or clinical data")
