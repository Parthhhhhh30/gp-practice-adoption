"""Practice / Signal | bounded FastAPI case-study backend.

Public GP Patient Survey data is fetched from the official source.
Customer accounts, adoption measures, feedback and issue drafts are ALWAYS simulated.
No patient-level information, external integrations or hiring decisions.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import math
import os
from datetime import datetime, timezone
from typing import Literal
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from data_pipeline import fetch_gpps
from rules import PracticeSignals, classify_practice, upsell_readiness, onboarding_state, adoption_health, recurring_issue_summary
from synthetic import customer_accounts, transcripts

ROOT=Path(__file__).parent
app=FastAPI(title="Practice / Signal",docs_url=None,redoc_url=None,openapi_url=None)
app.mount("/assets",StaticFiles(directory=str(ROOT/"assets")),name="assets")
NAMES=["Alderfield Surgery","Southbank Community Practice","Willow Grove Health Centre","Parkway Medical Practice","Birchfield Clinic","Harbour Street Practice","Elmfield Surgery","Briar Lane Medical Centre","Orchard View Practice","Eastmere Health","Meadowgate Medical","Station Road Surgery"]
# These names are invented; never join demo accounts to actual NHS practice identifiers.

def num(value,default=0):
    try:
        f=float(value)
        return round(f,1) if math.isfinite(f) else default
    except (TypeError,ValueError):return default

@lru_cache(maxsize=1)
def accounts():
    raw=customer_accounts(None)
    result=[]
    for i,row in raw.iterrows():
        d=row.to_dict()
        up,reasons=upsell_readiness(float(d["existing_adoption_ratio"]),bool(d["stakeholder_engaged"]),0,bool(d["critical_support_issue"]))
        result.append({
          "id":d["demo_customer_id"],"name":NAMES[i%len(NAMES)],"fictional":True,
          "product":d["current_product"],"goal":d["synthetic_goal"],
          "days_since_setup":int(d["days_since_setup"]),"activation":bool(d["activation_complete"]),
          "critical_issue":bool(d["critical_support_issue"]),
          "usage_ratio":num(d["usage_ratio"]), "existing_adoption":num(100*d["existing_adoption_ratio"]),
          "trend":num(d["four_week_change_pct"]), "weekly_requests":int(d["weekly_requests"]),
          "routed_pct":num(d["automated_or_routed_pct"]), "time_to_value":int(d["time_to_first_value_days"]),
          "time_saving":int(d["staff_minutes_saved_weekly"]),
          "onboarding":onboarding_state(int(d["days_since_setup"]),bool(d["activation_complete"]),bool(d["critical_support_issue"])),
          "health":adoption_health(bool(d["activation_complete"]),float(d["usage_ratio"]),float(d["four_week_change_pct"]),bool(d["critical_support_issue"])),
          "expansion":up,"expansion_reasons":reasons
        })
    return result

@lru_cache(maxsize=1)
def feedback():
    t=transcripts()
    return [{"id":str(r.call_id),"topic":str(r.category),"text":str(r.transcript),"fictional":True} for _,r in t.iterrows()]

@lru_cache(maxsize=1)
def public_source():
    # A six-second timeout keeps first-visit navigation responsive when
    # the upstream provider rejects automated serverless traffic.
    df=fetch_gpps(timeout=8)
    if df.empty:raise RuntimeError("No source records received")
    df=df.copy()
    # Data-source provenance intentionally excludes any generated customer account.
    for k in ["phone_easy_pct","website_easy_pct","app_easy_pct"]:
        df[k]=pd.to_numeric(df[k],errors="coerce")
    medians={k:num(df[k].median(),None) for k in ["phone_easy_pct","website_easy_pct","app_easy_pct"]}
    return df,medians

@app.get("/")
def home():
    return FileResponse(ROOT/"index.html",media_type="text/html")

@app.get("/workbench")
def workbench():
    return FileResponse(ROOT/"index.html",media_type="text/html")

@app.get("/api/health")
def health():
    return {"status":"ok","app":"Practice / Signal","data":"public GPPS on demand; customer records synthetic","mode":"free/read-only"}

@app.get("/api/overview")
def overview():
    a=accounts(); t=feedback()
    priority=[]
    for x in a:
        if x["onboarding"]=="Red" or x["health"]=="Red":
            tag="Resolve risk";rank=0
        elif x["expansion"]=="Ready for discovery":
            tag="Review opportunity";rank=1
        elif x["onboarding"]=="Amber" or x["health"]=="Amber":
            tag="Check activation";rank=2
        else:continue
        priority.append({"id":x["id"],"name":x["name"],"tag":tag,"rank":rank,"onboarding":x["onboarding"],"health":x["health"]})
    priority.sort(key=lambda x:(x["rank"],x["id"]))
    themes=[{"topic":k,"count":int(v)} for k,v in recurring_issue_summary([x["topic"] for x in t],3)]
    return {"fictional":True,"accounts":a,"priority":priority,"feedback":t,"themes":themes,
        "totals":{"accounts":len(a),"risk":sum(x["health"]=="Red" or x["onboarding"]=="Red" for x in a),
        "activated":sum(x["activation"] for x in a),"feedback":len(t),"themes":len(themes)},
        "provenance":"Fixed, deterministic synthetic fixtures; no clinical or customer records"}

@app.get("/api/practices")
def practices(q:str=Query("",max_length=90),signal:Literal["all","phone","digital","phone-digital"]="all",
              offset:int=Query(0,ge=0,le=10000),limit:int=Query(24,ge=1,le=100)):
    try:df,med=public_source()
    except Exception:
        return JSONResponse({"available":False,"records":[],"count":0,"total":None,"medians":None,"source":"GP Patient Survey 2026",
            "message":"The official public data feed is unavailable from this server session. No counts or percentages are imputed."},status_code=200)
    mask=pd.Series(True,index=df.index)
    if q:mask &= df["practice_name"].astype(str).str.contains(q,case=False,regex=False,na=False)|df["ics_name"].astype(str).str.contains(q,case=False,regex=False,na=False)
    if signal=="phone":mask &= (df["phone_easy_pct"] < med["phone_easy_pct"])
    elif signal=="digital":mask &= ((df["website_easy_pct"] < med["website_easy_pct"]) | (df["app_easy_pct"] < med["app_easy_pct"]))
    elif signal=="phone-digital":mask &= ((df["phone_easy_pct"] < med["phone_easy_pct"]) & (df["website_easy_pct"] >= med["website_easy_pct"]))
    sub=df.loc[mask]; result=[]
    for _,r in sub.iloc[offset:offset+limit].iterrows():
        result.append({"code":str(r["practice_code"]),"name":str(r["practice_name"]),"ics":str(r.get("ics_name","")),
          "phone":num(r.get("phone_easy_pct"),None),"website":num(r.get("website_easy_pct"),None),"app":num(r.get("app_easy_pct"),None)})
    return {"available":True,"records":result,"count":len(sub),"total":len(df),"medians":med,"source":"GP Patient Survey 2026 — practice-level public weighted results",
      "note":"Very easy + Fairly easy combined. Below-median tags are descriptive discovery signals, not product needs or customer status."}

class Decision(BaseModel):
    lens:Literal["public","rollout","feedback"]
    choice:Literal["a","b","c"]

@app.post("/api/decision")
def decide(body:Decision):
    right={"public":"b","rollout":"b","feedback":"b"}[body.lens]
    explanation={
      "public":"Ask how this practice handles access today. A public score cannot establish a supplier relationship, implementation requirement or sales opportunity.",
      "rollout":"Resolve critical support and activation issues before considering expansion. A healthy rollout requires evidence of actual usage, not just attendance.",
      "feedback":"Record exact reported behaviour, severity and an owner for review. A drafted product ticket is a proposal, not an authorised priority."
    }[body.lens]
    return {"supported":body.choice==right,"reason":explanation if body.choice==right else
      "This action makes a claim or change that the available evidence does not justify. Investigate first, then assign a human owner.",
      "recorded":False,"fictional":True}

class DraftTicket(BaseModel):
    feedback_id:str=Field(pattern=r"^CALL-\d{3}$",max_length=8)

@app.post("/api/ticket")
def ticket(body:DraftTicket):
    row=next((x for x in feedback() if x["id"]==body.feedback_id),None)
    if row is None:raise HTTPException(404,"Fictional feedback record not found")
    # Strictly deterministic, no implied AI inference or external side effects.
    return {"type":"DRAFT / HUMAN REVIEW ONLY","reference":row["id"],
        "category":row["topic"],"source":row["text"],"proposed_owner":"Customer operations / confirm internally",
        "next_step":"Confirm observed behaviour, reproduce with the customer, assess severity, then agree an owner and acceptance criteria.",
        "status":"Not submitted","fictional":True,"generated_by":"Rules-based template; no AI request"}
