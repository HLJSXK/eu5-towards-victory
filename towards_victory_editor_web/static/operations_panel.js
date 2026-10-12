// WP-10: operations panel. GET /api/operations existed with no caller in the frontend; this module
// polls it, splits the newest operations into running / failed / recently finished, and expands one
// row through GET /api/operations/{id}.
//
// Report text is not rendered here: `statusLabel` and `formatOperationReport` from display.js own that,
// exactly as the job panel and the generator panel reuse them.
import { fetchJson } from "./api.js";
import { escapeHtml, formatOperationReport, statusLabel } from "./display.js";
import { setToolJobs } from "./resource_state.js";

export const RUNNING_STATUSES = ["queued", "running", "cancelling"];
export const DETAIL_LIMIT = 25;

// One resource id or operation kind names at most one tab. Anything unmapped simply gets no marker.
const TOOL_BY_RESOURCE = {
  "editor.cost_reward": "cost-reward",
  "editor.victory_tree": "victory-tree",
  "editor.wonder": "wonder-localization",
  "editor.wonder_crop": "wonder-cropper",
  "media.historical": "media-studio",
};

const TOOL_BY_KIND = {
  media_job: "media-studio",
  generator_run: "generators",
};

const KIND_LABELS = {
  resource_commit: "资源保存",
  commit: "保存",
  media_job: "媒体作业",
  generator_run: "生成器运行",
};

export function kindLabel(kind) {
  return KIND_LABELS[kind] || kind;
}

export function isRunning(operation) {
  return RUNNING_STATUSES.includes(operation.status);
}

export function toolForOperation(operation) {
  for (const resourceId of operation.resource_ids || []) {
    if (TOOL_BY_RESOURCE[resourceId]) return TOOL_BY_RESOURCE[resourceId];
  }
  return TOOL_BY_KIND[operation.kind] || null;
}

// The three sections are disjoint so a row is never rendered twice: a failed operation belongs to
// 失败项, a running one to 在跑作业, and everything terminal-but-not-failed to 最近操作.
export function operationGroups(operations = []) {
  const groups = { running: [], failed: [], recent: [] };
  for (const operation of operations) {
    if (isRunning(operation)) groups.running.push(operation);
    else if (operation.status === "failed") groups.failed.push(operation);
    else groups.recent.push(operation);
  }
  return groups;
}

export function runningCounts(operations = []) {
  const counts = new Map();
  for (const operation of operations) {
    if (!isRunning(operation)) continue;
    const tool = toolForOperation(operation);
    if (tool) counts.set(tool, (counts.get(tool) || 0) + 1);
  }
  return counts;
}

export function formatTime(seconds) {
  if (typeof seconds !== "number" || !Number.isFinite(seconds)) return "—";
  return new Date(seconds * 1000).toLocaleTimeString(undefined, { hour12: false });
}

export function formatDuration(operation) {
  const { started_at: started, finished_at: finished } = operation;
  if (typeof started !== "number" || typeof finished !== "number" || finished < started) return "";
  return `${(finished - started).toFixed(1)} 秒`;
}

// Plain-text row facts. The rich formatting stays in display.js; this only arranges them.
export function operationSummary(operation) {
  const parts = [statusLabel(operation.status), kindLabel(operation.kind), formatTime(operation.created_at)];
  if (operation.resource_ids?.length) parts.push(operation.resource_ids.join(", "));
  const duration = formatDuration(operation);
  if (duration) parts.push(duration);
  return parts.filter(Boolean).join(" · ");
}

export function operationDetail(payload) {
  const operation = payload?.operation || payload || {};
  const lines = [operationSummary(operation)];
  if (operation.error) lines.push(`错误: ${operation.error}`);
  if (operation.persistence_error) lines.push(`操作记录写入失败: ${operation.persistence_error}`);
  const report = formatOperationReport({ operation_id: operation.id, operation });
  if (report) lines.push(report);
  for (const event of operation.events || []) {
    lines.push(`[${formatTime(event.at)}] ${event.level === "error" ? "错误: " : ""}${event.message}`);
  }
  return lines.join("\n");
}

function rowHtml(operation) {
  const id = escapeHtml(String(operation.id ?? ""));
  return `<li class="operations-row" data-operation-id="${id}" data-status="${escapeHtml(operation.status || "")}" data-kind="${escapeHtml(operation.kind || "")}">
    <div class="operations-row-main">
      <span class="operations-status" data-kind="${escapeHtml(operation.status || "")}">${escapeHtml(statusLabel(operation.status))}</span>
      <span class="operations-summary">${escapeHtml(operationSummary(operation))}</span>
      <button type="button" class="operations-toggle" data-operation-toggle="${id}" aria-expanded="false">展开</button>
    </div>
    ${operation.error ? `<p class="operations-error">${escapeHtml(operation.error)}</p>` : ""}
    <pre class="operations-detail" data-operation-detail="${id}" hidden></pre>
  </li>`;
}

