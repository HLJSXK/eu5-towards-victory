import { fetchJson } from "./api.js";
import { ResourceState, setControlsBusy } from "./resource_state.js";
import { escapeHtml } from "./display.js";
import { createJobPanel } from "./job_panel.js";

const state = { tools: [], selected: null };
const submission = new ResourceState({ onChange: () => syncFormControls() });
const jobPanel = createJobPanel({
  root: document.getElementById("media-job"), prefix: "media", allowCancel: true,
  onChange: syncFormControls,
});
const poller = jobPanel.poller;

function selectedTool() { return state.tools.find((tool) => tool.id === state.selected); }

function syncFormControls() {
  setControlsBusy(document.querySelectorAll("#media-tool-list button, #media-form input, #media-form select"), submission.busy || poller.active);
  document.getElementById("media-run").disabled = poller.active || submission.busy;
}

function renderToolList() {
  const root = document.getElementById("media-tool-list");
  root.innerHTML = "";
  state.tools.forEach((tool) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `media-tool-item${tool.id === state.selected ? " active" : ""}`;
    button.innerHTML = `<strong>${escapeHtml(tool.label)}</strong><span>${escapeHtml(tool.description)}</span>`;
    button.addEventListener("click", () => {
      if (submission.busy || poller.active) return;
      state.selected = tool.id; renderToolList(); renderForm();
    });
    root.appendChild(button);
  });
}

function field(label, input) {
  const wrapper = document.createElement("label"); wrapper.className = "media-field";
  const title = document.createElement("span"); title.textContent = label;
  wrapper.append(title, input); return wrapper;
}

function checkbox(label, name, checked = false) {
  const input = document.createElement("input"); input.type = "checkbox"; input.name = name; input.checked = checked;
  const wrapper = field(label, input); wrapper.classList.add("checkbox-field"); return wrapper;
}

function renderForm() {
  const root = document.getElementById("media-form"); root.innerHTML = "";
  const tool = selectedTool(); if (!tool) return;
  const title = document.createElement("h2"); title.textContent = tool.label; root.appendChild(title);
  const form = document.createElement("div"); form.className = "media-fields";
  (tool.options || []).forEach((option) => {
    if (option.kind === "boolean") { form.append(checkbox(option.label, option.key, option.default === true)); return; }
    if (option.kind === "paths") {
      const group = document.createElement("fieldset"); group.className = "media-input-list";
      const legend = document.createElement("legend"); legend.textContent = option.label; group.appendChild(legend);
      (window.__mediaBootstrap?.config?.historical_inputs || []).forEach((path, index) => { const item = checkbox(path, option.key, index === 0); item.querySelector("input").value = path; group.appendChild(item); });
      form.appendChild(group); return;
    }
    const input = option.choices?.length ? document.createElement("select") : document.createElement("input");
    input.name = option.key;
    if (input.tagName === "SELECT") option.choices.forEach((choice) => { const item = document.createElement("option"); item.value = choice; item.textContent = choice; input.appendChild(item); });
    else { input.type = option.kind === "integer" ? "number" : "text"; if (option.kind === "integer") input.step = "1"; input.value = option.default ?? ""; }
    input.placeholder = option.description || option.label;
    form.appendChild(field(option.label, input));
  });
  root.appendChild(form);
}

function formOptions() {
  const options = {};
  document.querySelectorAll("#media-form input, #media-form select").forEach((input) => {
    if (input.name === "inputs") return;
    if (input.type === "checkbox") options[input.name] = input.checked;
    else if (input.value.trim()) options[input.name] = input.value.trim();
  });
  if (selectedTool()?.id === "media.historical_style") options.inputs = [...document.querySelectorAll('#media-form input[name="inputs"]:checked')].map((input) => input.value);
  return options;
}

document.getElementById("media-run").addEventListener("click", async () => {
  if (submission.busy || poller.active) return;
  try {
    jobPanel.status.set("正在提交", "working");
    await submission.run("submitting", () => fetchJson("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tool: state.selected, options: formOptions() }) }), { apply: (job) => jobPanel.start(job) });
  } catch (error) { jobPanel.error(error); }
});

fetchJson("/api/media/bootstrap").then((payload) => {
  window.__mediaBootstrap = payload; state.tools = payload.tools || []; state.selected = state.tools[0]?.id || null; renderToolList(); renderForm();
}).catch((error) => jobPanel.error(error));
