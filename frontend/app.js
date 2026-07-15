const $ = (id) => document.getElementById(id);
const api = (path, opts) => fetch("/api" + path, opts).then((r) => r.json());
const post = (path, body) =>
  api(path, { method: "POST", headers: { "Content-Type": "application/json" },
              body: body ? JSON.stringify(body) : undefined });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let LATEST_SID = null;

// ---------- rendering ----------
function tierClass(t) { return "t-" + t; }

function renderIdentities(ids) {
  $("identities").innerHTML = Object.entries(ids).map(([u, d]) => `
    <div class="idrow">
      <div><b>${u}</b> <span class="meta">${d.role}</span>
        <div class="meta">hours ${d.hours[0]}:00–${d.hours[1]}:00 · devices: ${d.known_devices.join(", ") || "—"}${d.dormant ? " · ⚠ dormant" : ""}</div>
      </div>
    </div>`).join("");
}

function renderSystems(sys) {
  $("systems").innerHTML = Object.entries(sys).map(([s, c]) => `
    <div class="sysrow"><span>${s}</span><span class="tag ${c.replace("-", "")}">${c}</span></div>`).join("");
}

function renderSessions(sessions) {
  const el = $("sessions");
  if (!sessions.length) { el.className = "empty"; el.textContent = "No active sessions yet."; return; }
  el.className = "";
  el.innerHTML = sessions.slice().reverse().map((s) => `
    <div class="session">
      <div class="session-head">
        <b>${s.user}</b> <span class="muted">${s.role} → ${s.system}</span>
        <span class="status ${s.status}">${s.status.replace("_", " ")}</span>
      </div>
      <div class="session-meta">${s.id} · device ${s.device} · ${s.location} · ${String(s.opened_hour).padStart(2,"0")}:00
        ${s.credential ? ` · 🔑 injected ${s.credential.username} (${s.credential.masked})` : ""}</div>
      <div style="display:flex;align-items:center;gap:8px">
        <div class="gauge" style="flex:1"><div class="bg-${s.tier}" style="width:${s.risk}%"></div></div>
        <span class="risknum ${tierClass(s.tier)}">${s.risk} ${s.tier.toUpperCase()}</span>
      </div>
      <div class="reasons">${s.reasons.map((r) => `<div class="r">• ${r.reason}<span class="attck">[${r.attck}]</span></div>`).join("")}</div>
    </div>`).join("");
}

function renderFeed(feed) {
  const el = $("feed");
  if (!feed.length) { el.className = "empty"; el.textContent = "Waiting for privileged activity…"; return; }
  el.className = "";
  el.innerHTML = feed.map((f) => `
    <div class="fitem ${f.blocked ? "blocked" : ""}">
      <div class="top">
        <span><b>${f.user}</b> · ${f.type}${f.system ? " @ " + f.system : ""}${f.rows ? " · " + f.rows.toLocaleString() + " rows" : ""}${f.detail ? " · " + f.detail : ""}</span>
        <span class="delta ${tierClass(f.tier)}">${f.delta > 0 ? "+" + f.delta : "0"} → ${f.risk}</span>
      </div>
      ${(f.signals || []).filter(s => s.points !== 0).map((s) => `<div class="sig">↳ ${s.reason} <span class="attck">[${s.attck}]</span></div>`).join("")}
      <div class="resp">⚙ ${f.response}</div>
    </div>`).join("");
}

async function refresh() {
  const st = await api("/state");
  renderIdentities(st.identities);
  renderSystems(st.systems);
  renderSessions(st.sessions);
  renderFeed(st.feed);
  $("audit-count").textContent = st.audit_count;
  if (st.crypto) {
    const kem = $("kem-status"), sig = $("sig-status");
    kem.textContent = st.crypto.kem;
    kem.className = "crypto-badge " + (st.crypto.kem_active ? "pqc" : "classical");
    sig.textContent = st.crypto.sig;
    sig.className = "crypto-badge " + (st.crypto.sig_active ? "pqc" : "classical");
  }
  // populate manual selects once
  if (!$("m-user").options.length) {
    $("m-user").innerHTML = Object.keys(st.identities).map((u) => `<option>${u}</option>`).join("");
    $("m-system").innerHTML = Object.keys(st.systems).map((s) => `<option>${s}</option>`).join("");
  }
}

