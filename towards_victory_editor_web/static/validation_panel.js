import { escapeHtml } from "./display.js";

// Renders POST /api/validate (contract: Editor_Web_Work_Plan.md 6.1). A failed check is HTTP 200 with
// pass:false; 400/500/504 mean validation did not complete and carry `detail` (504/500 also `output_tail`).

function seconds(report) {
  return (report.duration_ms / 1000).toFixed(1);
}

function location(item) {
  if (!item.file) return "";
  return item.line == null ? item.file : `${item.file}:${item.line}`;
}

function groupByRule(items) {
  const groups = new Map();
  for (const item of items) {
    if (!groups.has(item.rule)) groups.set(item.rule, []);
    groups.get(item.rule).push(item);
  }
  return groups;
}

export function validationState(report) {
  if (!report.pass) return "errors";
  return report.warnings.length ? "warnings" : "pass";
}

export function validationSummary(report) {
  const scope = `检查 ${report.files_checked} 个文件，用时 ${seconds(report)} 秒`;
  const state = validationState(report);
  if (state === "errors") return `校验失败：${report.errors.length} 条错误，${report.warnings.length} 条警告（${scope}）`;
  if (state === "warnings") return `校验通过，有 ${report.warnings.length} 条警告（${scope}）`;
  return `校验通过（${scope}）`;
}

// Plain-text form used by the copy button.
export function formatValidationReport(report) {
  const lines = [validationSummary(report)];
  for (const [label, items] of [["错误", report.errors], ["警告", report.warnings]]) {
    for (const [rule, group] of groupByRule(items)) {
      lines.push(`[${label}] ${rule} (${group.length})`);
      for (const item of group) lines.push(`  ${[location(item), item.message].filter(Boolean).join(" ")}`);
    }
  }
  return lines.join("\n");
}

function renderGroups(severity, label, items) {
  return [...groupByRule(items)].map(([rule, group]) => `<section class="validation-group" data-severity="${severity}">
    <h4>${label} · ${escapeHtml(rule)} <span class="validation-count">${group.length}</span></h4>
    <ul>${group.map((item) => `<li class="validation-item" data-severity="${severity}">${item.file
      ? `<code class="validation-file" title="可选中复制">${escapeHtml(location(item))}</code> ` : ""}<span>${escapeHtml(item.message)}</span></li>`).join("")}</ul>
  </section>`).join("");
}

async function requestValidation(fetchImpl) {
  const response = await fetchImpl("api/validate", {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ changed: true }),
  });
  const text = await response.text();
  let payload;
  try { payload = JSON.parse(text); } catch { payload = null; }
  if (response.ok) return payload;
  const detail = payload?.detail ?? (text || response.statusText);
  const error = new Error(`HTTP ${response.status}：${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
  error.outputTail = payload?.output_tail || "";
  throw error;
}

export function createValidationPanel(root, {
  fetch: fetchImpl = (...args) => fetch(...args),
  writeText = (text) => navigator.clipboard.writeText(text),
} = {}) {
  root.innerHTML = `<div class="validation-bar">
    <strong class="validation-title">校验</strong>
    <span class="validation-status" role="status"></span>
    <button type="button" data-validate>校验当前改动</button>
    <button type="button" data-copy disabled>复制结果</button>
  </div>
  <div class="validation-results" hidden></div>`;
  const status = root.querySelector(".validation-status");
  const results = root.querySelector(".validation-results");
  const validateButton = root.querySelector("[data-validate]");
  const copyButton = root.querySelector("[data-copy]");
  let copyText = "", running = null, again = false;

  function show(state, summary, html, text) {
    root.dataset.state = state;
    status.textContent = summary;
    results.innerHTML = html;
    results.hidden = !html;
    copyText = text;
    copyButton.disabled = !text;
    copyButton.textContent = "复制结果";
  }

  function render(report) {
    const html = renderGroups("error", "错误", report.errors) + renderGroups("warning", "警告", report.warnings);
    show(validationState(report), validationSummary(report), html, formatValidationReport(report));
  }
  show("idle", "尚未校验。保存成功后会自动校验当前改动。", "", "");

  async function validateOnce(trigger) {
    validateButton.disabled = true;
    show("running", trigger === "saved" ? "保存成功，正在校验当前改动…" : "正在校验当前改动…", "", "");
    try {
      render(await requestValidation(fetchImpl));
    } catch (error) {
      const summary = `校验未完成：${error.message}`;
      show("failed", summary, error.outputTail ? `<pre class="validation-output">${escapeHtml(error.outputTail)}</pre>` : "",
        [summary, error.outputTail].filter(Boolean).join("\n"));
    } finally {
      validateButton.disabled = false;
    }
  }

  // Saves during a run queue one more run, so the last save is always covered.
  async function run(trigger = "manual") {
    if (running) { again = true; return running; }
    running = (async () => {
      do { again = false; await validateOnce(trigger); } while (again);
    })();
    try { await running; } finally { running = null; }
  }

  validateButton.addEventListener("click", () => run("manual"));
  copyButton.addEventListener("click", async () => {
    try {
      await writeText(copyText);
      copyButton.textContent = "已复制";
    } catch (error) {
      copyButton.textContent = `复制失败：${error.message}`;
    }
  });
  return { run, render };
}

// Page entry: index.html loads this module next to #validation-panel; editor_panel.js dispatches
// `resource-saved` once per successful commit.
const page = createValidationPanel(document.getElementById("validation-panel"));
window.addEventListener("resource-saved", () => page.run("saved"));
