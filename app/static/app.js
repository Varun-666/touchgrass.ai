const state = { mode: "nature", energy: "low" };

const $ = (id) => document.getElementById(id);
const result = $("result");

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".mode").forEach(btn => btn.classList.toggle("active", btn.dataset.mode === mode));
}

document.querySelectorAll(".mode").forEach(btn => btn.addEventListener("click", () => setMode(btn.dataset.mode)));

document.querySelectorAll("#energy button").forEach(btn => btn.addEventListener("click", () => {
  state.energy = btn.dataset.value;
  document.querySelectorAll("#energy button").forEach(b => b.classList.toggle("selected", b === btn));
}));

$("duration").addEventListener("input", e => $("durationValue").textContent = e.target.value);

function splitInterests(value) {
  return value.split(",").map(x => x.trim()).filter(Boolean).slice(0, 8);
}

function fillMission(data) {
  $("resultTitle").textContent = data.title;
  $("resultReason").textContent = data.reason;
  $("resultDuration").textContent = data.duration_minutes;
  $("resultModel").textContent = data.model.includes("fallback") ? "LOCAL FALLBACK" : "LOCAL MODEL";
  $("steps").innerHTML = data.steps.map(x => `<li>${escapeHtml(x)}</li>`).join("");
  $("lookFor").innerHTML = data.look_for.map(x => `<li>${escapeHtml(x)}</li>`).join("");
  $("phoneRule").textContent = data.phone_rule;
  $("safety").textContent = data.safety;
  $("closing").textContent = data.closing_line;
  result.classList.remove("hidden");
  result.scrollIntoView({ behavior: "smooth", block: "start" });
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value;
  return div.innerHTML;
}

$("generate").addEventListener("click", async () => {
  const button = $("generate");
  button.disabled = true;
  button.querySelector("span:first-child").textContent = "Thinking locally…";

  const payload = {
    mode: state.mode,
    duration: Number($("duration").value),
    energy: state.energy,
    setting: $("setting").value,
    interests: splitInterests($("interests").value),
    goal: $("goal").value.trim() || "I want to spend some time outside."
  };

  try {
    const response = await fetch("/api/mission", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error("Mission request failed");
    fillMission(await response.json());
  } catch (error) {
    alert("Could not generate a mission. Check that the local server is running.");
  } finally {
    button.disabled = false;
    button.querySelector("span:first-child").textContent = "Generate my mission";
  }
});

$("again").addEventListener("click", () => {
  result.classList.add("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
});

fetch("/api/health").then(r => r.json()).then(data => {
  $("status").innerHTML = `<span class="dot"></span> ${data.local ? "local AI" : "cloud AI"}`;
}).catch(() => {});

if ("serviceWorker" in navigator) navigator.serviceWorker.register("/static/sw.js").catch(() => {});
