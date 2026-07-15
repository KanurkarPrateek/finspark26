# FinSpark'26 · PS1 — Privileged-Access Sentinel · Architecture

**One-liner:** An *attack-validated* insider-threat control plane for privileged access — nobody
touches credentials directly; a smart guard watches every privileged action, gets stricter as risk
rises, and keeps a tamper-proof, quantum-safe logbook.

## System diagram

```mermaid
flowchart TB
    USERS["👤 Privileged Users<br/>(admins, DBAs, contractors, vendors)"]

    subgraph CORE["Privileged-Access Sentinel"]
        BROKER["① PAM ACCESS BROKER (spine)<br/>users connect THROUGH it · injects creds · enforces live"]
        VAULT["② Quantum-Safe Vault<br/>creds: hybrid X25519 + ML-KEM-768 (FIPS 203)"]
        TELE["③ Telemetry Stream<br/>logons · commands · file access · privesc · ACL changes"]
        ENGINE["④ Behavioural + Risk Engine<br/>per-user & peer baselines · Isolation Forest (AI)<br/>ATT&amp;CK rules → risk score + 'why'"]
        RESP["⑤ Risk-Based Response Plane<br/>low→log · med→step-up MFA · high→approval · crit→kill/rotate/lock"]
        AUDIT["⑥ Tamper-Evident Audit Log<br/>hash-chained + ML-DSA signed (FIPS 204)"]
        SOC["⑦ SOC Dashboard<br/>live risk gauge · explainable alerts"]
    end

    SYSTEMS["🏦 Protected Admin Systems<br/>Core-Banking Admin · Domain Controller · DB Servers · Payment Switch"]
    HARNESS["⑧ Purple-Team Attack Harness<br/>replays insider TTPs → proves detection (attacks AND validates)"]

    USERS --> BROKER
    BROKER -- pulls credential --> VAULT
    BROKER -- brokered + recorded session --> SYSTEMS
    BROKER -- every action --> TELE
    TELE --> ENGINE
    ENGINE -- risk tier --> RESP
    RESP -- ENFORCE: step-up / kill / rotate --> BROKER
    RESP -- logs every decision --> AUDIT
    AUDIT --> SOC
    ENGINE --> SOC
    HARNESS -. simulated malicious insider .-> BROKER
```

## Rubric coverage (PS1)

| # | Component | Covers (Outcome / Focus Area) |
|---|---|---|
| ① | PAM Access Broker | Protects admin systems · Privileged Access Management |
| ② | Quantum-Safe Vault | QPC for credentials · Quantum-Safe Security |
| ③ | Telemetry Stream | Real-time detection |
| ④ | Behavioural + Risk Engine | Detects privileged misuse · Insider Threat Detection · AI behavioural analysis · Behaviour Analytics |
| ⑤ | Risk-Based Response Plane | Risk-based access control · Risk-Based Authentication |
| ⑥ | Tamper-Evident Audit Log | QPC for sensitive artefacts · Quantum-Safe Security |
| ⑦ | SOC Dashboard | Explainability / real-time visibility |
| ⑧ | Purple-Team Harness | Differentiator — proves every detection works |

## Demo flow (the winning 90 seconds)
1. Contractor logs in at 2 AM from a new device → impossible-travel flag.
2. Bulk-dumps the customer table → exfiltration flag.
3. Creates a hidden admin account → persistence flag.
4. Risk gauge climbs live → step-up MFA forced → session **killed**.
5. Attacker tries to edit the audit log to hide tracks → ML-DSA signature breaks → **tamper detected**.

*Validated against the CMU CERT Insider Threat dataset (r4.2/r5.2) + live attack injection.*
