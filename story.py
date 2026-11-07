"""Interactive introduction to the GP operations prototype.

Public access observations are kept separate from synthetic accounts and training cases.
The choice interaction is explanatory only: no customer records are mutated.
"""
from __future__ import annotations
import html
import pandas as pd
import streamlit as st
from rules import recurring_issue_summary
from synthetic import transcripts


STORY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root{--story-ink:#122d35;--story-deep:#0c2730;--story-cream:#fcf5e9;--story-paper:#f7f5ee;--story-coral:#d87955;--story-amber:#f6bc72;--story-aqua:#9ac5c2}
.stApp{background:#f7f5ee;color:#122d35}
.block-container{max-width:1370px;padding-top:1.1rem}
.stApp h1,.stApp h2,.stApp h3,.story-wrap{font-family:'Manrope','DM Sans',sans-serif}
.story-wrap{color:var(--story-ink);line-height:1.5}
.story-wrap *{box-sizing:border-box}
.story-hero{position:relative;isolation:isolate;overflow:hidden;border-radius:20px;background:var(--story-deep);color:var(--story-cream);padding:clamp(30px,5vw,72px) clamp(24px,5vw,68px) 44px;display:grid;grid-template-columns:1.18fr .82fr;gap:35px;min-height:468px}
.story-hero:before{content:'';position:absolute;inset:0;pointer-events:none;background:radial-gradient(circle at 74% 40%,rgba(107,175,166,.16),transparent 42%),linear-gradient(120deg,transparent 58%,rgba(255,255,255,.025) 58.15%,transparent 58.3%)}
.story-hero>div{position:relative;z-index:1}
.story-kicker{display:flex;gap:12px;align-items:center;font-size:11px;letter-spacing:.18em;font-weight:800;color:var(--story-amber);text-transform:uppercase}
.story-kicker:before{content:'';width:8px;height:8px;border-radius:50%;background:var(--story-coral);box-shadow:0 0 0 5px rgba(216,121,85,.15)}
.story-hero h1{font-family:'Manrope',sans-serif;color:var(--story-cream);font-size:clamp(35px,4.4vw,62px);line-height:1.09;letter-spacing:-.055em;font-weight:800;margin:26px 0 20px}
.story-hero h1 em{color:var(--story-amber);font-style:normal}
.story-intro{color:#d5e3df;font-size:clamp(15px,1.35vw,18px);max-width:580px;line-height:1.7;margin:0}
.story-hero-bottom{margin-top:40px;display:flex;flex-wrap:wrap;gap:12px;align-items:center}
.story-outline{display:inline-block;padding:8px 13px;border:1px solid rgba(255,255,255,.26);border-radius:100px;color:#e5e8dc;font-size:11px;letter-spacing:.04em}
.story-diagram{position:relative;min-height:325px;display:flex;align-items:center;justify-content:center}
.story-orbit{position:absolute;width:310px;height:310px;border:1px solid rgba(197,226,219,.2);border-radius:50%;transform:rotate(-18deg)}
.story-orbit:before{content:'';position:absolute;inset:27px;border:1px dashed rgba(197,226,219,.21);border-radius:50%}
.story-diagram-card{position:absolute;background:#f5efe2;border:1px solid #c6dad4;color:var(--story-ink);padding:18px 19px;box-shadow:0 22px 65px rgba(0,0,0,.24);border-radius:12px;width:235px;transform:rotate(-5deg)}
.story-diagram-card.one{top:23%;right:27%;transform:rotate(-8deg)}
.story-diagram-card.two{top:48%;right:5%;transform:rotate(7deg);background:#b2d5ca}
.story-diagram-card.three{bottom:0;left:1%;transform:rotate(-4deg);width:213px;background:#f7bc77}
.story-diagram-card small{font-size:10px;letter-spacing:.16em;font-weight:800;display:block;margin-bottom:11px;opacity:.75}
.story-diagram-card b{font-size:16px;letter-spacing:-.03em;display:block}
.story-diagram-card span{font-size:11px;color:#36545a;display:block;margin-top:7px}
.story-section{margin-top:60px}
.story-index{font-size:11px;letter-spacing:.18em;font-weight:800;color:#ad5e45}
.story-title{font-family:'Manrope',sans-serif;font-size:clamp(29px,3.2vw,43px);letter-spacing:-.05em;line-height:1.15;margin:13px 0;color:var(--story-ink);font-weight:800}
.story-why{font-size:15px;max-width:800px;color:#526467;line-height:1.7;margin:0 0 22px}
.story-metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:17px}
.story-metric{border:1px solid #d7dacf;background:#fffdf6;border-radius:13px;padding:20px}
.story-metric strong{font-size:clamp(25px,3vw,40px);font-weight:800;letter-spacing:-.055em;display:block;line-height:1.2}
.story-metric span{font-size:12px;color:#62716d;display:block;margin-top:7px}
.story-metric small{display:block;font-size:10px;letter-spacing:.1em;color:#a25a43;font-weight:800;margin-bottom:8px}
.story-choice{background:#fffdf6;border:1px solid #d6d9cd;border-radius:16px;padding:26px 28px;margin-top:12px}
.story-choice-kicker{color:#a45941;font-weight:800;font-size:11px;letter-spacing:.12em}
.story-case-head{font-weight:800;font-size:clamp(20px,2.5vw,30px);letter-spacing:-.035em;margin:9px 0;color:#17343b}
.story-case-copy{color:#465e62;line-height:1.68;font-size:15px}
.story-case-foot{border-top:1px solid #e3e6db;padding-top:13px;margin-top:18px;color:#51645c;font-size:12px}
.story-result{padding:14px 18px;background:#eaf4e9;color:#245642;border-left:4px solid #4a9772;border-radius:8px;margin-top:12px;font-size:14px;line-height:1.55}
.story-result.no{background:#fff0e9;color:#894935;border-color:#c56b4e}
.story-navcard{border:1px solid #d5dad0;background:#fffdf7;padding:21px;border-radius:13px;min-height:155px}
.story-navnum{color:#a75d44;font-size:11px;letter-spacing:.13em;font-weight:800}
.story-navhead{font-size:18px;letter-spacing:-.035em;font-weight:800;margin:14px 0 6px}
.story-navtext{font-size:13px;color:#526568;line-height:1.55}
.story-boundary{background:#e7e9dc;border-radius:16px;padding:24px;margin-top:40px;color:#1b353b}
.story-boundary h3{margin:0 0 10px;font-size:20px;color:#17343b}
.story-boundary p{font-size:13px;line-height:1.7;color:#475b5e;margin:0}
.story-note{font-size:12px;color:#667774;margin:12px 0 0}
.story-footer{margin:48px 0 10px;padding:22px 0;border-top:1px solid #cbd4cb;font-size:12px;color:#60716e}
div.stButton>button{border:1px solid #46615e;background:#12333a;color:white;border-radius:8px;min-height:44px;font-family:'DM Sans',sans-serif;font-weight:700}
div.stButton>button:hover{border-color:#c67254;background:#274c51;color:white}
[data-testid="stSegmentedControl"]{margin-bottom:10px}
[data-testid="stSegmentedControl"] button{border:1px solid #d6d9cc!important;background:#fffdf6!important;border-radius:8px!important}
[data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#193840!important;color:white!important}
@media(max-width:920px){.story-hero{grid-template-columns:1fr;min-height:0;padding:32px 23px 31px}.story-diagram{height:230px;min-height:230px}.story-orbit{width:225px;height:225px}.story-diagram-card{width:185px;padding:12px}.story-diagram-card.one{top:1%;right:36%}.story-diagram-card.two{top:27%;right:4%}.story-diagram-card.three{bottom:0;left:4%}.story-metrics{grid-template-columns:1fr}.story-section{margin-top:42px}.story-choice{padding:17px}}
@media(prefers-reduced-motion:no-preference){.story-diagram-card{transition:transform .2s ease}.story-diagram-card:hover{transform:rotate(0deg) translateY(-4px)}}
</style>
"""


LENSES = ("Public access", "Rollout risk", "Customer feedback")

def decision_feedback(lens: str, selected: str) -> tuple[bool,str]:
    """Explain a human decision; do not treat it as an executed customer action."""
    checks = {
        "Public access": ("Check the practice's workflow before treating the access result as a product opportunity",
            "Correct. Survey measures are useful discovery context, not proof that a practice uses or needs a particular supplier."),
        "Rollout risk": ("Resolve the open support and activation blocker before discussing expansion",
            "Correct. A simulated customer with a critical issue needs a named owner and resolution before an upsell conversation."),
        "Customer feedback": ("Record the exact issue, evidence and owner for human review",
            "Correct. A draft ticket should preserve the reported friction; neither the AI nor the prototype silently assigns product priority."),
    }
    if lens not in checks:
        raise ValueError("Unknown scenario")
    expected, explanation = checks[lens]
    return selected == expected, explanation if selected == expected else "That would go beyond the available evidence. Keep the original observation separate from any assumption, then check the affected workflow with a human owner."


def story_stats(public: pd.DataFrame, accounts: pd.DataFrame) -> tuple[str,str,str]:
    """Do not turn missing public data into a fictional numeric benchmark."""
    count = f"{len(public):,}" if not public.empty else "—"
    phone = pd.to_numeric(public.get("phone_easy_pct",pd.Series(dtype=float)),errors="coerce")
    phone_median = f"{phone.dropna().median():.0f}%" if not phone.dropna().empty else "—"
    demo = f"{len(accounts):02d}" if not accounts.empty else "—"
    return count, phone_median, demo


def _safe(x) -> str:
    return html.escape(str(x if x is not None else ""))


def render_story(public: pd.DataFrame, accounts: pd.DataFrame, go_to) -> None:
    st.markdown(STORY_CSS,unsafe_allow_html=True)
    st.markdown("""<div class="story-wrap"><div class="story-hero">
      <div><div class="story-kicker">GP WORKFLOWS / AN INTERACTIVE CASE</div>
      <h1>THE DATA<br>IS THERE.<br><em>WHAT NEXT?</em></h1>
      <p class="story-intro">A GP practice can have a digital access problem, an onboarding problem or a workflow nobody wants to use. Those are not the same thing. Explore how an operations team might separate the evidence, choose the next action and check whether anything improved.</p>
      <div class="story-hero-bottom"><span class="story-outline">PUBLIC SURVEY EVIDENCE</span><span class="story-outline">SIMULATED CUSTOMER WORKFLOWS</span><span class="story-outline">HUMAN DECISIONS</span></div></div>
      <div class="story-diagram" aria-label="Illustration of the evidence-to-decision process"><div class="story-orbit"></div>
        <div class="story-diagram-card one"><small>01 / OBSERVE</small><b>Access signal</b><span>Measured. Not a sales score.</span></div>
        <div class="story-diagram-card two"><small>02 / INVESTIGATE</small><b>Operational friction</b><span>What is blocking adoption?</span></div>
        <div class="story-diagram-card three"><small>03 / FOLLOW THROUGH</small><b>Human action</b><span>Check the outcome, don't assume it.</span></div>
      </div></div></div>""", unsafe_allow_html=True)
    c1,c2=st.columns([.37,.63])
    with c1:
        st.button("Explore real practice data →",key="story-hero-practices",on_click=go_to,args=("Practices",),use_container_width=True)
    with c2:
        st.button("Open the operator workbench →",key="story-hero-workbench",on_click=go_to,args=("Today",),use_container_width=True)

    n,phone,demo=story_stats(public,accounts)
    st.markdown('<div class="story-wrap"><section class="story-section"><div class="story-index">01 / SEPARATE THE EVIDENCE</div><h2 class="story-title">Real context. Simulated decisions.</h2><p class="story-why">Start with the 2026 GP Patient Survey, then switch to a clearly fictional customer portfolio to see how an operator would respond. A real practice name never means a real customer relationship.</p><div class="story-metrics"><div class="story-metric"><small>PUBLIC / GP PATIENT SURVEY</small><strong>'+_safe(n)+'</strong><span>practice rows loaded from source</span></div><div class="story-metric"><small>PUBLIC / OBSERVED DISTRIBUTION</small><strong>'+_safe(phone)+'</strong><span>median practice-level “easy by phone” result</span></div><div class="story-metric"><small>SIMULATED / ACCOUNT PORTFOLIO</small><strong>'+_safe(demo)+'</strong><span>fictional customer workflows for demonstration</span></div></div></section></div>',unsafe_allow_html=True)
    if public.empty:
        st.caption("Public survey data unavailable. No median or practice count is invented.")

    st.markdown('<div class="story-wrap"><section class="story-section"><div class="story-index">02 / TAKE A DECISION</div><h2 class="story-title">Do not mistake a signal for a conclusion.</h2><p class="story-why">Three short cases expose different kinds of evidence. Choose a next action, then inspect the real workspace that supports it. This interaction explains the judgement—it does not modify customer records.</p></section></div>',unsafe_allow_html=True)
    lens=st.segmented_control("Choose a scenario",LENSES,default="Public access",key="story-lens")
    lens=lens or "Public access"
    specs={
        "Public access":{
            "title":"A low phone-access score appears in the public survey.",
            "desc":"The published survey provides a practice-level access observation. It does not reveal why people reported difficulty, the practice's software supplier or whether anyone has asked for help.",
            "source":"REAL SURVEY / SIMULATED DECISION",
            "options":["Automatically class the practice as a customer in need of an upgrade","Check the practice's workflow before treating the access result as a product opportunity","Assume the NHS App is the cause"],
            "button":"Open real practice explorer →","route":"Practices",
            "foot":"Survey ‘easy’ combines the published Very easy and Fairly easy responses, not a proprietary opportunity score."},
        "Rollout risk":{
            "title":"A fictional customer has a critical support issue.",
            "desc":"The prototype's rule engine marks accounts at risk when activation, support or usage signals warrant attention. Expanding an unresolved customer account would be premature.",
            "source":"FICTIONAL CUSTOMER / REAL RULE ENGINE",
            "options":["Propose a second product immediately","Resolve the open support and activation blocker before discussing expansion","Treat a low usage result as proof of a bad product"],
            "button":"Investigate simulated account →","route":"Accounts",
            "foot":"Account status and usage are seeded fictional records, not clinical or supplier performance data."},
        "Customer feedback":{
            "title":"Practice staff keep raising the same onboarding issue.",
            "desc":"In fictional feedback notes, staff struggle with handovers and unclear routing. The responsible action is to preserve what was said, examine repetition and propose a reviewable next step.",
            "source":"FICTIONAL CALL NOTES / REVIEWABLE ACTION",
            "options":["Ask an AI assistant to set the product backlog priority automatically","Record the exact issue, evidence and owner for human review","Count a drafted response as the issue being resolved"],
            "button":"Examine feedback evidence →","route":"Feedback",
            "foot":"Drafting can help write up an issue; a human must verify and decide what happens next."}
    }
    spec=specs[lens]
    st.markdown('<div class="story-wrap"><div class="story-choice"><div class="story-choice-kicker">'+_safe(spec["source"])+'</div><div class="story-case-head">'+_safe(spec["title"])+'</div><p class="story-case-copy">'+_safe(spec["desc"])+'</p></div></div>',unsafe_allow_html=True)
    choice=st.radio("What would you do next?",spec["options"],index=None,key="story-answer-"+lens)
    if choice is not None:
        correct,reason=decision_feedback(lens,choice)
        st.markdown('<div class="story-wrap"><div class="story-result'+('' if correct else ' no')+'"><strong>'+('SUPPORTED NEXT STEP' if correct else 'EVIDENCE CHECK NEEDED')+'</strong><br>'+_safe(reason)+'</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="story-wrap"><p class="story-note">'+_safe(spec["foot"])+'</p></div>',unsafe_allow_html=True)
    st.button(spec["button"],key="story-go-"+spec["route"],on_click=go_to,args=(spec["route"],),use_container_width=True)

    st.markdown('<div class="story-wrap"><section class="story-section"><div class="story-index">03 / FOLLOW THE WORK</div><h2 class="story-title">From an observation to a repeatable process.</h2><p class="story-why">The following workspaces are functional parts of the prototype. Each handles a different stage of a customer-operations decision; the underlying customer outcomes remain explicitly simulated.</p></section></div>',unsafe_allow_html=True)
    modules=[
        ("01","TODAY","Sort the work","A priority queue for account risk and follow-up.","Today"),
        ("02","PRACTICES","Find the signal","Explore sourced GPPS access observations.","Practices"),
        ("03","ACCOUNTS","Test readiness","Review activation and support blockers.","Accounts"),
        ("04","ADOPTION","Check the result","Look at fictional usage and value evidence.","Adoption"),
        ("05","FEEDBACK","Preserve the voice","Turn recurring friction into reviewable issues.","Feedback"),
        ("06","PLAYBOOK","Make it repeatable","Translate observed issues into process changes.","Playbook")
    ]
    for chunk in (modules[:3],modules[3:]):
        cols=st.columns(3,gap="medium")
        for col,(num,label,heading,description,route) in zip(cols,chunk):
            with col:
                st.markdown('<div class="story-wrap"><div class="story-navcard"><div class="story-navnum">'+num+' / '+label+'</div><div class="story-navhead">'+heading+'</div><div class="story-navtext">'+description+'</div></div></div>',unsafe_allow_html=True)
                st.button("Explore "+label.lower()+" ↗",key="story-module-"+route,on_click=go_to,args=(route,),use_container_width=True)

    st.markdown("""<div class="story-wrap"><div class="story-boundary"><h3>What is actually real here?</h3>
    <p><strong>Real:</strong> public GP Patient Survey context, transparent classification rules, Streamlit software, and optional AI-assisted drafting when a server-side key is configured.
    <br><strong>Fictional:</strong> customer accounts, product subscriptions, onboarding records, usage, time savings, call transcripts, and all customer outcomes.
    <br><strong>Never:</strong> patient-level information, confirmed commercial relationships, automated outreach or real NHS system integration.</p>
    </div><div class="story-footer">INDEPENDENT GP OPERATIONS EXERCISE · A demonstration of operational reasoning, not a deployed clinical product or customer case study.</div></div>""",unsafe_allow_html=True)
