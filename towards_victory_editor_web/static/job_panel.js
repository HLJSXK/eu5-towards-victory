import { fetchJson } from "./api.js";
import { JobPoller } from "./resource_state.js";
import { createLogView, createStatusView, escapeHtml, formatJobFiles, statusLabel } from "./display.js";

export function createJobPanel({ root, prefix, onChange, allowCancel = false, delay = 700 }) {
  root.innerHTML = `
    <div class="job-actions">
      ${allowCancel ? `<button id="${escapeHtml(prefix)}-cancel" type="button" disabled>取消作业</button>` : ""}
      <button id="${escapeHtml(prefix)}-poll-retry" type="button" hidden>重试查询</button>
      <button id="${escapeHtml(prefix)}-poll-stop" type="button" hidden>停止跟踪</button>
      <span id="${escapeHtml(prefix)}-status" class="job-status" role="status">就绪</span>
    </div>
    <p id="${escapeHtml(prefix)}-identity" class="job-identity"></p>
    <pre id="${escapeHtml(prefix)}-log" class="job-log"></pre>
    <details id="${escapeHtml(prefix)}-files" hidden>
      <summary>作业输入和输出</summary>
      <pre id="${escapeHtml(prefix)}-file-report" class="job-log"></pre>
    </details>`;
  const element = (suffix) => document.getElementById(`${prefix}-${suffix}`);
  const log = createLogView(element("log"));
  const status = createStatusView(element("status"));
  let cancelError = "", cancelling = false, detachedJobId = null;
  const poller = new JobPoller({
    delay,
    fetchJob: (id, cursor) => fetchJson(`/api/jobs/${id}?after_line=${cursor}`),
    onUpdate: renderJob,
    onError: renderPollError,
  });
  function changed() {
    if (allowCancel) element("cancel").disabled = !(poller.active || detachedJobId === poller.jobId) || cancelling;
    onChange();
  }
  function renderJob(job) {
    const operation = job.operation;
    detachedJobId = null;
    // A failed cancel request only matters while the job can still be cancelled.
    if (!poller.active) cancelError = "";
    let message = statusLabel(operation.status);
    if (job.outputs_may_be_partial) message += operation.interrupted
      ? " — 作业已中断，正式输出可能部分发布，请核对文件及保留的备份"
      : " — 正式输出需人工核对";
    if (operation.error) message += `: ${operation.error}`;
    if (cancelError) message += ` — ${cancelError}`;
    status.set(message, operation.error || cancelError ? "error" : "default");
    log.set(job.lines.join("\n"));
    element("poll-retry").hidden = true;
    element("poll-stop").hidden = true;
    const report = formatJobFiles(job);
    element("files").hidden = !report;
    element("file-report").textContent = report;
    element("identity").textContent = `作业 / 操作 ID: ${operation.id}${job.returncode == null ? "" : `；退出码: ${job.returncode}`}${operation.persistence_error ? `；记录写入失败: ${operation.persistence_error}` : ""}`;
    changed();
  }
  function renderPollError(error, retrying) {
    let message = poller.active
      ? `作业状态查询失败${retrying ? "，正在重试" : "，可重试或停止跟踪"}`
      : `已停止跟踪作业 ${poller.jobId}，服务端结果未知${detachedJobId === poller.jobId ? "，可能仍在运行，可取消" : ""}`;
    if (error) message += `: ${error.message}`;
    if (cancelError) message += ` — ${cancelError}`;
    status.set(message, "error");
    element("poll-retry").hidden = !poller.active;
    element("poll-stop").hidden = !poller.active;
    changed();
  }
  element("poll-retry").addEventListener("click", () => poller.poll());
  element("poll-stop").addEventListener("click", () => {
    poller.stop();
    if (allowCancel) detachedJobId = poller.jobId;
    renderPollError(poller.error, false);
  });
  if (allowCancel) element("cancel").addEventListener("click", async () => {
    const jobId = poller.jobId, generation = poller.generation, detached = !poller.active;
    if (!(poller.active || detachedJobId === jobId) || cancelling) return;
    cancelling = true;
    cancelError = "";
    let accepted = false;
    try {
      changed();
      const job = await fetchJson(`/api/jobs/${jobId}/cancel`, { method: "POST" });
      accepted = true;
      if (detached ? detachedJobId === jobId && poller.jobId === jobId : poller.isCurrent(jobId, generation) && poller.active) {
        if (detached) poller.start(job);
        else poller.accept(job, generation);
      }
    } catch (error) {
      if (poller.jobId === jobId && (detached || poller.isCurrent(jobId, generation))) {
        cancelError = `${accepted ? "取消请求已受理，但页面更新失败" : "取消失败"}: ${error.message}`;
        status.set(cancelError, "error");
        log.append(`\n[error] ${cancelError}\n`);
      }
    } finally {
      cancelling = false;
      changed();
    }
  });
  return {
    poller, log, status,
    start(job) { cancelError = ""; detachedJobId = null; poller.start(job); },
    // Synchronous callers (the generator panel) have no job to poll but still report the same
    // job-shaped file list through formatJobFiles rather than a second renderer.
    files(job) {
      const report = formatJobFiles(job);
      element("files").hidden = !report;
      element("file-report").textContent = report;
    },
    error(error) { status.set(error.message, "error"); log.append(`\n[error] ${error.message}\n`); log.report(error); },
  };
}
