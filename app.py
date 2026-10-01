from __future__ import annotations

import html

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
    page_title="Practice Growth Workspace",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      :root {
        --ink: #18251f;
        --muted: #65726b;
        --line: #dde5e0;
        --surface: #ffffff;
        --surface-soft: #f5f8f6;
        --accent: #2f6b59;
        --accent-soft: #e8f1ed;
        --warn-soft: #f7f0df;
        --risk-soft: #f8e9e8;
      }

      .stApp { background: #f7f9f8; }
      .block-container { max-width: 1320px; padding-top: 1.1rem; padding-bottom: 4rem; }
      [data-testid="stSidebar"] { display: none; }
      [data-testid="stHeader"] { background: transparent; }
      [data-testid="stToolbar"] { right: 1rem; }

      h1, h2, h3 { color: var(--ink); letter-spacing: -.02em; }
      p, li, label { color: var(--ink); }

      .topbar {
        display: flex; align-items: center; justify-content: space-between;
        gap: 1rem; padding: .35rem 0 1rem 0; border-bottom: 1px solid var(--line);
        margin-bottom: .85rem;
      }
      .brandline { display: flex; align-items: center; gap: .75rem; }
      .brandmark {
        width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center;
        background: var(--ink); color: white; font-weight: 750; font-size: 1.05rem;
      }
      .brandname { font-size: 1rem; font-weight: 730; color: var(--ink); }
      .brandsub { font-size: .78rem; color: var(--muted); margin-top: .05rem; }
      .topmeta { font-size: .78rem; color: var(--muted); text-align: right; }

      .page-kicker { font-size: .72rem; text-transform: uppercase; letter-spacing: .11em; color: var(--accent); font-weight: 760; margin-bottom: .35rem; }
      .page-title { font-size: 2.1rem; line-height: 1.05; font-weight: 760; color: var(--ink); letter-spacing: -.035em; }
      .page-copy { max-width: 780px; color: var(--muted); margin-top: .5rem; margin-bottom: 1.2rem; font-size: .98rem; }

      .queue-card {
        background: var(--surface); border: 1px solid var(--line); border-radius: 14px;
        padding: .95rem 1rem; margin-bottom: .65rem; box-shadow: 0 1px 1px rgba(20, 30, 25, .02);
      }
      .queue-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
      .queue-title { font-weight: 720; color: var(--ink); }
      .queue-sub { color: var(--muted); font-size: .84rem; margin-top: .25rem; }

      .pill {
        display: inline-flex; align-items: center; border-radius: 999px; padding: .24rem .58rem;
        font-size: .72rem; font-weight: 700; border: 1px solid var(--line); background: var(--surface-soft);
        color: var(--ink); white-space: nowrap;
      }
      .pill.good { background: var(--accent-soft); border-color: #d4e5dd; color: #245745; }
      .pill.warn { background: var(--warn-soft); border-color: #eadfbe; color: #785f1f; }
      .pill.risk { background: var(--risk-soft); border-color: #efd5d3; color: #8a3f3a; }

      .rail {
        display: grid; grid-template-columns: repeat(6, 1fr); gap: .35rem; margin: .75rem 0 1.2rem 0;
      }
      .rail-step {
        padding: .7rem .55rem; border-radius: 10px; border: 1px solid var(--line); background: var(--surface);
        font-size: .75rem; font-weight: 680; text-align: center; color: var(--muted);
      }
      .rail-step.active { border-color: #aac9bd; background: var(--accent-soft); color: #245745; }

      .profile-card {
        border: 1px solid var(--line); border-radius: 16px; background: var(--surface); padding: 1.05rem 1.1rem;
      }
      .profile-title { font-size: 1.18rem; font-weight: 760; color: var(--ink); }
      .profile-meta { color: var(--muted); font-size: .84rem; margin-top: .2rem; }
      .status-row { display: flex; flex-wrap: wrap; gap: .4rem; margin-top: .85rem; }

      .scorecard {
        border-top: 1px solid var(--line); padding-top: .85rem; margin-top: .6rem;
      }
      .score-label { color: var(--muted); font-size: .75rem; text-transform: uppercase; letter-spacing: .06em; }
      .score-value { color: var(--ink); font-size: 1.35rem; font-weight: 760; margin-top: .1rem; }

      .note-box {
        border: 1px solid var(--line); border-radius: 12px; background: var(--surface-soft); padding: .8rem .9rem;
        color: var(--ink); font-size: .9rem;
      }

      [data-testid="stMetric"] { background: transparent; border: none; padding: 0; }
      [data-testid="stMetricLabel"] { color: var(--muted); font-size: .72rem; }
      [data-testid="stMetricValue"] { color: var(--ink); font-size: 1.35rem; }
      div.stButton > button { border-radius: 10px; font-weight: 680; min-height: 2.45rem; }
      .stDataFrame { border: 1px solid var(--line); border-radius: 12px; overflow: hidden; background: white; }

      [data-testid="stSegmentedControl"] button {
        border-radius: 999px !important;
        font-size: .84rem !important;
      }

      @media (max-width: 900px) {
        .rail { grid-template-columns: repeat(3, 1fr); }
        .topmeta { display: none; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def safe(value) -> str:
    return html.escape(str(value if value is not None else ""))


def page_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(f'<div class="page-kicker">{safe(kicker)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{safe(title)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-copy">{safe(copy)}</div>', unsafe_allow_html=True)


def pill(text: str, tone: str = "") -> str:
    tone_class = f" {tone}" if tone else ""
    return f'<span class="pill{tone_class}">{safe(text)}</span>'


def tone_for(value: str) -> str:
    val = str(value).lower()
    if any(word in val for word in ["green", "ready", "healthy", "on track", "activated"]):
        return "good"
    if any(word in val for word in ["red", "risk", "blocked", "stalled", "not ready"]):
        return "risk"
    if any(word in val for word in ["amber", "develop", "attention", "monitor"]):
        return "warn"
    return ""


def lifecycle_rail(active_index: int) -> None:
    steps = ["Discover", "Configure", "Train", "Activate", "Prove value", "Expand"]
    blocks = []
    for idx, step in enumerate(steps):
        cls = "rail-step active" if idx <= active_index else "rail-step"
        blocks.append(f'<div class="{cls}">{safe(step)}</div>')
    st.markdown('<div class="rail">' + "".join(blocks) + "</div>", unsafe_allow_html=True)


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
        [x for x in xs if x not in {"No strong public-data signal", "Public context unavailable"}]
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


st.markdown(
    """
    <div class="topbar">
      <div class="brandline">
        <div class="brandmark">+</div>
        <div>
          <div class="brandname">Practice Growth Workspace</div>
          <div class="brandsub">Adoption, rollout and product operations</div>
        </div>
      </div>
      <div class="topmeta">Independent portfolio prototype<br>Public NHS context + simulated customer operations</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav = st.segmented_control(
    "Workspace",
    ["Today", "Practices", "Accounts", "Adoption", "Feedback", "Playbook"],
    default="Today",
    label_visibility="collapsed",
)
section = nav or "Today"

if public_error:
    st.warning("Public NHS refresh is unavailable in this session. Customer-operations modules remain usable with synthetic data.")


if section == "Today":
    page_header(
        "Customer operations",
        "Today’s work queue",
        "Start from the accounts that need a decision, a check-in or a launch action — not from a generic dashboard of metrics.",
    )

    queue_items: list[dict] = []
    for _, a in accounts.iterrows():
        if a.onboarding_health in {"Activation risk", "Blocked"} or a.adoption_health == "Red":
            queue_items.append(
                {
                    "priority": 0,
                    "label": "Adoption risk",
                    "tone": "risk",
                    "title": a.public_practice_name,
                    "sub": f"{a.demo_customer_id} · {a.current_product} · {a.onboarding_health} · {a.adoption_health}",
                    "action": "Review blocker, confirm owner and schedule customer check-in",
                }
            )
        elif a.upsell_state == "Ready for discovery":
            queue_items.append(
                {
                    "priority": 1,
                    "label": "Expansion review",
                    "tone": "good",
                    "title": a.public_practice_name,
                    "sub": f"{a.demo_customer_id} · existing adoption {a.existing_adoption_ratio:.0%}",
                    "action": "Validate expansion case and prepare discovery conversation",
                }
            )
        elif a.adoption_health == "Amber":
            queue_items.append(
                {
                    "priority": 2,
                    "label": "Check-in",
                    "tone": "warn",
                    "title": a.public_practice_name,
                    "sub": f"{a.demo_customer_id} · usage {a.usage_ratio:.0%} · 4-week change {a.four_week_change_pct:+.1f}%",
                    "action": "Check adoption friction before it becomes a retention issue",
                }
            )

    queue_items = sorted(queue_items, key=lambda x: x["priority"])
    left, right = st.columns([1.35, .65], gap="large")
    with left:
        st.markdown("### Priority queue")
        if not queue_items:
            st.info("No accounts currently meet the demo queue rules.")
        for item in queue_items[:6]:
            st.markdown(
                f"""
                <div class="queue-card">
                  <div class="queue-head">
                    <div class="queue-title">{safe(item['title'])}</div>
                    {pill(item['label'], item['tone'])}
                  </div>
                  <div class="queue-sub">{safe(item['sub'])}</div>
                  <div style="margin-top:.55rem;font-size:.88rem;color:#18251f;"><strong>Next action:</strong> {safe(item['action'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("### This cycle")
        ready_count = int((accounts.upsell_state == "Ready for discovery").sum())
        active_count = int(accounts.activation_complete.sum())
        red_count = int((accounts.adoption_health == "Red").sum())
        recurring_count = len(recurring_issue_summary(transcripts().category, min_count=3))
        st.markdown(
            f"""
            <div class="profile-card">
              <div class="scorecard"><div class="score-label">Expansion reviews</div><div class="score-value">{ready_count}</div></div>
              <div class="scorecard"><div class="score-label">Activated accounts</div><div class="score-value">{active_count}</div></div>
              <div class="scorecard"><div class="score-label">Adoption risks</div><div class="score-value">{red_count}</div></div>
              <div class="scorecard"><div class="score-label">Recurring feedback themes</div><div class="score-value">{recurring_count}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("### Operating model")
        st.markdown(
            '<div class="note-box">Public data creates discovery context. Customer state, usage and ROI are simulated. Rules own lifecycle states and KPIs. Drafting assistance prepares reviewable content; people approve external and product actions.</div>',
            unsafe_allow_html=True,
        )


elif section == "Practices":
    page_header(
        "Public market context",
        "Practice explorer",
        "Use practice-level NHS data as a discovery starting point. The interface shows observed signals first; it does not manufacture a hidden propensity score.",
    )
    if public.empty:
        st.info("Public dataset is unavailable in this session. Refresh the deployment later to retry the NHS sources.")
    else:
        filter_col, signal_col = st.columns([1.4, 1])
        with filter_col:
            filter_text = st.text_input("Find a practice or ICS", placeholder="Search by practice or system name...")
        with signal_col:
            signal_filter = st.selectbox(
                "Observed signal",
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

        selected_name = st.selectbox(
            "Open practice",
            view["practice_name"].head(500).tolist() if not view.empty else [],
        )

        if selected_name:
            row = view[view.practice_name == selected_name].iloc[0]
            tags = tags_for(row)
            st.markdown(
                f"""
                <div class="profile-card">
                  <div class="profile-title">{safe(row['practice_name'])}</div>
                  <div class="profile-meta">{safe(row.get('ics_name', ''))} · {safe(row.get('practice_code', ''))}</div>
                  <div class="status-row">{''.join(pill(tag, tone_for(tag)) for tag in tags)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Registered list", f"{int(row['list_size']):,}" if pd.notna(row.get("list_size")) else "—")
            c2.metric("Easy phone access", f"{row['phone_easy_pct']:.0f}%" if pd.notna(row.get("phone_easy_pct")) else "—")
            c3.metric("Easy website access", f"{row['website_easy_pct']:.0f}%" if pd.notna(row.get("website_easy_pct")) else "—")
            c4.metric("Easy NHS App access", f"{row['app_easy_pct']:.0f}%" if pd.notna(row.get("app_easy_pct")) else "—")

            if st.button("Prepare discovery brief", type="primary"):
                st.markdown("#### Discovery brief")
                st.write(draft_account_brief(row.to_dict(), tags))
                st.caption("Draft for operator review. Public data does not establish product need or customer status.")

        with st.expander("Browse the underlying practice dataset"):
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
            st.caption(
                f"Loaded {len(public):,} practices · phone median {phone_median:.0f}% · digital median {digital_median:.0f}% · upper-quartile list size {list_q75:,.0f}."
            )


elif section == "Accounts":
    page_header(
        "Customer growth",
        "Account workspace",
        "Open one simulated customer at a time, understand why it is ready or at risk, and move from evidence to a human-owned next action.",
    )
    st.caption("Customer state is synthetic. A real practice name, when shown, is public context only and does not imply a Healthtech-1 relationship.")

    aid = st.selectbox(
        "Account",
        accounts.demo_customer_id.tolist(),
        format_func=lambda x: f"{x} — {accounts.loc[accounts.demo_customer_id == x, 'public_practice_name'].iloc[0]}",
    )
    a = accounts[accounts.demo_customer_id == aid].iloc[0]

    st.markdown(
        f"""
        <div class="profile-card">
          <div class="profile-title">{safe(a.public_practice_name)}</div>
          <div class="profile-meta">{safe(a.demo_customer_id)} · Current product: {safe(a.current_product)}</div>
          <div class="status-row">
            {pill(a.upsell_state, tone_for(a.upsell_state))}
            {pill(a.onboarding_health, tone_for(a.onboarding_health))}
            {pill(a.adoption_health, tone_for(a.adoption_health))}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not bool(a.activation_complete):
        active_step = 2 if int(a.days_since_setup) <= 7 else 1
    elif float(a.usage_ratio) < .75:
        active_step = 3
    elif a.upsell_state == "Ready for discovery":
        active_step = 5
    else:
        active_step = 4
    lifecycle_rail(active_step)

    left, right = st.columns([1.15, .85], gap="large")
    with left:
        st.markdown("### Why this account is here")
        for reason in a.upsell_reasons:
            st.write("• " + reason)
        st.markdown("### Context")
        st.write("**Demo objective:**", a.synthetic_goal)
        st.write("**Public signals:**", ", ".join(a.public_tags))
        st.caption("Expansion state is deterministic. A person still decides whether and how to engage the account.")
    with right:
        st.markdown("### Current state")
        c1, c2 = st.columns(2)
        c1.metric("Existing adoption", f"{a.existing_adoption_ratio:.0%}")
        c2.metric("Days since setup", int(a.days_since_setup))
        st.markdown(
            '<div class="note-box"><strong>Operator decision</strong><br>Confirm the customer outcome, check for active support risk, then decide whether the next action is activation support, value review or expansion discovery.</div>',
            unsafe_allow_html=True,
        )

    if st.button("Prepare outreach draft", type="primary"):
        st.text_area(
            "Draft — review before external use",
            draft_upsell_message(a.to_dict(), list(a.public_tags)),
            height=170,
        )

    with st.expander("Open portfolio list"):
        display = accounts[
            [
                "demo_customer_id",
                "public_practice_name",
                "current_product",
                "existing_adoption_ratio",
                "upsell_state",
                "onboarding_health",
                "adoption_health",
            ]
        ].copy()
        st.dataframe(display, use_container_width=True, hide_index=True)


elif section == "Adoption":
    page_header(
        "Customer value",
        "Adoption review",
        "A 90-day review workspace for one account at a time: activation, usage trajectory and value evidence before expansion or retention decisions.",
    )

    selected = st.selectbox(
        "Account",
        accounts.demo_customer_id.tolist(),
        key="adoption-account",
        format_func=lambda x: f"{x} — {accounts.loc[accounts.demo_customer_id == x, 'public_practice_name'].iloc[0]}",
    )
    a = accounts[accounts.demo_customer_id == selected].iloc[0]

    st.markdown(
        f"""
        <div class="profile-card">
          <div class="queue-head">
            <div>
              <div class="profile-title">{safe(a.public_practice_name)}</div>
              <div class="profile-meta">90-day value review · synthetic usage data</div>
            </div>
            {pill(a.adoption_health, tone_for(a.adoption_health))}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, .9], gap="large")
    with left:
        st.markdown("### Adoption trajectory")
        st.progress(min(max(float(a.usage_ratio), 0.0), 1.0), text=f"Usage vs expected level: {a.usage_ratio:.0%}")
        st.write(f"Four-week usage change: **{a.four_week_change_pct:+.1f}%**")
        st.write(f"Weekly requests: **{int(a.weekly_requests):,}**")
        st.markdown(
            '<div class="note-box">Health is rules-based from activation, current usage, recent trend and critical-support status. It is not an AI sentiment score.</div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("### Value evidence")
        c1, c2 = st.columns(2)
        c1.metric("Time to first value", f"{int(a.time_to_first_value_days)} days")
        c2.metric("Automated / routed", f"{a.automated_or_routed_pct:.1f}%")
        st.metric("Illustrative staff time released", f"{int(a.staff_minutes_saved_weekly)} min/week")
        st.caption("All usage and value fields here are synthetic demonstration measures, not Healthtech-1 performance claims.")

    with st.expander("Compare the portfolio"):
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


elif section == "Feedback":
    page_header(
        "Voice of customer",
        "Feedback inbox",
        "Treat customer calls as evidence: review the original note, identify recurring friction, then create a draft issue without losing the source context.",
    )
    t = transcripts()
    recurring = recurring_issue_summary(t.category, min_count=3)

    left, right = st.columns([.9, 1.1], gap="large")
    with left:
        st.markdown("### Recurring themes")
        if recurring:
            for cat, count in recurring:
                st.markdown(
                    f'<div class="queue-card"><div class="queue-head"><div class="queue-title">{safe(cat)}</div>{pill(str(count) + " calls", "warn")}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No recurring themes meet the current threshold.")

        call = st.selectbox("Customer call", t.call_id.tolist())
        row = t[t.call_id == call].iloc[0]
        st.caption(f"Synthetic transcript · Theme: {row.category}")
        st.text_area("Customer note", row.transcript, height=170)

    with right:
        st.markdown("### Draft issue")
        st.markdown(
            '<div class="note-box">Select a call and create a reviewable issue. The draft does not write to a backlog or set product priority.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Create draft issue", type="primary"):
            ticket = extract_product_ticket(row.transcript)
            st.markdown("#### Problem")
            st.write(ticket.get("problem", ""))
            st.markdown("#### Evidence")
            st.write(ticket.get("evidence", ""))
            st.markdown("#### Suggested outcome")
            st.write(ticket.get("suggested_outcome", ""))
            st.markdown(
                '<div class="status-row">'
                + pill(ticket.get("category", ""))
                + pill(ticket.get("severity", ""), tone_for(ticket.get("severity", "")))
                + pill("Confidence: " + str(ticket.get("confidence", "")))
                + '</div>',
                unsafe_allow_html=True,
            )
            st.caption("Draft only. Product/Operations should validate evidence, scope and priority before backlog creation.")


elif section == "Playbook":
    page_header(
        "Process design",
        "Onboarding & adoption playbook",
        "A versioned customer journey that keeps launch, early adoption, value evidence and feedback connected instead of treating onboarding as a one-off setup call.",
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

    left, right = st.columns([1.1, .9], gap="large")
    with left:
        st.markdown("### Journey")
        for number, name, text in steps:
            st.markdown(
                f"""
                <div class="queue-card">
                  <div class="queue-head"><div class="queue-title">{safe(number)} · {safe(name)}</div></div>
                  <div class="queue-sub">{safe(text)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    with right:
        st.markdown("### Suggested changes")
        recurring = recurring_issue_summary(transcripts().category, min_count=3)
        mapping = {
            "Onboarding / training": "Add a one-page workflow guide and a second training path for staff who join after launch.",
            "Configuration": "Add a mandatory pre-launch configuration check and a one-week post-launch review.",
            "Reporting / ROI": "Agree 30/60/90-day value measures before go-live and provide a simple evidence template.",
            "Workflow / UX": "Capture repeated workflow ambiguity with evidence and route validated patterns to Product.",
            "Support": "Standardise escalation evidence: screenshot, expected behaviour, urgency, owner and impact.",
        }
        if recurring:
            for cat, count in recurring:
                st.markdown(
                    f'<div class="queue-card"><div class="queue-head"><div class="queue-title">{safe(cat)}</div>{pill(str(count) + " calls", "warn")}</div><div class="queue-sub">{safe(mapping.get(cat, "Review recurring evidence and update the relevant playbook step."))}</div></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No recurring themes currently meet the update threshold.")


st.divider()
footer_left, footer_right = st.columns([1, 1])
with footer_left:
    st.caption("Independent portfolio prototype. Healthtech-1 is not affiliated with or responsible for this project.")
with footer_right:
    service_state = "connected" if drafting_available() else "local fallback"
    st.caption(f"Drafting service: {service_state} · No patient-level or clinical data")