// ---------- attack scenario (⑧) ----------
function narrate(step, text, done = false) {
  const el = $("narration");
  el.classList.remove("hidden");
  el.className = "narration" + (done ? " done" : "");
  el.innerHTML = `<div class="n-step">${step}</div>${text}`;
}

async function runAttack() {
  $("run-attack").disabled = true;
  await post("/reset");
  const sc = await api("/attack/scenario");

  narrate("Attack · logging in", `<b>${sc.open.user}</b> opens a session on
    <code>${sc.open.target_system}</code> at ${String(sc.open.hour).padStart(2, "0")}:00
    from <code>${sc.open.device}</code> · ${sc.open.location}. Watch the risk gauge.`);
  const s = await post("/session/open", sc.open);
  LATEST_SID = s.id;
  await refresh();

  const n = sc.steps.length;
  for (let i = 0; i < n; i++) {
    await sleep(1800);
    narrate(`Attack · step ${i + 1} of ${n}`, sc.steps[i].label);
    await post(`/session/${LATEST_SID}/action`, sc.steps[i].event);
    await refresh();
  }

  await sleep(600);
  const final = (await api("/state")).sessions.find((x) => x.id === LATEST_SID);
  if (final) {
    narrate("Attack complete — caught",
      `Risk reached <b>${final.risk} ${final.tier.toUpperCase()}</b> and the session is
       <b>${final.status.replace("_", " ").toUpperCase()}</b>. The last privilege-grant was refused.
       Every step above says <b>why</b>, mapped to MITRE ATT&CK.`, true);
  }
  $("run-attack").disabled = false;
  document.dispatchEvent(new CustomEvent("attack-complete"));
}

// ---------- manual probe ----------
async function manualOpen() {
  const s = await post("/session/open", {
    user: $("m-user").value, target_system: $("m-system").value,
    device: $("m-device").value, hour: Number($("m-hour").value), location: "manual",
  });
  LATEST_SID = s.id;
  await refresh();
}
async function manualAction() {
  if (!LATEST_SID) return alert("Open a session first.");
  const type = $("m-action").value;
  const ev = { type };
  if (type === "query") ev.rows = Number($("m-rows").value);
  if ($("m-detail").value) ev.detail = $("m-detail").value;
  await post(`/session/${LATEST_SID}/action`, ev);
  await refresh();
}

// ---------- audit (⑥) ----------
async function showAudit() {
  const { records } = await api("/audit");
  $("audit-log").textContent = records.map((r) =>
    `#${r.seq} ${r.type}  ${r.hash.slice(0, 12)}…\n   ${JSON.stringify(r.payload)}`).join("\n");
}
async function verify() {
  const v = await post("/audit/verify");
  $("audit-result").innerHTML = v.valid
    ? `<div class="banner ok">✔ Chain intact — ${v.count} records verified.</div>`
    : `<div class="banner bad">✘ TAMPERING DETECTED at record #${v.broken_at} (${v.record_type}) — ${v.reason}</div>`;
  await showAudit();
}
async function tamper() {
  const t = await post("/audit/tamper");
  $("audit-result").innerHTML = `<div class="banner bad">🕵 Attacker altered record #${t.tampered_seq}: ${t.note}. Now click Verify…</div>`;
  await showAudit();
}

// ---------- vault (②) ----------
async function exfil() {
  const v = await api("/vault/exfiltrate");
  const out = $("exfil-out");
  out.classList.remove("hidden");
  out.textContent =
    `Stolen vault (protected by ${v.scheme}) — useless without the decapsulation key:\n\n` +
    `wrapped data-key: ${v.wrapped_data_key_b64.slice(0, 64)}…\n\n` +
    Object.entries(v.credentials).map(([s, b]) => `${s}: ${b.username}\n  ${b.ciphertext_b64}`).join("\n");
}

