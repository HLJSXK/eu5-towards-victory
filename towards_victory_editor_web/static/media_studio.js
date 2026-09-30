const state = { tools: [], selected: null, jobId: null, timer: null };

async function jsonFetch(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  let payload = {};
  try { payload = text ? JSON.parse(text) : {}; } catch { payload = { detail: text }; }
  if (!response.ok) throw new Error(payload.detail || response.statusText);
  return payload;
}

function selectedTool() { return state.tools.find((tool) => tool.id === state.selected); }

function renderToolList() {
  const root = document.getElementById("media-tool-list");
  root.innerHTML = "";
  state.tools.forEach((tool) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `media-tool-item${tool.id === state.selected ? " active" : ""}`;
    button.innerHTML = `<strong>${tool.label}</strong><span>${tool.description}</span>`;
    button.addEventListener("click", () => { state.selected = tool.id; renderToolList(); renderForm(); });
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

function renderJob(job) {
  window.clearTimeout(state.timer);
  document.getElementById("media-status").textContent = job.outputs_may_be_partial
    ? `${job.status} — output files changed; no rollback performed` : job.status;
  document.getElementById("media-log").textContent = (job.lines || []).join("\n");
  const files = [];
  if (job.resource_ids.length) files.push(`Resources: ${job.resource_ids.join(", ")}`);
  if (job.source_snapshots.length) files.push("Inputs:", ...job.source_snapshots.map((source) => `  ${source.path}${source.sha256 === "missing" ? " (optional, absent)" : ""}`));
  const artifacts = new Map(job.artifacts.map((artifact) => [artifact.path, artifact]));
  const errors = new Map((job.metadata.output_validation || []).filter((report) => !report.valid).map((report) => [report.path, report.error]));
  if (job.declared_outputs.length) files.push("Outputs:", ...job.declared_outputs.map((path) => {
    const artifact = artifacts.get(path);
    let status = "not produced";
    if (artifact) status = artifact.role === "deleted" ? "deleted" : artifact.changed ? "changed" : "unchanged";
    else if (job.missing_outputs.includes(path)) status = "missing";
    else if (["queued", "running", "cancelling"].includes(job.status)) status = "pending";
    return `  ${path} (${status})${errors.has(path) ? `: ${errors.get(path)}` : ""}`;
  }));
  document.getElementById("media-files").hidden = files.length === 0;
  document.getElementById("media-file-report").textContent = files.join("\n");
  document.getElementById("media-cancel").disabled = !["queued", "running", "cancelling"].includes(job.status);
  if (["queued", "running", "cancelling"].includes(job.status) && state.jobId) state.timer = window.setTimeout(pollJob, 700);
  else state.jobId = null;
}
async function pollJob() { try { renderJob(await jsonFetch(`/api/jobs/${state.jobId}`)); } catch (error) { document.getElementById("media-status").textContent = error.message; } }

document.getElementById("media-run").addEventListener("click", async () => {
  const button = document.getElementById("media-run"); button.disabled = true;
  try {
    const job = await jsonFetch("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tool: state.selected, options: formOptions() }) });
    state.jobId = job.id; renderJob(job);
  } catch (error) { document.getElementById("media-status").textContent = error.message; }
  finally { button.disabled = false; }
});
document.getElementById("media-cancel").addEventListener("click", async () => { if (state.jobId) renderJob(await jsonFetch(`/api/jobs/${state.jobId}/cancel`, { method: "POST" })); });

jsonFetch("/api/media/bootstrap").then((payload) => {
  window.__mediaBootstrap = payload; state.tools = payload.tools || []; state.selected = state.tools[0]?.id || null; renderToolList(); renderForm();
}).catch((error) => { document.getElementById("media-status").textContent = error.message; });
