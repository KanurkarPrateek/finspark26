"""Fill the FinSpark template with Privileged-Access Sentinel content."""
from copy import deepcopy

from pptx import Presentation
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

TEMPLATE = "/Users/apple/Downloads/Finspark_Hackathon_Template.pptx"
OUT = "/Users/apple/personal-space/finspark26/FinSpark26_PrivilegedAccessSentinel.pptx"
ARCH = "/Users/apple/personal-space/finspark26/assets/architecture.png"
DASH = "/Users/apple/personal-space/finspark26/assets/dashboard.png"

prs = Presentation(TEMPLATE)


def set_content(shape, lines, size_pt=None):
    """Replace a text frame's content with `lines`, preserving the original run style."""
    tf = shape.text_frame
    tmpl = None
    if tf.paragraphs and tf.paragraphs[0].runs:
        tmpl = deepcopy(tf.paragraphs[0].runs[0]._r.get_or_add_rPr())
    tf.clear()
    for i, line in enumerate(lines):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        run = para.add_run()
        run.text = line
        if tmpl is not None:
            old = run._r.find(qn("a:rPr"))
            if old is not None:
                run._r.remove(old)
            run._r.insert(0, deepcopy(tmpl))
        if size_pt:
            run.font.size = Pt(size_pt)


def find(slide, startswith):
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(startswith):
            return sh
    return None


S = prs.slides

# ---- Slide 0: Title ----
title = find(S[0], "Presentation Template")
set_content(title, ["Privileged-Access Sentinel",
                    "Attack-Validated Insider Threat Detection for Banking"])
team = find(S[0], "Your Team Name")
set_content(team, [
    "Team Name:  ________________________",
    "Bio:  Security & pentest builders — banking cyber-resilience",
    "FinSpark'26  ·  Problem Statement 1  ·  Date: ____________",
], size_pt=16)

