"""
Build a designed FinSpark'26 PPTX (Privileged-Access Sentinel) — real product POV.
Card-based layout, kickers, accent bars, navy callouts. 16 slides, 16:9.
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

# palette
NAVY   = RGBColor(0x08, 0x24, 0x3A)
NAVY2  = RGBColor(0x0F, 0x3A, 0x52)
INK    = RGBColor(0x0E, 0x22, 0x33)
SLATE  = RGBColor(0x5B, 0x6B, 0x7B)
TEAL   = RGBColor(0x21, 0x58, 0x68)   # Bank of Maharashtra brand teal
GOLD   = RGBColor(0xFF, 0xD4, 0x49)   # Bank of Maharashtra brand gold
GOLDT  = RGBColor(0x8A, 0x6D, 0x12)
CORAL  = RGBColor(0xD1, 0x50, 0x2F)
MIST   = RGBColor(0xF4, 0xF7, 0xF9)
LINE   = RGBColor(0xE2, 0xE9, 0xEE)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xCF, 0xE0, 0xEC)
FONT   = "Arial"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]

LX, RX = 0.85, 12.48          # content left / right
CW = RX - LX                  # content width

# Bank of Maharashtra logo, lifted from the FinSpark'26 hackathon template.
BOM_LOGO = "/Users/apple/personal-space/finspark26/assets/bom-logo.png"
LOGO_W, LOGO_H = 1.92, 0.225  # native aspect, same size the template uses

def slide():
    return prs.slides.add_slide(BLANK)

def logo(s):
    """Bank of Maharashtra mark, top-right, flush to the content grid."""
    s.shapes.add_picture(BOM_LOGO, Inches(RX - LOGO_W), Inches(0.34),
                         Inches(LOGO_W), Inches(LOGO_H))

def _noline(shape):
    shape.line.fill.background()

def rect(s, x, y, w, h, fill, line=None, lw=1.0, rounded=True, radius=0.09):
    shp = s.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        try: shp.adjustments[0] = radius
        except Exception: pass
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid(); shp.fill.fore_color.rgb = fill
    if line is None:
        _noline(shp)
    else:
        shp.line.color.rgb = line; shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    return shp

def tb(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    box = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    return tf

def para(tf, first=False, space_after=4, space_before=0, align=PP_ALIGN.LEFT, line=1.0):
    p = tf.paragraphs[0] if first and not tf.paragraphs[0].runs else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after); p.space_before = Pt(space_before)
    try: p.line_spacing = line
    except Exception: pass
    return p

def run(p, text, size, color, bold=False, italic=False, font=FONT):
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.italic = italic
    r.font.name = font; r.font.color.rgb = color
    return r

# --- reusable slide furniture ---
def kicker(s, text):
    tf = tb(s, LX, 0.6, CW, 0.3)
    run(para(tf, True), text.upper(), 12, TEAL, bold=True)

def title(s, text, size=29):
    tf = tb(s, LX, 0.92, CW, 1.0)
    for i, ln in enumerate(text.split("\n")):
        run(para(tf, i == 0, space_after=0, line=1.08), ln, size, NAVY, bold=True)

def accent(s, y=1.98):
    rect(s, LX, y, 0.62, 0.09, GOLD, radius=0.5)

def footer(s, num):
    tf = tb(s, LX, 7.02, 8, 0.3)
    run(para(tf, True), "PRIVILEGED-ACCESS SENTINEL · FinSpark'26", 9, RGBColor(0x9A,0xA9,0xB4))
    tf2 = tb(s, RX-1, 7.02, 1, 0.3)
    run(para(tf2, True, align=PP_ALIGN.RIGHT), num, 9, RGBColor(0x9A,0xA9,0xB4), bold=True)

def head(s, kick, ttl, num, tsize=29):
    kicker(s, kick); title(s, ttl, tsize); accent(s); footer(s, num); logo(s)

def card(s, x, y, w, h, navy=False, border=None, lw=1.0):
    return rect(s, x, y, w, h, NAVY if navy else MIST,
                line=(border if border else (None if navy else LINE)),
                lw=lw, radius=0.06)

def card_text(s, x, y, w, h, h3, body, navy=False, h3size=15, bsize=12.5):
    tf = tb(s, x+0.22, y+0.2, w-0.44, h-0.4)
    run(para(tf, True, space_after=6), h3, h3size, WHITE if navy else NAVY, bold=True)
    for i, b in enumerate(body):
        run(para(tf, space_after=3, line=1.18), b, bsize, LIGHT if navy else SLATE)
    return tf

def bullets(s, x, y, w, h, items, navy=False, size=14.5, gap=8):
    tf = tb(s, x, y, w, h)
    for i, it in enumerate(items):
        p = para(tf, i == 0, space_after=gap, line=1.16)
        run(p, "▪  ", size, TEAL, bold=True)
        # allow **bold** segments
        for seg, b in _segs(it):
            run(p, seg, size, LIGHT if navy else INK, bold=b)
    return tf

def _segs(text):
    out = []
    for i, part in enumerate(text.split("**")):
        if part:
            out.append((part, i % 2 == 1))
    return out

def pill(s, x, y, text, w=None, tint=TEAL):
    w = w or (0.16 + 0.085*len(text))
    r = rect(s, x, y, w, 0.32, RGBColor(0xE6,0xEE,0xF2), radius=0.5)
    tf = tb(s, x, y+0.02, w, 0.28, anchor=MSO_ANCHOR.MIDDLE)
    run(para(tf, True, align=PP_ALIGN.CENTER), text, 10.5, tint, bold=True)
    return w

# ================= SLIDES =================

# 0 — COVER
s = slide()
rect(s, -0.1, -0.1, 13.6, 7.7, NAVY, rounded=False)
rect(s, 8.6, -0.1, 5.0, 7.7, NAVY2, rounded=False)   # subtle two-tone band
rect(s, 8.6, -0.1, 0.03, 7.7, NAVY, rounded=False)
mark = rect(s, LX, 2.05, 0.62, 0.62, GOLD, radius=0.28)
tfm = tb(s, LX, 2.09, 0.62, 0.56, anchor=MSO_ANCHOR.MIDDLE)
run(para(tfm, True, align=PP_ALIGN.CENTER), "🛡", 24, NAVY, bold=True)
tfn = tb(s, LX+0.8, 2.13, 8, 0.45, anchor=MSO_ANCHOR.MIDDLE)
run(para(tfn, True), "PRIVILEGED-ACCESS SENTINEL", 17, WHITE, bold=True)
tft = tb(s, LX, 2.95, 10.5, 1.7)
run(para(tft, True, line=1.04), "Catch the insider", 58, WHITE, bold=True)
run(para(tft, line=1.04), "before the breach.", 58, WHITE, bold=True)
tfg = tb(s, LX, 4.95, 9.6, 1.2)
p = para(tfg, True, line=1.4)
run(p, "An ", 18, LIGHT); run(p, "attack-validated", 18, WHITE, bold=True)
run(p, " insider-threat control plane for banking — it watches every privileged action, scores risk in real time, stops misuse automatically, and secures it with post-quantum cryptography.", 18, LIGHT)
tfmeta = tb(s, LX, 6.7, 11, 0.3)
run(para(tfmeta, True), "Team HappenedBefore   ·   FinSpark'26   ·   Problem Statement 1 — Privileged Access Misuse & Insider Threat", 12.5, RGBColor(0x8F,0xB0,0xC7))
tfsnip = tb(s, RX-4, 0.62, 4, 0.3)
run(para(tfsnip, True, align=PP_ALIGN.RIGHT), "FINSPARK'26 · PS1", 11, RGBColor(0x7C,0xA0,0xBA), bold=True)
logo(s)

# 1 — PROBLEM STATEMENT
s = slide(); head(s, "The Problem · PS1", "Insiders already hold the keys.\nNormal security never sees them.", "02")
gw = (CW - 2*0.25)/3
cards = [
    ("The threat is inside", ["Employees, contractors, vendors and admins — acting maliciously, negligently, or under compromise — already have privileged access to core banking systems."]),
    ("Perimeter defences miss it", ["They use legitimate credentials. Firewalls, EDR and login-time MFA don't flag a trusted user quietly abusing the access they already hold."]),
    ("Lost in the noise", ["One malicious action hides among thousands of normal privileged operations. By the time anyone notices, the data — or the money — is gone."]),
]
for i,(h3,b) in enumerate(cards):
    x = LX + i*(gw+0.25); card(s, x, 2.3, gw, 1.9); card_text(s, x, 2.3, gw, 1.9, h3, b)
card(s, LX, 4.5, CW, 1.75, navy=True)
tf = tb(s, LX+0.28, 4.72, CW-0.56, 1.4)
run(para(tf, True, space_after=8), "Why we chose PS1", 16, WHITE, bold=True)
p = para(tf, line=1.35)
run(p, "Our team's edge is ", 15, LIGHT); run(p, "offensive security", 15, WHITE, bold=True)
run(p, ". We know exactly how insiders abuse privileged access — so we detect it ", 15, LIGHT)
run(p, "attack-first", 15, WHITE, bold=True)
run(p, ", grounded in real techniques, not guessed at with a black-box model.", 15, LIGHT)
pill(s, RX-3.3, 4.74, "Attack-first advantage", w=2.9, tint=GOLDT)

# 2 — PRE-REQUISITES
s = slide(); head(s, "Pre-Requisites", "What the product needs to run.", "03")
bullets(s, LX, 2.35, 6.6, 4, [
    "**Privileged-session telemetry** — logons (time / geo / device), commands, DB queries, file access, privilege escalation, account & ACL changes.",
    "**Identity & asset inventory** — privileged users, roles, and which systems are crown-jewels.",
    "**Behavioural baselines** — per-identity history, or the CMU CERT Insider Threat dataset for training & validation.",
    "**Inline deployment** — a broker in the privileged-access path (SSH / RDP / DB proxy).",
], size=15, gap=13)
cx = LX + 7.1
card(s, cx, 2.35, CW-7.1, 3.5, navy=True)
tf = tb(s, cx+0.28, 2.6, CW-7.1-0.56, 3)
run(para(tf, True, space_after=10), "Deployment assumptions", 15, WHITE, bold=True)
for it in ["Python 3.11+ runtime.", "Runs fully **on-prem** — no external SaaS.", "**Data never leaves the bank.**", "Sits alongside existing PAM / SIEM."]:
    p = para(tf, space_after=9, line=1.2); run(p, "✓  ", 13, GOLD, bold=True)
    for seg,b in _segs(it): run(p, seg, 14, LIGHT, bold=b)

# 3 — TOOLS
s = slide(); head(s, "Tools & Resources", "Built on a lean, standards-aligned stack.", "04")
gw = (CW - 2*0.22)/3; gh = 1.75
tools = [
    ("Backend", "Python · FastAPI", "Async event pipeline + static SOC dashboard.", None),
    ("Post-Quantum", "ML-KEM-768 · ML-DSA-65", "Real NIST FIPS 203 / 204 + AES-256-GCM.", TEAL),
    ("Detection", "Explainable scoring", "Rule + statistical baselines; peer-group ML next.", None),
    ("Threat model", "MITRE ATT&CK", "Insider TTPs — T1078, T1530, T1136, T1098.", None),
    ("Frontend", "SOC dashboard", "Live risk gauges, explainable feed, verify/tamper.", None),
    ("Dataset", "CMU CERT", "Insider Threat benchmark for validation.", None),
]
for i,(pl,h3,b,bd) in enumerate(tools):
    r,c = divmod(i,3); x = LX + c*(gw+0.22); y = 2.3 + r*(gh+0.22)
    card(s, x, y, gw, gh, border=(TEAL if bd else None), lw=2 if bd else 1)
    tf = tb(s, x+0.2, y+0.18, gw-0.4, gh-0.36)
    pill_w = 0.16+0.075*len(pl)
    # inline pill as colored small text
    run(para(tf, True, space_after=6), pl.upper(), 10, TEAL, bold=True)
    run(para(tf, space_after=4), h3, 15, NAVY, bold=True)
    run(para(tf, line=1.15), b, 12, SLATE)

# 4 — SUPPORTING DOCS
s = slide(); head(s, "Supporting Functional Documents", "Everything documented — to build it and defend it.", "05")
bullets(s, LX, 2.35, 5.6, 3, [
    "**Architecture document** — component diagram ①–⑧ with data flows.",
    "**Coverage matrix** — every PS1 outcome & focus-area mapped to a component.",
    "**Risk-scoring logic** — signals, weights, ATT&CK mapping, thresholds.",
], size=15, gap=13)
bullets(s, LX+6.0, 2.35, 5.6, 3, [
    "**Demo runbook** — the 90-second malicious-insider scenario.",
    "**README** — run instructions + honest 'real vs. next iteration' note.",
    "**Working MVP** — end-to-end, runnable with a single command.",
], size=15, gap=13)
card(s, LX, 5.05, CW, 1.2, navy=True)
tf = tb(s, LX+0.28, 5.25, CW-0.56, 0.9, anchor=MSO_ANCHOR.MIDDLE)
p = para(tf, True, line=1.3)
run(p, "Every claim is demonstrable.", 16, WHITE, bold=True)
run(p, "  The MVP runs the attack, the detection, the enforcement and the tamper-proof audit live — nothing here is a mock-up.", 15, LIGHT)

# 5 — DIFFERENTIATORS & ADOPTION
s = slide(); head(s, "Key Differentiators & Adoption Plan", "Why we win — and how a bank rolls it out.", "06")
gw = (CW - 3*0.2)/4
diffs = [
    ("Attack-validated", "A built-in purple-team harness generates the attack and proves detection caught it."),
    ("Explainable", "Every alert states why, mapped to a MITRE ATT&CK technique — no black box."),
    ("Quantum-safe", "Credentials & audit trail protected by real ML-KEM-768 + ML-DSA-65 today."),
    ("Inline enforcement", "Not just detect — step-up MFA, approve, or kill the session in real time."),
]
for i,(h3,b) in enumerate(diffs):
    x = LX + i*(gw+0.2); card(s, x, 2.3, gw, 1.75); card_text(s, x, 2.3, gw, 1.75, h3, [b], bsize=11.5)
# phases
tfp = tb(s, LX, 4.35, 6, 0.3); run(para(tfp, True), "ADOPTION PLAN", 11, GOLDT, bold=True)
pw = (CW - 2*0.2)/3
phases = [("PHASE 1 · 0–3 mo","Observe","Deploy read-only beside PAM / SIEM — score risk, prove signal."),
          ("PHASE 2 · 3–9 mo","Enforce","Turn on graduated response on crown-jewel systems."),
          ("PHASE 3 · 9 mo+","Integrate","Wire into ITSM / SOAR; expand coverage bank-wide.")]
for i,(no,h4,b) in enumerate(phases):
    x = LX + i*(pw+0.2); card(s, x, 4.7, pw, 1.5)
    tf = tb(s, x+0.2, 4.85, pw-0.4, 1.25)
    run(para(tf, True, space_after=4), no, 10.5, TEAL, bold=True)
    run(para(tf, space_after=4), h4, 15, NAVY, bold=True)
    run(para(tf, line=1.15), b, 12, SLATE)

# 6 — PRODUCT & ACCESS
s = slide(); head(s, "Product & Repository", "A runnable MVP, one command away.", "07")
bullets(s, LX, 2.4, 6.4, 3, [
    "**GitHub** — github.com/<team>/privileged-access-sentinel  (add link).",
    "**Demo video** — <add link>.",
    "**Architecture & screenshots** — see the following slides.",
], size=15, gap=13)
cx = LX+6.9; card(s, cx, 2.4, CW-6.9, 3.4, navy=True)
tf = tb(s, cx+0.3, 2.62, CW-6.9-0.6, 0.5)
run(para(tf, True), "Run it in 30 seconds", 15, WHITE, bold=True)
codebg = rect(s, cx+0.3, 3.2, CW-6.9-0.6, 1.4, RGBColor(0x04,0x12,0x1D), line=RGBColor(0x1B,0x4A,0x63), radius=0.06)
tfc = tb(s, cx+0.5, 3.38, CW-6.9-1.0, 1.1)
run(para(tfc, True, space_after=4), "$ ./run.sh", 13, RGBColor(0x8F,0xE3,0xD4), font="Courier New")
run(para(tfc, space_after=4), "→ http://127.0.0.1:8000", 12, RGBColor(0x7C,0xA0,0xBA), font="Courier New")
run(para(tfc), "# click ▶ Run Attack Scenario", 12, RGBColor(0x7C,0xA0,0xBA), font="Courier New")
tfn = tb(s, cx+0.3, 4.75, CW-6.9-0.6, 0.6)
run(para(tfn, True, line=1.2), "FastAPI backend + static dashboard · no external services.", 12, RGBColor(0x8F,0xB0,0xC7))

# 7 — BUSINESS POTENTIAL
s = slide(); head(s, "Business Potential & Relevance", "A real market — with a regulator tailwind.", "08")
bullets(s, LX, 2.4, 6.3, 3.5, [
    "Insider misuse is a **leading cause of banking data breaches**; RBI & IBA mandate strong privileged-access control and tamper-proof audit.",
    "PAM + UEBA is a **multi-billion-dollar market** (CyberArk, Securonix) — but nothing is India / RBI-mapped **and** quantum-safe. That's our wedge.",
    "Applies to any regulated enterprise — **banking, insurance, fintech, government.**",
], size=15, gap=15)
cx = LX+6.8; card(s, cx, 2.4, CW-6.8, 3.3, navy=True)
tf = tb(s, cx+0.3, 2.62, CW-6.8-0.6, 3)
run(para(tf, True, space_after=10), "Regulator tailwind", 15, WHITE, bold=True)
for it in ["RBI Cyber Security Framework — access control & audit integrity.","Mandated tamper-proof audit trails.","The coming **post-quantum migration** — we're already there."]:
    p = para(tf, space_after=9, line=1.2); run(p, "✓  ", 13, GOLD, bold=True)
    for seg,b in _segs(it): run(p, seg, 14, LIGHT, bold=b)

# 8 — UNIQUENESS
s = slide(); head(s, "Uniqueness of Approach", "What makes this different.", "09")
bullets(s, LX, 2.4, 6.3, 3.5, [
    "**Attack-first, not model-first** — detection grounded in real attacker TTPs, built by pentesters who know how insiders operate.",
    "**Self-validating** — a purple-team harness ships with the product; detection is continuously proven, not assumed.",
    "**Quantum-safe custody** — post-quantum vault + PQC-signed audit resist harvest-now-decrypt-later.",
    "**Observe AND enforce** — one inline broker; most tools only alert after the fact.",
], size=15, gap=12)
cx = LX+6.8; card(s, cx, 2.4, CW-6.8, 3.3, navy=True)
tf = tb(s, cx+0.3, 2.75, CW-6.8-0.6, 2.7, anchor=MSO_ANCHOR.MIDDLE)
run(para(tf, True, space_after=10), "The one-line pitch", 15, WHITE, bold=True)
p = para(tf, line=1.4)
run(p, "“We didn't train a model and hope. We ", 17, LIGHT)
run(p, "attacked it, then proved it holds", 17, WHITE, bold=True)
run(p, " — and locked it with post-quantum crypto.”", 17, LIGHT)

# 9 — USER EXPERIENCE
s = slide(); head(s, "User Experience", "One screen. Every alert explains itself.", "10")
gw = (CW-2*0.25)/3
ux = [("Live risk, at a glance","A colour-coded gauge per session — green → amber → red — that climbs as an insider crosses the line."),
      ("Plain-English 'why'","Each alert reads like a sentence, tagged with its ATT&CK technique. Analysts trust it instantly."),
      ("Acts for you","Graduated automatic responses cut analyst workload — the system steps up, blocks, or kills."),
      ("One-click demo","Replay a full insider attack, or use the manual probe to explore how behaviour maps to risk."),
      ("Tangible integrity","Verify / Tamper controls make the audit-log guarantee something you can see in seconds."),
      ("Zero training","A SOC analyst reads the dashboard with no manual — the design carries the meaning.")]
for i,(h3,b) in enumerate(ux):
    r,c = divmod(i,3); x = LX+c*(gw+0.25); y=2.3+r*(1.75+0.22)
    card(s, x, y, gw, 1.75); card_text(s, x, y, gw, 1.75, h3, [b], bsize=11.5)

# 10 — SCALABILITY
s = slide(); head(s, "Scalability", "From one data-centre to a national bank.", "11")
bullets(s, LX, 2.4, 6.3, 3.5, [
    "**Stateless scoring** — scales horizontally behind a queue (Kafka / Redis stream).",
    "**Per-identity + peer-group baselines** handle thousands of privileged users.",
    "**Broker per region / data-centre**; a central risk plane aggregates signals.",
    "**Crown-jewel weighting** prioritises what matters under high session volume.",
], size=15, gap=13)
cx=LX+6.8; card(s, cx, 2.4, CW-6.8, 3.0)
tf = tb(s, cx+0.28, 2.62, CW-6.8-0.56, 2.6)
run(para(tf, True, space_after=8), "Deployment shape", 15, NAVY, bold=True)
run(para(tf, line=1.3, space_after=12), "Cloud-native and containerisable, with an on-prem option for data residency. Brokers scale out per site; the scoring plane scales out per load — no shared bottleneck.", 13, SLATE)
pill(s, cx+0.28, 4.55, "Horizontally scalable", w=2.3)
pill(s, cx+2.7, 4.55, "On-prem or cloud", w=1.9, tint=GOLDT)

# 11 — DEPLOYMENT
s = slide(); head(s, "Ease of Deployment & Maintenance", "Easy to deploy, easy to trust.", "12")
bullets(s, LX, 2.4, 5.6, 3, [
    "**Single service + static dashboard** — start with ./run.sh.",
    "**No external SaaS** — runs fully on-prem; data stays in the bank.",
    "**Modular** — swap detection, crypto or ingestion independently.",
], size=15, gap=13)
bullets(s, LX+6.0, 2.4, 5.6, 3, [
    "**Transparent rules** — baselines & thresholds readable and tunable by the SOC.",
    "**Pure-Python PQC** — no native builds; FIPS 203 / 204 aligned.",
    "**Low footprint** — containerises to a small, auditable image.",
], size=15, gap=13)
card(s, LX, 5.1, CW, 1.15, navy=True)
tf = tb(s, LX+0.28, 5.3, CW-0.56, 0.85, anchor=MSO_ANCHOR.MIDDLE)
p = para(tf, True, line=1.3)
run(p, "Because the logic is rules + explainable statistics", 15, WHITE, bold=True)
run(p, " rather than an opaque model, the SOC can read it, trust it, and tune it — which is what gets a tool adopted inside a bank.", 14, LIGHT)

# 12 — SECURITY
s = slide(); head(s, "Security Considerations", "Security is the product — including post-quantum.", "13")
bullets(s, LX, 2.4, 6.3, 3.5, [
    "**Zero credential exposure** — secrets brokered via injection; users never see them.",
    "**Least-privilege, risk-based access** — automatic session kill on critical risk.",
    "**Aligned to standards** — RBI Cyber Security Framework, MITRE ATT&CK, NIST PQC.",
], size=15, gap=14)
cx=LX+6.8; card(s, cx, 2.4, CW-6.8, 3.3, navy=True)
tf = tb(s, cx+0.3, 2.62, CW-6.8-0.6, 3)
run(para(tf, True, space_after=10), "Post-quantum by design", 15, WHITE, bold=True)
for it in ["Credentials: AES-256-GCM, data-key wrapped by **ML-KEM-768** (FIPS 203).","Audit log: hash-chained & **ML-DSA-65** signed (FIPS 204) — any rewrite detected.","Resists **harvest-now-decrypt-later.**"]:
    p = para(tf, space_after=10, line=1.25); run(p, "✓  ", 13, GOLD, bold=True)
    for seg,b in _segs(it): run(p, seg, 14, LIGHT, bold=b)

# 13 — ARCHITECTURE (image)
s = slide(); head(s, "Architecture", "How it all fits together.", "14")
from PIL import Image as _Img
aw, ah = _Img.open("/Users/apple/personal-space/finspark26/assets/architecture.png").size
maxw, maxh = 11.4, 4.35
scale = min(maxw/(aw/96*1.0*0+aw), 1)  # placeholder
# fit by aspect
ar = aw/ah
w = maxw; h = w/ar
if h > maxh: h = maxh; w = h*ar
s.shapes.add_picture("/Users/apple/personal-space/finspark26/assets/architecture.png",
                     Inches(LX + (CW-w)/2), Inches(2.25), Inches(w), Inches(h))
tfc = tb(s, LX, 6.55, CW, 0.4)
run(para(tfc, True, align=PP_ALIGN.CENTER), "Broker ① · quantum-safe vault ② · telemetry ③ · risk engine ④ · response ⑤ · tamper-evident audit ⑥ · SOC dashboard ⑦ · purple-team harness ⑧.", 11, SLATE)

# 14 — SCREENSHOTS (image)
s = slide(); head(s, "Solution Screenshots · MVP", "The working MVP, live.", "15")
dw, dh = _Img.open("/Users/apple/personal-space/finspark26/assets/dashboard.png").size
ar = dw/dh; h = 4.3; w = h*ar
if w > 11.4: w = 11.4; h = w/ar
s.shapes.add_picture("/Users/apple/personal-space/finspark26/assets/dashboard.png",
                     Inches(LX + (CW-w)/2), Inches(2.2), Inches(w), Inches(h))
tfc = tb(s, LX, 6.55, CW, 0.4)
run(para(tfc, True, align=PP_ALIGN.CENTER), "Insider attack, live: contractor carol hits 100 CRITICAL → session KILLED, each step ATT&CK-tagged, audit chain verified (ML-DSA-65), vault ciphertext-only (ML-KEM-768).", 11, SLATE)

# 15 — CLOSE
s = slide()
rect(s, -0.1, -0.1, 13.6, 7.7, NAVY, rounded=False)
rect(s, 8.6, -0.1, 5.0, 7.7, NAVY2, rounded=False)
rect(s, 8.6, -0.1, 0.03, 7.7, NAVY, rounded=False)
mark = rect(s, LX, 2.2, 0.62, 0.62, GOLD, radius=0.28)
tfm = tb(s, LX, 2.24, 0.62, 0.56, anchor=MSO_ANCHOR.MIDDLE)
run(para(tfm, True, align=PP_ALIGN.CENTER), "🛡", 24, NAVY, bold=True)
tfn = tb(s, LX+0.8, 2.28, 8, 0.45, anchor=MSO_ANCHOR.MIDDLE)
run(para(tfn, True), "PRIVILEGED-ACCESS SENTINEL", 17, WHITE, bold=True)
tft = tb(s, LX, 3.2, 11, 1.6)
run(para(tft, True, line=1.05), "Catch the insider.", 52, WHITE, bold=True)
run(para(tft, line=1.05), "Prove it. Every time.", 52, WHITE, bold=True)
tfg = tb(s, LX, 5.1, 10, 0.8)
run(para(tfg, True, line=1.4), "Attack-validated detection · inline enforcement · post-quantum custody.", 17, LIGHT)
tfmeta = tb(s, LX, 6.7, 11, 0.3)
run(para(tfmeta, True), "Team HappenedBefore   ·   prateekkanurkar@gmail.com   ·   FinSpark'26 · PS1", 12.5, RGBColor(0x8F,0xB0,0xC7))
tfsnip = tb(s, RX-2, 0.62, 2, 0.3)
run(para(tfsnip, True, align=PP_ALIGN.RIGHT), "THANK YOU", 11, RGBColor(0x7C,0xA0,0xBA), bold=True)
logo(s)

out = "/Users/apple/personal-space/finspark26/FinSpark26_PrivilegedAccessSentinel.pptx"
prs.save(out)
print("saved", out, "slides", len(prs.slides))
