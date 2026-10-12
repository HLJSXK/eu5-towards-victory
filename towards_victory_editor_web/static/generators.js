import { fetchJson } from "./api.js";
import { statusLabel } from "./display.js";
import { createJobPanel } from "./job_panel.js";

// WP-09: browser entry for the registered generator scripts (contract: Editor_Web_Work_Plan.md 6.3).
//
// The backend runs the selected scripts in request order and stops at the first failure. There is no
// dependency graph: the panel only states the order the user picked, and the server rejects a selection
// whose outputs intersect. Reports reuse the shared display layer — `jobPanel.log.report()` renders
// formatOperationReport and `jobPanel.files()` renders formatJobFiles; this module only maps the
// generator payload into those two existing shapes.

export function groupGenerators(generators) {
  const groups = new Map();
  for (const generator of generators) {
    const key = `${generator.root}/${generator.domain}`;
    if (!groups.has(key)) groups.set(key, { key, root: generator.root, domain: generator.domain, scripts: [] });
    groups.get(key).scripts.push(generator);
  }
  return [...groups.values()];
}

// Step and artifact field names differ from the Wonder generation report; the mapping is the whole
// difference, so the shared renderer stays the only place that formats these lines.
export function generationPayload(payload) {
  const operation = payload.operation || {};
  return {
    operation_id: payload.operation_id,
    operation: payload.operation,
    generation: {
      status: operation.status,
      error: operation.error,
      steps: (payload.results || []).map((result) => ({
        id: result.script,
        status: result.status,
        returncode: result.exit_code,
        duration_seconds: result.duration_ms == null ? null : Number((result.duration_ms / 1000).toFixed(3)),
      })),
      artifacts: (payload.artifacts || []).map((artifact) => ({
        path: artifact.path,
        role: artifact.sha256 === "missing" ? "deleted" : "generated",
        changed: artifact.changed,
      })),
      rollback: payload.rollback,
    },
  };
}

export function jobPayload(payload, declaredOutputs) {
  return {
    operation: payload.operation || {},
    formal_output_changes: [],
    staging_extra_files: [],
    source_snapshots: [],
    artifacts: payload.artifacts || [],
    declared_outputs: declaredOutputs,
    missing_outputs: [],
    metadata: { output_validation: [] },
    publication_rollback_failed: false,
  };
}

export function planText(selected) {
  if (!selected.length) return "执行顺序：尚未选择脚本。脚本按勾选顺序执行，没有依赖图。";
  return `执行顺序：${selected.map((script, index) => `${index + 1}. ${script}`).join(" → ")}`;
}

export function runSummary(payload, dryRun) {
  const results = payload.results || [];
  const artifacts = payload.artifacts || [];
  const parts = [`${results.length} 个脚本`, statusLabel(payload.operation?.status)];
  if (dryRun) parts.push("dry_run：未执行脚本、未写入文件");
  else parts.push(`${artifacts.filter((artifact) => artifact.changed).length}/${artifacts.length} 个产物有变化`);
  return parts.join("；");
}

function listLines(items) {
  return items.length ? items.map((item) => `  ${item}`).join("\n") : "  （未登记）";
}

