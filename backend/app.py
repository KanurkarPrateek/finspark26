"""
FinSpark'26 · PS1 — Privileged-Access Sentinel (MVP)
FastAPI backend + static dashboard. Run:  ./run.sh   (or see README.md)
"""
import os

from attack_harness import SCENARIO
from fastapi import Body, FastAPI
from fastapi.staticfiles import StaticFiles
from store import Store

app = FastAPI(title="Privileged-Access Sentinel")
store = Store()

FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.get("/api/state")
def get_state():
    return store.state()


@app.post("/api/session/open")
def open_session(payload: dict = Body(...)):
    return store.open_session(
        user=payload["user"], system=payload["target_system"],
        device=payload.get("device", "unknown"), location=payload.get("location", "—"),
        hour=int(payload.get("hour", 12)),
    )


@app.post("/api/session/{sid}/action")
def session_action(sid: str, event: dict = Body(...)):
    return store.action(sid, event) or {"error": "no such session"}


@app.get("/api/attack/scenario")
def attack_scenario():
    return SCENARIO


@app.get("/api/vault/exfiltrate")
def vault_exfiltrate():
    return store.vault.exfiltrate()


@app.get("/api/audit")
def audit_records():
    return {"records": store.audit.records}


@app.post("/api/audit/verify")
def audit_verify():
    return store.audit.verify()


@app.post("/api/audit/tamper")
def audit_tamper():
    return store.audit.tamper()


@app.post("/api/reset")
def reset():
    store.reset()
    return {"ok": True}


# Serve the dashboard (index.html) and assets from /frontend at the root.
app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
