import { fetchJson } from "./api.js";
import { createLogView, createStatusView } from "./display.js";

function diffValue(value, item, side) {
  if (item[side + "_present"] === false) return "（不存在）";
  if (item.value_kind === "text" || item.value_kind === "script") return value;
  if (item.value_kind === "structure") return JSON.stringify(value, null, 2);
  return value === undefined ? "—" : JSON.stringify(value);
}

export function createDiffView(root) {
  root.innerHTML = `<dialog class="diff-dialog" aria-label="保存前预览">
    <h2>确认保存以下变更</h2><p class="diff-summary"></p>
    <div class="diff-scroll"><table><thead><tr><th>文件 / 条目 / 字段</th><th>原值</th><th>新值</th></tr></thead><tbody></tbody></table></div>
    <div class="actions"><button type="button" data-confirm>确认保存</button><button type="button" data-cancel>返回编辑</button></div>
  </dialog>`;
  const dialog = root.querySelector("dialog");
  return {
    confirm(preview) {
      const tbody = dialog.querySelector("tbody");
      tbody.innerHTML = "";
      for (const item of [...preview.diff, ...(preview.file_diff || [])]) {
        const row = document.createElement("tr");
        const target = [item.path, item.wonder_id, item.wonder_key, item.language, item.id,
          item.field || (!item.id ? "文件摘要" : "")].filter(value => value !== undefined && value !== null && value !== "").join(" / ");
        for (const text of [target, diffValue(item.before, item, "before"), diffValue(item.after, item, "after")]) {
          const cell = document.createElement("td");
          if (item.value_kind) cell.className = "diff-value";
          cell.textContent = text;
          row.appendChild(cell);
        }
        tbody.appendChild(row);
      }
      dialog.querySelector(".diff-summary").textContent = preview.generation_plan
        ? `${preview.diff.length} 个字段变更；${preview.file_diff.length} 个源文件；${preview.generation_plan.steps.length} 个生成步骤。生成产物的实际文件摘要在保存后报告。`
        : preview.diff.length
        ? `${preview.diff.length} 项变更；确认后保存并重新生成。` : "没有内容差异；确认后仍执行保存和重新生成。";
      return new Promise((resolve) => {
        const confirm = dialog.querySelector("[data-confirm]"), cancel = dialog.querySelector("[data-cancel]");
        const finish = (accepted) => {
          confirm.removeEventListener("click", accept);
          cancel.removeEventListener("click", reject);
          dialog.removeEventListener("cancel", escape);
          dialog.close();
          resolve(accepted);
        };
        const accept = () => finish(true), reject = () => finish(false);
        const escape = (event) => { event.preventDefault(); finish(false); };
        confirm.addEventListener("click", accept);
        cancel.addEventListener("click", reject);
        dialog.addEventListener("cancel", escape);
        dialog.showModal();
      });
    },
  };
}

export function createEditorPanel({ prefix, resourceId, resource, request, apply,
  log = createLogView(document.getElementById(`${prefix}-log`)),
  status = createStatusView(document.getElementById(`${prefix}-status`)),
  buttons = { save: document.getElementById(`${prefix}-save-btn`), reload: document.getElementById(`${prefix}-reload-btn`) },
  beforeSave = () => true, beforeLoad = () => {},
  confirmReload = () => window.confirm("重新加载会丢弃未保存的修改，继续吗？"),
  loadRequest = () => fetchJson(`api/resources/${resourceId}`), applyLoaded = apply,
  onLoaded = () => status.set("已加载"),
  afterLoad = async () => {},
  onSaved = (payload) => { log.report(payload); log.append("\n[ok] 已保存。\n"); status.set("已保存"); },
  afterSave = async () => {}, refreshKeepingDrafts = null, onError,
}) {
  const diff = createDiffView(document.getElementById(`${prefix}-preview`));
  const url = `api/resources/${resourceId}`;
  let syncPending = false;
  // Another editor wrote files in this base: refresh without discarding drafts once idle.
  async function sync() {
    if (!syncPending || resource.busy) return;
    syncPending = false;
    await refreshKeepingDrafts();
    await sync();
  }
  if (refreshKeepingDrafts) {
    window.addEventListener("resource-committed", ({ detail }) => {
      if (detail.resourceId === resourceId || !detail.writtenPaths.some(path => Object.hasOwn(resource.base, path))) return;
      syncPending = true;
      void sync();
    });
  }
  function error(err, label) {
    if (typeof err.log_text === "string") log.set(err.log_text);
    log.append(`\n[error] ${label}: ${err.message}\n`);
    log.report(err);
    status.set(`${label}: ${err.message}`, "error");
  }
  async function load({ confirmDirty = false, context } = {}) {
    if (resource.busy) return;
    let loaded;
    try {
      beforeLoad();
      if (confirmDirty && resource.dirty && !confirmReload()) return;
      status.set("正在加载", "working");
      loaded = await resource.run("loading", () => loadRequest(context), { apply: (payload) => { applyLoaded(payload); onLoaded(payload); } });
    } catch (err) { (onError || error)(err, resource.dirty ? "加载失败，草稿已保留" : "加载失败"); }
    if (loaded) await afterLoad(loaded);
    await sync();
  }
  async function save() {
    if (resource.busy) return;
    let committed;
    try {
      if (beforeSave() === false) return;
      status.set("正在获取预览", "working");
      // Freeze one serialized request through preview, confirmation and commit.
      // Preview never changes the resource base or marks the draft as saved.
      await resource.run("saving", async () => {
        const options = { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(request()) };
        const preview = await fetchJson(`${url}/preview`, options);
        status.set("请确认变更", "working");
        if (!await diff.confirm(preview)) {
          status.set("已返回编辑，草稿已保留");
          return null;
        }
        status.set("正在保存并重新生成", "working");
        const payload = await fetchJson(`${url}/commit`, options);
        if (payload.written_paths?.length) {
          window.dispatchEvent(new CustomEvent("resource-committed", {
            detail: { resourceId, writtenPaths: payload.written_paths },
          }));
        }
        return payload;
      }, { apply: (payload) => {
        if (!payload) return;
        committed = payload;
        apply(payload);
        onSaved(payload);
      } });
    } catch (err) {
      if (committed) log.report(committed);
      (onError || error)(err, committed ? "已保存，但页面更新失败" : "保存失败，草稿已保留", { keepReport: !!committed });
    }
    if (committed) window.dispatchEvent(new CustomEvent("resource-saved", { detail: { resourceId } }));
    if (committed) await afterSave(committed);
    await sync();
  }
  buttons.save.addEventListener("click", save);
  buttons.reload.addEventListener("click", () => load({ confirmDirty: true }));
  return { log, status, load, save, sync };
}
