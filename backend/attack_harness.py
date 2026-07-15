"""
⑧ Purple-Team Attack Harness  (the differentiator)
The scripted insider scenario. The frontend replays these real backend
endpoints with delays so judges WATCH the risk climb — same tool attacks AND validates.
"""

SCENARIO = {
    "title": "Malicious insider — contractor 'carol' goes rogue",
    "open": {
        "user": "carol", "target_system": "db-prod",
        "device": "unknown-host", "location": "TOR exit (RU)", "hour": 2,
    },
    "steps": [
        {"label": "Bulk-read the customer table",
         "event": {"type": "query", "target_system": "db-prod", "rows": 50000}},
        {"label": "Create a hidden admin account",
         "event": {"type": "create_user", "target_system": "db-prod", "detail": "sys_backup_adm (backdoor)"}},
        {"label": "Grant ALL privileges to the backdoor (should be BLOCKED)",
         "event": {"type": "grant", "target_system": "db-prod", "detail": "GRANT ALL TO sys_backup_adm"}},
    ],
}