// ---------- guided demo ----------
// Each step: what it explains, what to spotlight, and (optionally) the action
// the visitor must take before Next unlocks — so the story can't get out of order.
const TOUR = [
  {
    title: "A bank's admins already hold the keys",
    body: `Admins, DBAs, contractors and vendors can legitimately reach the systems that
           hold your money and customer data. If one of them goes rogue, a firewall sees
           nothing wrong — they're using <b>valid credentials</b>.<br><br>
           This tool sits <b>in the path</b>: every privileged session is brokered, scored
           live, and stopped automatically when it turns malicious. Takes about 90 seconds.`,
  },
  {
    title: "Meet the insiders",
    body: `Three privileged identities. Each has a <b>learned baseline</b> — normal working
           hours and known devices — so "unusual" means unusual <i>for that person</i>.<br><br>
           Note <b>carol</b>: a contractor, flagged <b>⚠ dormant</b>. She's about to go rogue.`,
    target: "card-identities",
  },
  {
    title: "The crown jewels",
    body: `The systems worth protecting. <code>db-prod</code> and <code>core-banking-admin</code>
           are <b>crown-jewel</b> tier — touching them scores higher than touching a test box.
           Nobody reaches these except <b>through</b> the broker.`,
    target: "card-systems",
  },
  {
    title: "Run the attack",
    body: `Now the part nobody else can demo: the tool <b>generates the attack itself</b>.<br><br>
           carol logs into <code>db-prod</code> at <b>02:00</b> from an unknown host over TOR,
           bulk-reads <b>50,000 customer rows</b>, plants a backdoor admin, then tries to grant
           it everything. Watch the gauge climb.`,
    target: "card-sessions",
    doText: "Click ▶ Run Attack Scenario (top right)",
    spotlightBtn: "run-attack",
    waitFor: "attack-complete",
  },
  {
    title: "It acted — it didn't just alert",
    body: `Risk climbed <b>medium → high → critical</b> as evidence stacked up. At critical the
           session was <b>KILLED</b> and the final <code>GRANT</code> was <b>BLOCKED</b>.<br><br>
           That's the difference between a dashboard and a <b>control plane</b>: detection in the
           access path can stop the breach, not just describe it afterwards.`,
    target: "card-sessions",
  },
  {
    title: "Every alert explains itself",
    body: `No black box. Each line states <b>why</b> it scored — dormant account, odd hour,
           unknown device, bulk read, crown-jewel target — and maps to a
           <b>MITRE ATT&CK</b> technique.<br><br>
           That's what makes it defensible to an auditor, and what an ML anomaly score can't give you.`,
    target: "card-feed",
  },
  {
    title: "Steal the vault — it's worthless",
    body: `Admins never see raw passwords; the broker injects them from an encrypted vault.<br><br>
           So assume the attacker exfiltrates the vault file itself. The data key is wrapped with
           <b>ML-KEM-768</b> — real NIST post-quantum crypto (FIPS 203). What they get is
           <b>ciphertext only</b>, and it stays safe even against a future quantum attacker.`,
    target: "card-vault",
    doText: "Click 🕵 Simulate vault theft",
    spotlightBtn: "exfil",
    waitFor: "click:exfil",
  },
  {
    title: "Now watch them cover their tracks",
    body: `A smart insider edits the logs. This audit log is <b>hash-chained</b> and signed with
           <b>ML-DSA-65</b> (FIPS 204), so any edit breaks the chain.<br><br>
           Do all three in order — <b>Verify</b> (intact) → <b>Tamper</b> (rewrite the backdoor
           alert) → <b>Verify</b> again. The forgery is caught and pinpointed to the exact record.`,
    target: "card-audit",
    doText: "Verify → Tamper → Verify again",
    spotlightBtn: "tamper",
    waitFor: "click:tamper",
  },
  {
    title: "Prove it isn't theatre",
    body: `Fair question: does it just flag <i>everything</i>? No — the baselines are real.<br><br>
           Open a <b>normal</b> session: <code>alice</code> → <code>db-prod</code>, device
           <code>alice-laptop</code>, hour <code>14</code>. It stays <b>green / low</b>.
           Same engine, same systems — only genuine anomalies score.`,
    target: "card-probe",
    doText: "Click Open session (alice · 14:00)",
    spotlightBtn: "m-open",
    waitFor: "click:m-open",
  },
  {
    title: "That's the loop",
    body: `<b>Attack → detect → explain → enforce → prove.</b><br><br>
           The same tool generates the insider attack <i>and</i> validates that detection caught
           it — so every claim here is demonstrable, not a mock-up. Post-quantum crypto protects
           the credentials and the evidence trail.<br><br>
           Replay any time with <b>🎓 Guided demo</b>.`,
  },
];

