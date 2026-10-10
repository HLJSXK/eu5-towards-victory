import { fetchJson } from "./api.js";
import { createLogView, createStatusView } from "./display.js";

function diffValue(value) {
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
      for (const item of preview.diff) {
        const row = document.createElement("tr");
        const target = [item.path, item.id, item.field || (!item.id ? "文件摘要" : "")].filter(Boolean).join(" / ");
        for (const text of [target, diffValue(item.before), diffValue(item.after)]) {
          const cell = document.createElement("td");
          cell.textContent = text;
          row.appendChild(cell);
        }
        tbody.appendChild(row);
      }
      dialog.querySelector(".diff-summary").textContent = preview.diff.length
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

export function createEditorPanel({ prefix, resourceId, resource, request, apply }) {
  const log = createLogView(document.getElementById(`${prefix}-log`));
  const status = createStatusView(document.getElementById(`${prefix}-status`));
  const diff = createDiffView(document.getElementById(`${prefix}-preview`));
  const url = `api/resources/${resourceId}`;
  function error(err) {
    if (typeof err.log_text === "string") log.set(err.log_text);
    log.append(`\n[error] ${err.message}\n`);
    log.report(err);
    status.set(`请求失败，草稿已保留: ${err.message}`, "error");
  }
  async function load({ confirmDirty = false } = {}) {
    if (resource.busy) return;
    if (confirmDirty && resource.dirty && !window.confirm("重新加载会丢弃未保存的修改，继续吗？")) return;
    status.set("正在加载", "working");
    try {
      await resource.run("loading", () => fetchJson(url), { apply });
      status.set("已加载");
    } catch (err) { error(err); }
  }
  async function save() {
    if (resource.busy) return;
    status.set("正在获取预览", "working");
    try {
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
        return fetchJson(`${url}/commit`, options);
      }, { apply: (payload) => {
        if (!payload) return;
        apply(payload);
        log.report(payload);
        log.append("\n[ok] 已保存。\n");
        status.set("已保存");
      } });
    } catch (err) { error(err); }
  }
  document.getElementById(`${prefix}-save-btn`).addEventListener("click", save);
  document.getElementById(`${prefix}-reload-btn`).addEventListener("click", () => load({ confirmDirty: true }));
  return { log, status, load, save };
}