export function createGeneratorsPanel(root, {
  load = () => fetchJson("/api/generators"),
  run = (body) => fetchJson("/api/generators/run", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  }),
} = {}) {
  root.dataset.busy = "false";
  root.dataset.running = "false";
  root.innerHTML = `<div class="generators-layout">
    <aside class="generators-sidebar">
      <div class="generators-note">
        <strong>顺序执行，无依赖图</strong>
        <p>脚本按勾选顺序依次执行。中途失败即停止，后续脚本不再运行，产物不会发布；
        一次请求内输出路径相交的脚本组合会被服务端直接拒绝。</p>
      </div>
      <div class="generators-actions">
        <button type="button" class="primary-button" data-run disabled>运行所选生成器</button>
        <button type="button" data-reload>重新加载列表</button>
        <label class="generators-dry-run"><input type="checkbox" data-dry-run> 仅校验（dry_run，不执行脚本）</label>
      </div>
      <p class="generators-plan" data-plan role="status"></p>
    </aside>
    <main class="generators-main">
      <div class="generators-groups"></div>
      <div class="generators-run-panel"></div>
    </main>
  </div>`;

  const groupsNode = root.querySelector(".generators-groups");
  const planNode = root.querySelector("[data-plan]");
  const runButton = root.querySelector("[data-run]");
  const reloadButton = root.querySelector("[data-reload]");
  const dryRunInput = root.querySelector("[data-dry-run]");
  const state = { generators: [], groups: [], selected: [], rows: new Map(), toggles: new Map(), running: false, loaded: false };
  const jobPanel = createJobPanel({ root: root.querySelector(".generators-run-panel"), prefix: "gen", onChange: sync });

  function sync() {
    for (const group of state.groups) {
      const chosen = group.scripts.filter((generator) => state.selected.includes(generator.script)).length;
      const toggle = state.toggles.get(group.key);
      toggle.checked = chosen === group.scripts.length;
      toggle.indeterminate = chosen > 0 && chosen < group.scripts.length;
      toggle.disabled = state.running;
    }
    for (const [script, checkbox] of state.rows) {
      checkbox.checked = state.selected.includes(script);
      checkbox.disabled = state.running;
    }
    runButton.disabled = state.running || !state.selected.length;
    reloadButton.disabled = state.running;
    dryRunInput.disabled = state.running;
    planNode.textContent = state.running
      ? `正在按顺序执行 ${state.selected.length} 个脚本…`
      : planText(state.selected);
  }

  function select(script, checked) {
    const index = state.selected.indexOf(script);
    if (checked && index < 0) state.selected.push(script);
    if (!checked && index >= 0) state.selected.splice(index, 1);
  }

  function row(generator) {
    const element = document.createElement("div");
    element.className = "generator-row";
    const choice = document.createElement("label");
    choice.className = "generator-choice";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.addEventListener("change", () => { select(generator.script, checkbox.checked); sync(); });
    const name = document.createElement("span");
    name.className = "generator-script";
    name.textContent = generator.script;
    choice.appendChild(checkbox);
    choice.appendChild(name);
    const counts = document.createElement("span");
    counts.className = "generator-counts";
    counts.textContent = `${generator.outputs.length} 个产物`;
    const details = document.createElement("details");
    details.className = "generator-details";
    const summary = document.createElement("summary");
    summary.textContent = "输入与产物";
    const body = document.createElement("pre");
    body.textContent = `输入：\n${listLines(generator.data_inputs)}\n产物：\n${listLines(generator.outputs)}`;
    details.appendChild(summary);
    details.appendChild(body);
    element.appendChild(choice);
    element.appendChild(counts);
    element.appendChild(details);
    state.rows.set(generator.script, checkbox);
    return element;
  }

  function renderGroups() {
    groupsNode.innerHTML = "";
    state.rows.clear();
    state.toggles.clear();
    for (const group of state.groups) {
      const section = document.createElement("section");
      section.className = "generator-group";
      const head = document.createElement("label");
      head.className = "generator-group-head";
      const toggle = document.createElement("input");
      toggle.type = "checkbox";
      toggle.addEventListener("change", () => {
        for (const generator of group.scripts) select(generator.script, toggle.checked);
        sync();
      });
      const title = document.createElement("span");
      title.className = "generator-group-title";
      title.textContent = `${group.root} / ${group.domain}`;
      const counts = document.createElement("span");
      counts.className = "generator-group-counts";
      counts.textContent = `${group.scripts.length} 个脚本`;
      head.appendChild(toggle);
      head.appendChild(title);
      head.appendChild(counts);
      const rows = document.createElement("div");
      rows.className = "generator-group-rows";
      for (const generator of group.scripts) rows.appendChild(row(generator));
      section.appendChild(head);
      section.appendChild(rows);
      groupsNode.appendChild(section);
      state.toggles.set(group.key, toggle);
    }
  }

  function declaredOutputs() {
    const outputs = [];
    for (const group of state.groups) {
      for (const generator of group.scripts) {
        if (state.selected.includes(generator.script)) outputs.push(...generator.outputs);
      }
    }
    return outputs;
  }

  async function reload() {
    root.dataset.busy = "true";
    try {
      const payload = await load();
      state.generators = payload.generators || [];
      state.groups = groupGenerators(state.generators);
      // A reload keeps the current selection but drops scripts the catalogue no longer lists.
      state.selected = state.selected.filter((script) => state.generators.some((item) => item.script === script));
      renderGroups();
      state.loaded = true;
      jobPanel.status.set(`已加载 ${state.generators.length} 个已登记生成器`, "default");
    } catch (error) {
      jobPanel.error(error);
    } finally {
      root.dataset.busy = "false";
      sync();
    }
    return state;
  }

  async function runSelected() {
    if (state.running || !state.selected.length) return;
    const dryRun = dryRunInput.checked;
    const scripts = [...state.selected];
    state.running = true;
    root.dataset.running = "true";
    jobPanel.log.set("");
    jobPanel.status.set(dryRun ? "正在校验选择（dry_run）…" : `正在按顺序执行 ${scripts.length} 个脚本…`, "default");
    sync();
    try {
      const payload = await run({ scripts, dry_run: dryRun });
      jobPanel.log.report(generationPayload(payload));
      for (const result of payload.results || []) {
        if (result.output_tail) jobPanel.log.append(`\n[${result.script}]\n${result.output_tail}`);
      }
      jobPanel.files(jobPayload(payload, dryRun ? [] : declaredOutputs()));
      jobPanel.status.set(runSummary(payload, dryRun), payload.operation?.status === "succeeded" ? "default" : "error");
    } catch (error) {
      jobPanel.error(error);
    } finally {
      state.running = false;
      root.dataset.running = "false";
      sync();
    }
  }

  runButton.addEventListener("click", () => runSelected());
  reloadButton.addEventListener("click", () => reload());
  sync();

  return { state, sync, run: runSelected, reload };
}

// Page entry: shared.js dispatches `tool-activated` when a tab is shown, so the generator catalogue is
// fetched when the tab is first opened rather than on page load.
const page = createGeneratorsPanel(document.getElementById("generators-root"));
document.addEventListener("tool-activated", (event) => {
  if (event.detail?.tool === "generators" && !page.state.loaded) void page.reload();
});
