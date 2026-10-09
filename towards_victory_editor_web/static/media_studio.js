import { fetchJson } from "./api.js";
import { ResourceState, JobPoller, setControlsBusy } from "./resource_state.js";

// detachedJobId: a job the user stopped tracking while it may still run; it stays cancellable.
const state = { tools: [], selected: null, cancelError: "", cancelling: false, detachedJobId: null };
const submission = new ResourceState({ onChange: () => syncFormControls() });
const poller = new JobPoller({
  fetchJob: (id, cursor) => fetchJson(`/api/jobs/${id}?after_line=${cursor}`),
  onUpdate: renderJob,
  onError: renderPollError,
});

function renderPollError(error, retrying) {
  const message = poller.active
    ? `Status request failed${retrying ? "; retrying" : "; retry or stop tracking"}`
    : `Stopped tracking job ${poller.jobId}; server outcome unknown${state.detachedJobId === poller.jobId ? "; it may still run and can be cancelled" : ""}`;
  document.getElementById("media-status").textContent = `${message}: ${error.message}${state.cancelError ? ` — ${state.cancelError}` : ""}`;
  document.getElementById("media-poll-retry").hidden = !poller.active;
  document.getElementById("media-poll-stop").hidden = !poller.active;
  syncFormControls();
}

function selectedTool() { return state.tools.find((tool) => tool.id === state.selected); }

function cancellable() { return poller.active || state.detachedJobId === poller.jobId; }

function syncFormControls() {
  setControlsBusy(document.querySelectorAll("#media-tool-list button, #media-form input, #media-form select"), submission.busy || poller.active);
  document.getElementById("media-cancel").disabled = !cancellable() || state.cancelling;
  document.getElementById("media-run").disabled = poller.active || submission.busy;
}

function renderToolList() {
  const root = document.getElementById("media-tool-list");
  root.innerHTML = "";
  state.tools.forEach((tool) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `media-tool-item${tool.id === state.selected ? " active" : ""}`;
    button.innerHTML = `<strong>${tool.label}</strong><span>${tool.description}</span>`;
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

function renderJob(job) {
  state.detachedJobId = null;
  document.getElementById("media-status").textContent = job.operation.interrupted && job.outputs_may_be_partial
    ? `${job.status} — interrupted; formal outputs may be partially published; review files and retained backups`
    : job.outputs_may_be_partial ? `${job.status} — formal outputs require review` : job.status;
  if (job.error) document.getElementById("media-status").textContent += `: ${job.error}`;
  if (state.cancelError) document.getElementById("media-status").textContent += ` — ${state.cancelError}`;
  document.getElementById("media-log").textContent = job.lines.join("\n");
  document.getElementById("media-poll-retry").hidden = true;
  document.getElementById("media-poll-stop").hidden = true;
  const files = [];
  if (job.resource_ids.length) files.push(`Resources: ${job.resource_ids.join(", ")}`);
  if (job.formal_output_changes.length) files.push("Formal outputs changed outside staging (review required):", ...job.formal_output_changes.map((path) => `  ${path}`));
  if (job.staging_extra_files.length) files.push("Intermediate files excluded from publication:", ...job.staging_extra_files.map((path) => `  ${path}`));
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
  syncFormControls();
}

document.getElementById("media-poll-retry").addEventListener("click", () => poller.poll());
document.getElementById("media-poll-stop").addEventListener("click", () => {
  poller.stop();
  state.detachedJobId = poller.jobId;
  renderPollError(poller.error, false);
});
document.getElementById("media-run").addEventListener("click", async () => {
  if (submission.busy || poller.active) return;
  const button = document.getElementById("media-run"); button.disabled = true;
  try {
    await submission.run("submitting", () => fetchJson("/api/jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ tool: state.selected, options: formOptions() }) }), { apply: (job) => {
      state.cancelError = "";
      poller.start(job);
    } });
  } catch (error) { document.getElementById("media-status").textContent = error.message; }
  finally { button.disabled = poller.active; }
});
document.getElementById("media-cancel").addEventListener("click", async () => {
  const jobId = poller.jobId;
  const generation = poller.generation;
  const detached = !poller.active;
  if (!cancellable() || state.cancelling) return;
  state.cancelling = true;
  state.cancelError = "";
  document.getElementById("media-cancel").disabled = true;
  try {
    const job = await fetchJson(`/api/jobs/${jobId}/cancel`, { method: "POST" });
    // The cancel response is a full snapshot, so a detached job resumes tracking from it.
    if (detached ? state.detachedJobId === jobId && poller.jobId === jobId : poller.isCurrent(jobId, generation) && poller.active) {
      if (detached) poller.start(job);
      else poller.accept(job, generation);
    }
  } catch (error) {
    if (poller.jobId === jobId && (detached || poller.isCurrent(jobId, generation))) {
      state.cancelError = `Cancellation failed: ${error.message}`;
      document.getElementById("media-status").textContent = state.cancelError;
    }
  } finally {
    state.cancelling = false;
    syncFormControls();
  }
});

fetchJson("/api/media/bootstrap").then((payload) => {
  window.__mediaBootstrap = payload; state.tools = payload.tools || []; state.selected = state.tools[0]?.id || null; renderToolList(); renderForm();
}).catch((error) => { document.getElementById("media-status").textContent = error.message; });
