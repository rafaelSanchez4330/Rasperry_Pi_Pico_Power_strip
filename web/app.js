"use strict";

const REFRESH_MS = 5000;

const els = {
  projectName: document.getElementById("project-name"),
  statusDot: document.getElementById("status-dot"),
  statusText: document.getElementById("status-text"),
  deviceIp: document.getElementById("device-ip"),
  outlets: document.getElementById("outlets"),
  allOn: document.getElementById("all-on"),
  allOff: document.getElementById("all-off"),
  error: document.getElementById("error"),
};

function showError(message) {
  if (!message) {
    els.error.hidden = true;
    els.error.textContent = "";
    return;
  }
  els.error.hidden = false;
  els.error.textContent = message;
}

async function api(path, options) {
  const response = await fetch(path, options);
  if (!response.ok) {
    throw new Error("HTTP " + response.status);
  }
  return response.json();
}

async function refreshStatus() {
  try {
    const data = await api("/api/status");
    if (data.project) {
      els.projectName.textContent = data.project;
      document.title = data.project;
    }
    const online = Boolean(data.online);
    els.statusDot.className = "dot " + (online ? "online" : "offline");
    els.statusText.textContent = online ? "En línea" : "Sin conexión";
    els.deviceIp.textContent = data.ip ? data.ip : "";
  } catch (err) {
    els.statusDot.className = "dot offline";
    els.statusText.textContent = "Sin conexión";
  }
}

function outletCard(outlet) {
  const isOn = outlet.state === "on";
  const card = document.createElement("div");
  card.className = "outlet" + (isOn ? " is-on" : "");

  const name = document.createElement("div");
  name.className = "outlet__name";
  name.textContent = outlet.name;

  const state = document.createElement("div");
  state.className = "outlet__state";
  const indicator = document.createElement("span");
  indicator.className = "indicator";
  const label = document.createElement("span");
  label.className = "label";
  label.textContent = isOn ? "ON" : "OFF";
  state.appendChild(indicator);
  state.appendChild(label);

  const button = document.createElement("button");
  button.className = "btn " + (isOn ? "btn-off" : "btn-on");
  button.textContent = isOn ? "Apagar" : "Encender";
  button.addEventListener("click", () => toggleOutlet(outlet.id, isOn));

  card.appendChild(name);
  card.appendChild(state);
  card.appendChild(button);
  return card;
}

function renderOutlets(outlets) {
  els.outlets.innerHTML = "";
  outlets.forEach((outlet) => els.outlets.appendChild(outletCard(outlet)));
}

async function refreshOutlets() {
  try {
    const data = await api("/api/outlets");
    renderOutlets(data.outlets || []);
    showError(null);
  } catch (err) {
    showError("No se pudo cargar el estado de los contactos.");
  }
}

async function toggleOutlet(id, isOn) {
  const action = isOn ? "off" : "on";
  try {
    await api("/api/outlets/" + id + "/" + action, { method: "POST" });
    await refreshOutlets();
  } catch (err) {
    showError("No se pudo cambiar el contacto " + id + ".");
  }
}

async function allOutlets(action) {
  try {
    await api("/api/outlets/all/" + action, { method: "POST" });
    await refreshOutlets();
  } catch (err) {
    showError("No se pudo aplicar la acción global.");
  }
}

els.allOn.addEventListener("click", () => allOutlets("on"));
els.allOff.addEventListener("click", () => allOutlets("off"));

function tick() {
  refreshStatus();
  refreshOutlets();
}

tick();
setInterval(tick, REFRESH_MS);
