import os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from server import app
c=TestClient(app)
def test_health():
 r=c.get("/api/health"); assert r.status_code==200 and r.json()["status"]=="ok"
def test_home():
 r=c.get("/"); assert r.status_code==200 and "THE SIGNAL" in r.text
def test_overview():
 d=c.get("/api/overview").json()
 assert len(d["accounts"])==12 and len(d["feedback"])>=10
 assert all(x["fictional"] for x in d["accounts"])
 assert d["priority"]
def test_decision():
 assert c.post("/api/decision",json={"lens":"rollout","choice":"b"}).json()["supported"]
 assert not c.post("/api/decision",json={"lens":"rollout","choice":"a"}).json()["supported"]
def test_ticket():
 d=c.post("/api/ticket",json={"feedback_id":"CALL-001"}).json()
 assert d["status"]=="Not submitted" and d["fictional"]
 assert d["generated_by"].startswith("Rules-based")
def test_bad_ticket():
 assert c.post("/api/ticket",json={"feedback_id":"../../etc"}).status_code==422
