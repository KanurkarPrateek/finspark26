"""
In-memory state + the orchestration that ties every piece together:
① PAM broker  →  ③ telemetry  →  ④ risk engine  →  ⑤ response  →  ⑥ audit log
"""
from audit import AuditLog
from risk_engine import (IDENTITIES, SYSTEMS, criticality, evaluate,
                         identity_of, response_for, tier)
from vault import QuantumSafeVault


class Store:
    def __init__(self):
        self.reset()

    def reset(self):
        self.vault = QuantumSafeVault()      # ②
        self.audit = AuditLog()              # ⑥
        self.sessions = {}                   # id -> session
        self.feed = []                       # newest-first event feed for the UI
        self._seq = 0

    # ① PAM broker: user connects THROUGH us; we inject the credential.
    def open_session(self, user, system, device, location, hour):
        ident = identity_of(user)
        sid = f"S-{self._seq:03d}"
        self._seq += 1
        cred = self.vault.broker(system)
        session = {
            "id": sid, "user": user, "role": ident["role"], "system": system,
            "criticality": criticality(system), "device": device, "location": location,
            "opened_hour": hour, "status": "active", "risk": 0, "tier": "low",
            "reasons": [], "actions": [], "credential": cred,
        }
        self.sessions[sid] = session
        self.audit.append("session_open", {
            "sid": sid, "user": user, "system": system, "device": device,
            "location": location, "hour": hour,
            "credential_brokered": cred["username"] if cred else None,
        })
        # Treat the login itself as the first scored action.
        self._score(session, {"type": "login", "hour": hour, "device": device,
                              "target_system": system, "location": location})
        return session

    def action(self, sid, event):
        session = self.sessions.get(sid)
        if not session:
            return None
        if session["status"] == "killed":
            # ⑤ enforcement proof: further actions are blocked.
            self.feed.insert(0, {
                "sid": sid, "user": session["user"], "type": event["type"],
                "system": event.get("target_system", session["system"]),
                "detail": event.get("detail"), "rows": event.get("rows"),
                "delta": 0, "signals": [], "risk": session["risk"], "tier": "critical",
                "response": "BLOCKED — session already terminated", "blocked": True,
            })
            return session
        event.setdefault("target_system", session["system"])
        self._score(session, event)
        return session

    # ④ score → record → ⑤ enforce → ⑥ audit
    def _score(self, session, event):
        ident = identity_of(session["user"])
        signals = evaluate(event, ident)
        delta = sum(s["points"] for s in signals)
        session["risk"] = min(100, session["risk"] + delta)
        session["tier"] = tier(session["risk"])

        for s in signals:
            entry = {"reason": s["reason"], "attck": s["attck"]}
            if entry not in session["reasons"]:
                session["reasons"].append(entry)

        ev = {
            "sid": session["id"], "user": session["user"], "type": event["type"],
            "system": event.get("target_system"), "detail": event.get("detail"),
            "rows": event.get("rows"), "delta": delta, "signals": signals,
            "risk": session["risk"], "tier": session["tier"],
        }
        self.audit.append("event", {
            "sid": session["id"], "type": event["type"],
            "system": event.get("target_system"), "rows": event.get("rows"),
            "detail": event.get("detail"), "delta": delta,
        })

        resp = response_for(session["tier"])
        self._enforce(session, resp)
        ev["response"] = resp["label"]
        self.feed.insert(0, ev)

    def _enforce(self, session, resp):
        action = resp["action"]
        if action == "kill_session":
            session["status"] = "killed"
        elif action == "require_approval" and session["status"] in ("active", "mfa_required"):
            session["status"] = "approval_required"
        elif action == "step_up_mfa" and session["status"] == "active":
            session["status"] = "mfa_required"
        session["actions"].append({"tier": session["tier"], "label": resp["label"]})

        backdoor = any("backdoor" in r["reason"] for r in session["reasons"])
        self.audit.append("risk_decision", {
            "sid": session["id"], "risk": session["risk"], "tier": session["tier"],
            "action": action, "backdoor": backdoor,
            "reasons": [r["reason"] for r in session["reasons"]],
        })

    def state(self):
        return {
            "identities": IDENTITIES,
            "systems": SYSTEMS,
            "sessions": list(self.sessions.values()),
            "feed": self.feed[:40],
            "audit_count": len(self.audit.records),
            "vault_systems": self.vault.systems(),
            "crypto": {
                "kem": self.vault.scheme, "kem_active": self.vault.pqc_active,
                "sig": self.audit.scheme, "sig_active": self.audit.pqc_active,
            },
        }