let tourIdx = 0, tourArmed = null;

function clearSpotlight() {
  document.querySelectorAll(".spotlight, .spotlight-btn")
    .forEach((e) => e.classList.remove("spotlight", "spotlight-btn"));
}

function disarm() {
  if (!tourArmed) return;
  const { el, type, fn } = tourArmed;
  (el || document).removeEventListener(type, fn);
  tourArmed = null;
}

function renderTour() {
  const step = TOUR[tourIdx];
  clearSpotlight();
  disarm();

  $("tour-count").textContent = `Step ${tourIdx + 1} of ${TOUR.length}`;
  $("tour-title").textContent = step.title;
  $("tour-body").innerHTML = step.body;
  $("tour-dots").innerHTML = TOUR.map((_, i) =>
    `<i class="${i === tourIdx ? "on" : i < tourIdx ? "done" : ""}"></i>`).join("");
  $("tour-back").disabled = tourIdx === 0;
  $("tour-next").textContent = tourIdx === TOUR.length - 1 ? "Done ✓" : "Next →";

  if (step.target) {
    const t = $(step.target);
    if (t) { t.classList.add("spotlight"); t.scrollIntoView({ behavior: "smooth", block: "center" }); }
  }
  if (step.spotlightBtn) $(step.spotlightBtn)?.classList.add("spotlight-btn");

  // Steps with a required action gate Next until it happens.
  const doEl = $("tour-do");
  if (step.doText) {
    doEl.textContent = "👉 " + step.doText;
    doEl.classList.remove("hidden");
  } else {
    doEl.classList.add("hidden");
  }

  if (step.waitFor) {
    $("tour-next").disabled = true;
    const [kind, id] = step.waitFor.split(":");
    const el = kind === "click" ? $(id) : document;
    const type = kind === "click" ? "click" : step.waitFor;
    const fn = () => {
      $("tour-next").disabled = false;
      doEl.textContent = "✓ Done — press Next";
      doEl.style.background = "#163f33";
      doEl.style.color = "#b6f0d8";
      doEl.style.borderLeftColor = "#34d399";
      disarm();
    };
    el.addEventListener(type, fn, { once: true });
    tourArmed = { el, type, fn };
    doEl.style.background = ""; doEl.style.color = ""; doEl.style.borderLeftColor = "";
  } else {
    $("tour-next").disabled = false;
  }
}

function tourGo(i) {
  if (i < 0 || i >= TOUR.length) return closeTour();
  tourIdx = i;
  renderTour();
}
function openTour(from = 0) { $("tour").classList.remove("hidden"); tourGo(from); }
function closeTour() {
  clearSpotlight(); disarm();
  $("tour").classList.add("hidden");
  localStorage.setItem("pas_tour_seen", "1");
}

// Prefill the manual probe with the "normal session" the tour asks for.
function prefillProbe() {
  $("m-user").value = "alice"; $("m-system").value = "db-prod";
  $("m-device").value = "alice-laptop"; $("m-hour").value = 14;
}

// ---------- wire up ----------
$("tour-start").onclick = () => openTour(0);
$("tour-close").onclick = closeTour;
$("tour-next").onclick = () => {
  if (tourIdx === TOUR.length - 1) return closeTour();
  if (TOUR[tourIdx + 1]?.target === "card-probe") prefillProbe();
  tourGo(tourIdx + 1);
};
$("tour-back").onclick = () => tourGo(tourIdx - 1);
$("run-attack").onclick = runAttack;
$("reset").onclick = async () => { await post("/reset"); LATEST_SID = null; $("audit-result").innerHTML = ""; $("audit-log").textContent = ""; $("exfil-out").classList.add("hidden"); $("narration").classList.add("hidden"); await refresh(); };
$("m-open").onclick = manualOpen;
$("m-act").onclick = manualAction;
$("verify").onclick = verify;
$("tamper").onclick = tamper;
$("exfil").onclick = exfil;

// First-time visitors (judges opening the link cold) get the guide automatically.
refresh().then(() => {
  if (!localStorage.getItem("pas_tour_seen")) openTour(0);
});
setInterval(refresh, 1500);