export function operationsHtml(groups) {
  const section = (key, title, operations, empty) => `<section class="operations-group" data-group="${key}">
    <h4>${escapeHtml(title)} <span class="operations-count">${operations.length}</span></h4>
    ${operations.length ? `<ul>${operations.map(rowHtml).join("")}</ul>` : `<p class="operations-empty">${escapeHtml(empty)}</p>`}
  </section>`;
  return [
    section("running", "在跑作业", groups.running, "没有正在运行的作业。"),
    section("failed", "失败项", groups.failed, "没有失败的操作。"),
    section("recent", "最近操作", groups.recent, "暂无已完成的操作。"),
  ].join("");
}

export function createOperationsPanel(root, {
  fetch: fetchImpl = fetchJson, schedule = (callback, ms) => globalThis.setTimeout(callback, ms),
  cancel = (timer) => globalThis.clearTimeout(timer), delay = 5000, limit = DETAIL_LIMIT,
} = {}) {
  root.innerHTML = `<div class="operations-bar">
    <strong class="operations-title">操作</strong>
    <span class="operations-status-bar" role="status"></span>
    <button type="button" data-operations-refresh>刷新</button>
  </div>
  <div class="operations-results"></div>`;
  const statusBar = root.querySelector(".operations-status-bar");
  const results = root.querySelector(".operations-results");
  const refreshButton = root.querySelector("[data-operations-refresh]");
  let timer = null, generation = 0, stopped = false;
  const details = new Map();

  function publishJobs(operations) {
    const counts = runningCounts(operations);
    // Clear every tool we know about so a finished job's marker disappears, not just the ones still busy.
    for (const tool of Object.values(TOOL_BY_RESOURCE).concat(Object.values(TOOL_BY_KIND))) {
      setToolJobs(tool, counts.get(tool) || 0);
    }
  }

  function render(operations, { error = null } = {}) {
    const groups = operationGroups(operations);
    root.dataset.state = error ? "failed" : operations.length ? "loaded" : "empty";
    statusBar.textContent = error
      ? `操作列表查询失败: ${error.message}`
      : `共 ${operations.length} 项：在跑 ${groups.running.length}，失败 ${groups.failed.length}，最近 ${groups.recent.length}`;
    results.innerHTML = operationsHtml(groups);
    // An expanded row keeps its content only while the operation is still in the list.
    const present = new Set(operations.map((operation) => String(operation.id)));
    for (const id of [...details.keys()]) if (!present.has(id)) details.delete(id);
  }

  async function refresh() {
    const current = ++generation;
    refreshButton.disabled = true;
    try {
      const payload = await fetchImpl(`api/operations?limit=${limit}`);
      if (current !== generation) return;
      const operations = payload.operations || [];
      render(operations);
      publishJobs(operations);
    } catch (error) {
      if (current !== generation) return;
      render([], { error });
      publishJobs([]);
    } finally {
      if (current === generation) refreshButton.disabled = false;
    }
  }

  async function toggle(button) {
    const id = button.dataset.operationToggle;
    const detail = button.closest(".operations-row")?.querySelector(".operations-detail");
    if (!detail) return;
    if (detail.hidden === false || details.has(id)) {
      detail.hidden = true;
      details.delete(id);
      button.textContent = "展开";
      button.setAttribute("aria-expanded", "false");
      return;
    }
    button.disabled = true;
    try {
      const payload = await fetchImpl(`api/operations/${encodeURIComponent(id)}`);
      detail.textContent = operationDetail(payload);
      detail.hidden = false;
      details.set(id, payload);
      button.textContent = "收起";
      button.setAttribute("aria-expanded", "true");
    } catch (error) {
      detail.textContent = `操作详情查询失败: ${error.message}`;
      detail.hidden = false;
      button.textContent = "收起";
      button.setAttribute("aria-expanded", "true");
    } finally {
      button.disabled = false;
    }
  }

  results.addEventListener("click", (event) => {
    const button = event.target.closest("[data-operation-toggle]");
    if (button && root.contains(button)) void toggle(button);
  });
  refreshButton.addEventListener("click", () => void refresh());

  function poll() {
    if (stopped) return;
    if (timer !== null) cancel(timer);
    timer = schedule(async () => {
      timer = null;
      await refresh();
      poll();
    }, delay);
  }

  return {
    refresh,
    poll,
    render,
    stop() {
      stopped = true;
      generation += 1;
      if (timer !== null) cancel(timer);
      timer = null;
    },
  };
}

// Page entry: index.html loads this module next to #operations-panel. Guarded so a Node test can
// import the pure grouping helpers above without a DOM.
const host = document.getElementById("operations-panel");
if (host) {
  const page = createOperationsPanel(host);
  window.__operationsPanel = page;
  void page.refresh();
  page.poll();
}
