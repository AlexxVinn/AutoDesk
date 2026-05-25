const API_HOST = "127.0.0.1";
const API_PORT = 9477;
const API_BASE = `http://${API_HOST}:${API_PORT}`;
const WS_URL = `ws://${API_HOST}:${API_PORT}/ws`;

const statusDot = document.getElementById("status-dot");
const connectionStatus = document.getElementById("connection-status");
const commandInput = document.getElementById("command-input");
const runBtn = document.getElementById("run-btn");
const feedback = document.getElementById("feedback");
const presetsEl = document.getElementById("presets");
const voiceBtn = document.getElementById("voice-btn");
const reconnectBtn = document.getElementById("reconnect-btn");

let ws = null;
let voiceOn = false;

function setConnected(ok, message) {
  statusDot.className = "dot " + (ok ? "ok" : "err");
  connectionStatus.textContent = message;
}

function showFeedback(data) {
  feedback.textContent = JSON.stringify(data, null, 2);
}

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  return res.json();
}

async function loadPresets() {
  try {
    const presets = await api("/presets");
    presetsEl.innerHTML = "";
    for (const p of presets) {
      const btn = document.createElement("button");
      btn.className = "preset-btn";
      btn.innerHTML = `<strong>${p.label}</strong><span>${p.description || p.id}</span>`;
      btn.addEventListener("click", () => runPreset(p.id));
      presetsEl.appendChild(btn);
    }
  } catch (err) {
    presetsEl.innerHTML = "<p class='hint'>Backend offline — start Python server.</p>";
  }
}

async function runCommand(text) {
  if (!text.trim()) return;
  try {
    const result = await api("/command", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
    showFeedback(result);
  } catch (err) {
    showFeedback({ success: false, error: String(err) });
  }
}

async function runPreset(id) {
  try {
    const result = await api(`/preset/${id}`, { method: "POST" });
    showFeedback(result);
  } catch (err) {
    showFeedback({ success: false, error: String(err) });
  }
}

function connectWs() {
  if (ws) {
    ws.close();
  }
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    setConnected(true, "Connected");
    ws.send(JSON.stringify({ type: "ping" }));
  };
  ws.onmessage = (ev) => {
    const data = JSON.parse(ev.data);
    if (data.type === "transcript" || data.type === "result") {
      showFeedback(data);
    }
    if (data.type === "status") {
      connectionStatus.textContent = `Voice: ${data.status}`;
    }
  };
  ws.onclose = () => setConnected(false, "Disconnected");
  ws.onerror = () => setConnected(false, "Connection error");
}

async function toggleVoice() {
  voiceOn = !voiceOn;
  try {
    await api("/voice/toggle", {
      method: "POST",
      body: JSON.stringify({ enabled: voiceOn }),
    });
    voiceBtn.textContent = `Voice: ${voiceOn ? "on" : "off"}`;
  } catch (err) {
    showFeedback({ success: false, error: String(err) });
  }
}

runBtn.addEventListener("click", () => runCommand(commandInput.value));
commandInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") runCommand(commandInput.value);
});
voiceBtn.addEventListener("click", toggleVoice);
reconnectBtn.addEventListener("click", () => {
  connectWs();
  loadPresets();
});

connectWs();
loadPresets();
