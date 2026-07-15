# Privileged-Access Sentinel — MVP

FinSpark'26 · **Problem Statement 1** (Privileged Access Misuse & Insider Threat Detection).
An *attack-validated* insider-threat control plane: privileged users connect **through** a PAM
broker, every action is risk-scored in real time against attacker TTPs, the system **acts** as risk
rises, and everything is recorded in a quantum-safe, tamper-evident audit log.

> This is a thin-but-complete MVP — every one of PS1's outcomes/focus areas is wired end-to-end so
> you can see the use case work. Depth (peer-group ML, real PQC, real SSH/DB proxying) comes next.

## Run

```bash
./run.sh                       # creates venv, installs deps, serves on :8000
# then open http://127.0.0.1:8000
```

Or manually:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd backend && uvicorn app:app --reload --port 8000
```

## The 90-second demo
1. Click **▶ Run Attack Scenario**. Watch contractor *carol* (dormant account) log in at 02:00 from
   an unknown host → bulk-read 50k customer rows → create a backdoor admin. The risk gauge climbs
   **medium → high → critical**, each step explained and ATT&CK-tagged.
2. At critical, the session is **killed**; the follow-up `GRANT` attempt is **BLOCKED**.
3. Click **🕵 Simulate vault theft** — the stolen credentials are ciphertext only.
4. Click **✔ Verify integrity** (intact) → **✎ Tamper** (attacker rewrites the backdoor alert) →
   **✔ Verify** again → **TAMPERING DETECTED**.
5. Use **🧪 Manual probe** to open a *normal* session (e.g. alice / db-prod / 14:00) and confirm it
   stays green — the baseline awareness is real, not theatre.

## How the pieces map to PS1 (component numbers match docs/architecture.md)
| # | File | Covers |
|---|---|---|
| ① PAM broker | `store.py` (`open_session`) | Protects admin systems · PAM |
| ② Quantum-safe vault | `vault.py` | QPC for credentials · Quantum-Safe Security |
| ③ Telemetry | `store.py` (`action`/`_score`) | Real-time |
| ④ Risk engine | `risk_engine.py` | Misuse detection · behaviour analytics · explainable AI |
| ⑤ Response plane | `risk_engine.response_for` + `store._enforce` | Risk-based access control / auth |
| ⑥ Tamper-evident audit | `audit.py` | QPC for sensitive artefacts |
| ⑦ Dashboard | `frontend/` | Explainability / visibility |
| ⑧ Attack harness | `attack_harness.py` | Differentiator — proves detection |

## Honest notes (what's real vs. stubbed in this MVP)
- **Real:** post-quantum crypto via **ML-KEM-768 (FIPS 203)** for the credential vault and
  **ML-DSA-65 (FIPS 204)** for audit-log signatures (`kyber-py` / `dilithium-py` — see
  `backend/pqc.py`; falls back to X25519/Ed25519 only if those libs are absent).
  AES-256-GCM credential encryption, hash-chained audit log (tamper truly detected),
  explainable rule+baseline scoring, live enforcement.
- **Stubbed / next iteration:** the broker simulates sessions rather than proxying real
  SSH/RDP/DB; scoring is rules+z-thresholds (Isolation Forest / peer-group ML plugs into
  `risk_engine.evaluate`). State is in-memory.
```
