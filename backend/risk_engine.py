"""
④ Behavioural + Risk Engine
Explainable insider-threat scoring: per-identity baselines + ATT&CK-mapped rules.
Deliberately rules + statistics first (not a black box) so every alert can say WHY.
(Isolation Forest / peer-group ML plugs in here later — see evaluate().)
"""

# ⑤ Protected admin systems + their criticality
SYSTEMS = {
    "core-banking-admin": "crown-jewel",
    "payment-switch": "crown-jewel",
    "domain-controller": "crown-jewel",
    "db-prod": "crown-jewel",
    "db-replica": "high",
    "jump-host": "high",
    "db-test": "low",
}

# Seeded identity baselines ("normal" behaviour per privileged user)
IDENTITIES = {
    "alice": {
        "role": "DBA", "hours": [9, 18], "home_systems": ["db-prod", "db-replica"],
        "typical_max_rows": 500, "known_devices": ["alice-laptop"], "dormant": False,
    },
    "bob": {
        "role": "SysAdmin", "hours": [8, 19], "home_systems": ["domain-controller", "jump-host"],
        "typical_max_rows": 50, "known_devices": ["bob-ws"], "dormant": False,
    },
    "carol": {
        "role": "Contractor", "hours": [10, 17], "home_systems": ["db-test"],
        "typical_max_rows": 200, "known_devices": ["carol-vm"], "dormant": True,
    },
}

_DEFAULT_IDENTITY = {
    "role": "Unknown", "hours": [9, 18], "home_systems": [],
    "typical_max_rows": 100, "known_devices": [], "dormant": False,
}


def identity_of(user):
    return IDENTITIES.get(user, _DEFAULT_IDENTITY)


def criticality(system):
    return SYSTEMS.get(system, "medium")


def evaluate(event, identity):
    """Return a list of signals {points, reason, attck} for one privileged action."""
    signals = []
    etype = event["type"]
    system = event.get("target_system")
    crit = criticality(system) if system else "n/a"

    if etype == "login":
        hour = int(event.get("hour", 12))
        lo, hi = identity["hours"]
        if hour < lo or hour > hi:
            signals.append({"points": 15, "attck": "T1078 Valid Accounts",
                            "reason": f"Login at {hour:02d}:00 is outside normal hours ({lo:02d}:00–{hi:02d}:00)"})
        if event.get("device") not in identity["known_devices"]:
            signals.append({"points": 12, "attck": "T1078 Valid Accounts",
                            "reason": f"Login from unrecognised device '{event.get('device')}'"})
        if identity.get("dormant"):
            signals.append({"points": 8, "attck": "T1078 Valid Accounts",
                            "reason": "Dormant account reactivated after long inactivity"})

    elif etype == "query":
        if system not in identity["home_systems"]:
            signals.append({"points": 10, "attck": "T1078 Valid Accounts",
                            "reason": f"Accessed '{system}', outside {identity['role']}'s normal scope"})
        rows = int(event.get("rows", 0))
        if rows > identity["typical_max_rows"] * 5:
            mult = rows // max(identity["typical_max_rows"], 1)
            signals.append({"points": 15, "attck": "T1530 Data from Information Repositories",
                            "reason": f"Bulk read of {rows:,} rows (~{mult}x normal) — possible exfiltration"})

    elif etype == "create_user":
        signals.append({"points": 25, "attck": "T1136 Create Account",
                        "reason": f"Created new privileged account '{event.get('detail', '?')}' — possible backdoor"})

    elif etype == "grant":
        signals.append({"points": 20, "attck": "T1098 Account Manipulation",
                        "reason": f"Granted elevated privileges ({event.get('detail', '?')})"})

    elif etype == "config_change":
        signals.append({"points": 15, "attck": "T1562 Impair Defenses",
                        "reason": f"Modified critical configuration ({event.get('detail', '?')})"})

    # ⑤ Crown-jewel weighting: anything touching a critical admin system costs more.
    if crit == "crown-jewel" and signals:
        signals.append({"points": 5, "attck": "—",
                        "reason": f"Target '{system}' is a CROWN-JEWEL system — risk weighting increased"})

    return signals


def tier(score):
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def response_for(t):
    """⑤ Risk-based response: graduated controls by tier."""
    return {
        "low": {"action": "log", "label": "Logged — no action"},
        "medium": {"action": "step_up_mfa", "label": "Step-up MFA required"},
        "high": {"action": "require_approval", "label": "Manager approval required"},
        "critical": {"action": "kill_session", "label": "SESSION TERMINATED + credential rotation"},
    }[t]