# ---- content slides: (start-of-title, new_title_or_None, [lines], size) ----
CONTENT = {
    1: ("Problem Statement?", "Problem Statement 1 — Privileged Access Misuse & Insider Threat", [
        "We chose PS1: Privileged Access Misuse & Insider Threat Detection.",
        "Insiders — employees, contractors, vendors, admins — already hold the keys. Acting",
        "maliciously, negligently, or under compromise, they bypass perimeter defences and",
        "hide inside legitimate activity, putting banking data and money at direct risk.",
        "",
        "Why we chose it: our team's edge is offensive security. We know exactly how insiders",
        "abuse privileged access — so we can detect it attack-first, not guess with a model.",
        "It is also the most defensible problem for a security team vs. a crowded fraud-ML field.",
    ], 15),
    2: (None, None, [
        "•  Privileged-session telemetry: logons (time / geo / device), commands, DB queries,",
        "    file access, privilege escalation, account & ACL changes.",
        "•  Read access to identity and asset inventory (users, roles, crown-jewel systems).",
        "•  Per-identity behavioural baselines — or the CMU CERT Insider Threat dataset",
        "    (r4.2 / r5.2) for training and validation.",
        "•  Deployment inline as a broker in the privileged-access path (SSH / RDP / DB proxy).",
        "•  Python 3.11+ runtime. Runs fully on-prem — no external SaaS required.",
    ], 15),
    3: (None, None, [
        "•  Backend:  Python · FastAPI · Uvicorn.",
        "•  Post-quantum crypto:  ML-KEM-768 (FIPS 203, kyber-py) for the credential vault;",
        "    ML-DSA-65 (FIPS 204, dilithium-py) for audit-log signatures; AES-256-GCM at rest.",
        "•  Detection:  explainable rule + statistical baselines (Isolation Forest / peer-group ML next).",
        "•  Threat model:  MITRE ATT&CK insider techniques (T1078, T1530, T1136, T1098…).",
        "•  Frontend:  vanilla HTML / CSS / JS SOC dashboard (zero build step).",
        "•  Validation dataset:  CMU CERT Insider Threat.",
    ], 15),
    4: (None, None, [
        "•  Architecture document (component diagram ①–⑧ + data flows).",
        "•  Coverage matrix — every PS1 expected-outcome & focus-area mapped to a component.",
        "•  Risk-scoring logic — signals, weights, ATT&CK mapping, and tier thresholds.",
        "•  Demo runbook — the 90-second malicious-insider scenario.",
        "•  README — run instructions and an honest 'what's real vs. next iteration' note.",
    ], 16),
    5: (None, None, [
        "Key differentiators",
        "•  Attack-validated — the same tool generates the attack AND proves detection (purple team).",
        "•  Explainable by design — every alert states WHY, mapped to a MITRE ATT&CK technique.",
        "•  Quantum-safe today — real ML-KEM-768 + ML-DSA-65 protect credentials and the audit trail.",
        "•  Inline enforcement — not just detect: step-up MFA, approval, or kill session in real time.",
        "",
        "Adoption plan",
        "•  Phase 1 — deploy read-only (observe + score) alongside existing PAM / SIEM.",
        "•  Phase 2 — enable graduated enforcement on crown-jewel systems.",
        "•  Phase 3 — integrate ITSM / SOAR and expand coverage bank-wide.",
    ], 14),
    6: (None, None, [
        "•  GitHub:  github.com/<your-team>/privileged-access-sentinel   (add link before submission)",
        "•  Architecture diagram — see the 'Architecture' slide.",
        "•  Live dashboard screenshots — see the 'Solution Screenshots' slide.",
        "•  Demo video:  <add link>",
        "•  Run locally:  ./run.sh  →  http://127.0.0.1:8000",
    ], 16),
    7: (None, None, [
        "•  Insider misuse is a leading cause of banking data breaches; RBI & IBA mandate strong",
        "    privileged-access control and tamper-proof audit trails.",
        "•  PAM + UEBA is a multi-billion-dollar market (CyberArk, Securonix) — but no offering is",
        "    India / RBI-mapped AND quantum-safe. That is our wedge.",
        "•  Directly supports the RBI Cyber Security Framework, audit-integrity requirements, and the",
        "    coming post-quantum cryptography migration.",
        "•  Applies to any regulated enterprise — banking, insurance, fintech, government.",
    ], 15),
    8: (None, None, [
        "•  Attack-first detection grounded in real attacker TTPs — built by pentesters, not only",
        "    data scientists — so alerts reflect how insiders actually operate.",
        "•  A purple-team harness ships with the product: detection is continuous and self-validating.",
        "•  Post-quantum credential vault + tamper-evident, PQC-signed audit log — resistant to",
        "    'harvest-now-decrypt-later' attacks.",
        "•  Explainable, ATT&CK-mapped risk scoring — analyst-trustable, low alert fatigue.",
        "•  Inline broker = observe AND enforce in one; most tools only alert after the fact.",
    ], 15),
    9: (None, None, [
        "•  A single SOC dashboard: a live risk gauge per session, colour-coded low → critical.",
        "•  Every alert is in plain English with its ATT&CK tag — analysts see WHY instantly.",
        "•  One-click attack demo, plus a manual probe to explore how behaviour maps to risk.",
        "•  Graduated, automatic responses cut analyst workload — the system acts, not just alerts.",
        "•  Verify / Tamper controls make audit-log integrity tangible in seconds.",
    ], 16),
    10: (None, None, [
        "•  Stateless event scoring — scales horizontally behind a queue (Kafka / Redis stream).",
        "•  Per-identity and peer-group baselines scale to thousands of privileged users.",
        "•  Broker deploys per region / data-centre; a central risk plane aggregates signals.",
        "•  Crown-jewel weighting prioritises the systems that matter under high session volume.",
        "•  Cloud-native and containerisable; on-prem option for data residency.",
    ], 16),
    11: (None, None, [
        "•  A single Python service + static dashboard — start with ./run.sh.",
        "•  No external SaaS dependency; runs fully on-prem so data never leaves the bank.",
        "•  Modular design — swap detection, crypto, or ingestion without touching the rest.",
        "•  Rules and baselines are transparent and tunable by the SOC team.",
        "•  PQC via pure-Python libraries — no native builds; standards-aligned (FIPS 203 / 204).",
    ], 16),
    12: (None, None, [
        "•  Zero credential exposure — secrets are brokered via injection; users never see them.",
        "•  Credentials at rest under AES-256-GCM, with the data-key wrapped by ML-KEM-768 (PQC).",
        "•  Tamper-evident audit log — hash-chained and ML-DSA-65 signed; any rewrite is detected.",
        "•  Least-privilege, risk-based access control with automatic session kill on critical risk.",
        "•  Aligned to the RBI Cyber Security Framework, MITRE ATT&CK, and NIST PQC standards.",
    ], 15),
    13: (None, None, [
        "End-to-end flow: users connect through the PAM broker (①), which injects credentials from",
        "the quantum-safe vault (②). Every action streams as telemetry (③) into the risk engine (④),",
        "which drives graduated response (⑤); all of it is recorded in a tamper-evident audit log (⑥)",
        "and surfaced on the SOC dashboard (⑦). The purple-team harness (⑧) attacks and validates it.",
    ], 12),
    14: (None, None, [
        "Live SOC dashboard during the insider attack: carol's session hits 100 CRITICAL and is KILLED,",
        "every step explained with its ATT&CK tag, the audit chain verifies (ML-DSA-65), and the",
        "stolen vault is ciphertext only (ML-KEM-768).   Demo video: <add link>   ·   GitHub: <add link>",
    ], 12),
}

for idx, (old_title, new_title, lines, size) in CONTENT.items():
    slide = S[idx]
    if old_title and new_title:
        t = find(slide, old_title)
        if t:
            set_content(t, [new_title])
    # guidance box = the body text box that isn't the title
    guides = [sh for sh in slide.shapes if sh.has_text_frame
              and sh.text_frame.text.strip()
              and not sh.text_frame.text.strip().startswith(("Problem", old_title or "\0"))]
    # pick the widest tall text box (the guidance placeholder)
    guide = None
    for sh in slide.shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().startswith(
            ("Mention", "List", "Add", "Explain", "Show", "Describe", "Highlight")):
            guide = sh
            break
    if guide:
        set_content(guide, lines, size)

# ---- images ----
S[13].shapes.add_picture(ARCH, Inches(1.36), Inches(2.30), width=Inches(10.6))
S[14].shapes.add_picture(DASH, Inches(3.30), Inches(2.00), width=Inches(6.7))

# ---- Slide 15: Thank You ----
g = find(S[15], "Add team member")
if g:
    set_content(g, [
        "Team: ____________________",
        "Contact: ____________________",
        "Thank you — Privileged-Access Sentinel · FinSpark'26 · PS1",
    ], 16)

prs.save(OUT)
print("saved:", OUT)
print("slides:", len(prs.slides))
