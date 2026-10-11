import { setControlsBusy } from "./resource_state.js";

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

export function createLogView(node) {
  return {
    set(text) { node.textContent = text || ""; },
    append(text) {
      node.textContent += text;
      node.scrollTop = node.scrollHeight;
    },
    report(payload) {
      const text = formatOperationReport(payload);
      if (text) this.append(`\n${text}\n`);
    },
  };
}

export function createStatusView(node) {
  return {
    set(text, kind = "default") {
      node.textContent = text;
      node.dataset.kind = kind;
    },
  };
}

// Used by editors that show one operation report alongside the server log.
export function createLatestLogView(node) {
  let server = "", report = "", diagnostic = "";
  const view = createLogView(node);
  const log = {
    get text() { return [server, report, diagnostic].filter(Boolean).join("\n"); },
    set(text) { server = text || ""; log.render(); },
    report(payload) { report = formatOperationReport(payload); diagnostic = ""; log.render(); },
    diagnostic(text) { diagnostic = text; log.render(); },
    reset(text) { server = text || ""; report = diagnostic = ""; log.render(); },
    render() { view.set(log.text || "[server] 暂无新日志"); },
  };
  return log;
}

export function renderTabs(root, { items, active, key, label, select, busy }) {
  root.innerHTML = "";
  for (const item of items) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `tab${key(item) === active ? " active" : ""}`;
    button.textContent = label(item);
    setControlsBusy([button], busy());
    button.addEventListener("click", () => { if (!busy()) select(key(item)); });
    root.appendChild(button);
  }
}

export function statusLabel(status) {
  return ({ queued: "排队中", running: "运行中", cancelling: "正在取消", cancelled: "已取消",
    succeeded: "已完成", failed: "失败", pending: "等待执行", skipped: "已跳过", incomplete: "未完全恢复" })[status] || status;
}

export function formatOperationReport(payload) {
  const generation = payload.generation;
  const id = payload.operation_id || payload.operation?.id || generation?.operation_id;
  const lines = [];
  if (id) lines.push(`操作 ID: ${id}`);
  if (payload.operation?.status) lines.push(`操作状态: ${statusLabel(payload.operation.status)}`);
  const persistenceError = payload.persistence_error || payload.operation?.persistence_error;
  if (persistenceError) lines.push(`操作记录写入失败: ${persistenceError}`);
  if (generation) {
    lines.push(`生成结果: ${statusLabel(generation.status)}`);
    if (generation.error) lines.push(generation.error);
    for (const step of generation.steps || []) {
      lines.push(`  ${step.id}: ${statusLabel(step.status)}${step.returncode == null ? "" : ` (退出码 ${step.returncode})`}${step.duration_seconds == null ? "" : ` / ${step.duration_seconds}s`}`);
    }
    for (const artifact of generation.artifacts || []) {
      lines.push(`  ${artifact.path}: ${artifact.role === "deleted" ? "已删除" : artifact.changed ? "已变化" : "未变化"}`);
    }
    for (const path of generation.missing_outputs || []) lines.push(`缺失输出: ${path}`);
    for (const item of generation.output_validation || []) if (!item.valid) lines.push(`校验失败: ${item.path}: ${item.error}`);
    if (generation.rollback) {
      lines.push(`恢复结果: ${statusLabel(generation.rollback.status)}`);
      lines.push(...(generation.rollback.errors || []));
    }
  }
  return lines.join("\n");
}

export function formatJobFiles(job) {
  const operation = job.operation;
  const files = [];
  if (operation.resource_ids.length) files.push(`资源: ${operation.resource_ids.join(", ")}`);
  if (job.formal_output_changes.length) files.push("正式输出在暂存区外发生变化（需核对）:", ...job.formal_output_changes.map((path) => `  ${path}`));
  if (job.staging_extra_files.length) files.push("不参与发布的中间文件:", ...job.staging_extra_files.map((path) => `  ${path}`));
  if (job.source_snapshots.length) files.push("输入:", ...job.source_snapshots.map((source) => `  ${source.path}${source.sha256 === "missing" ? "（可选，缺失）" : ""}`));
  const artifacts = new Map(job.artifacts.map((artifact) => [artifact.path, artifact]));
  const errors = new Map((job.metadata.output_validation || []).filter((item) => !item.valid).map((item) => [item.path, item.error]));
  if (job.declared_outputs.length) files.push("输出:", ...job.declared_outputs.map((path) => {
    const artifact = artifacts.get(path);
    const status = artifact ? artifact.role === "deleted" ? "已删除" : artifact.changed ? "已变化" : "未变化"
      : job.missing_outputs.includes(path) ? "缺失" : ["queued", "running", "cancelling"].includes(operation.status) ? "等待生成" : "未生成";
    return `  ${path}（${status}）${errors.has(path) ? `: ${errors.get(path)}` : ""}`;
  }));
  if (job.publication_rollback_failed) files.push("发布恢复失败，需人工核对保留的备份。");
  return files.join("\n");
}
