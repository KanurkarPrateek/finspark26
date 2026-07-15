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
async function runAttack() {
  $("run-attack").disabled = true;
  await post("/reset");
  const sc = await api("/attack/scenario");
  const s = await post("/session/open", sc.open);
  LATEST_SID = s.id;
  await refresh();
  for (const step of sc.steps) {
    await sleep(1400);
    await post(`/session/${LATEST_SID}/action`, step.event);
    await refresh();
  }
  $("run-attack").disabled = false;
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

// ---------- wire up ----------
$("run-attack").onclick = runAttack;
$("reset").onclick = async () => { await post("/reset"); LATEST_SID = null; $("audit-result").innerHTML = ""; $("audit-log").textContent = ""; $("exfil-out").classList.add("hidden"); await refresh(); };
$("m-open").onclick = manualOpen;
$("m-act").onclick = manualAction;
$("verify").onclick = verify;
$("tamper").onclick = tamper;
$("exfil").onclick = exfil;

refresh();
setInterval(refresh, 1500);
