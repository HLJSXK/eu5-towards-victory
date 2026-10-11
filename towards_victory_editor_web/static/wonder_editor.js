import { fetchJson } from "./api.js";
import { createLatestLogView } from "./display.js";
import { createEditorPanel } from "./editor_panel.js";
import { resourceBase } from "./resource_state.js";

export function createWonderEditor({ state, elements, dirtyCount, draftHasChanges,
  currentId, setCurrent, hydrate, invalidateDesigns, syncSelection, render, updateStatus, showToast }) {
  const log = createLatestLogView(elements.logOutput);
  let selectedId = null;
  let detailError = null;

  function renderLog() {
    log.render();
    elements.copyLogButton.disabled = !log.text;
    elements.retryDetailButton.hidden = !detailError;
  }

  function reportError(error, label, { keepReport = false } = {}) {
    if (typeof error.log_text === "string") log.set(error.log_text);
    if (!keepReport) log.report(error);
    const message = label + ": " + error.message;
    log.diagnostic("[error] " + message);
    updateStatus(message, "error");
    renderLog();
    showToast(message, "error");
  }

  function acceptResource(payload, wonders) {
    state.resource.replace({ base: resourceBase(payload), saved: { wonders, pageDrafts: {} } });
    invalidateDesigns();
  }

  function displayWonder(payload) {
    detailError = null;
    log.diagnostic("");
    setCurrent(payload);
    syncSelection();
    render();
  }

  async function loadDetail(wonderId, payload, saved = false) {
    if (state.busy || wonderId === null) return;
    updateStatus(saved ? "已保存，正在加载详情" : "正在切换奇观", "working");
    try {
      await state.resource.run("loading", async () => hydrate(payload || await fetchJson("api/wonder-localization/wonders/" + wonderId)), {
        apply: (wonder) => {
          selectedId = wonderId;
          updateStatus(saved ? "已保存" : wonder.status || "已加载");
          displayWonder(wonder);
        },
      });
    } catch (error) {
      detailError = { wonderId, saved };
      reportError(error, saved ? "已保存，但详情加载失败" : "详情加载失败", { keepReport: true });
    }
  }

  async function select(wonderId) {
    if (state.busy || currentId() === wonderId) return;
    await loadDetail(wonderId);
  }

  const panel = createEditorPanel({
    prefix: "wonder", resourceId: "editor.wonder", resource: state.resource,
    log, status: { set: updateStatus },
    buttons: { save: elements.saveButton, reload: elements.reloadButton },
    beforeSave() {
      if (!state.currentWonder) return false;
      selectedId = currentId();
      return true;
    },
    request: () => ({ regenerate: true, current_wonder_id: selectedId, base: state.resource.base,
      wonders: Object.entries(state.pageDrafts).filter(([, draft]) => draftHasChanges(draft))
        .map(([id, draft]) => ({ wonder_id: Number(id), ...draft })) }),
    confirmReload: () => window.confirm("重新加载会放弃全部 " + dirtyCount() + " 个奇观页面的未保存编辑，继续吗？"),
    async loadRequest({ initial = false } = {}) {
      const resource = await fetchJson("api/resources/editor.wonder");
      const id = currentId() ?? selectedId ?? resource.draft.initial_wonder_id;
      // Bootstrap publishes the list before fetching detail; reload replaces both together.
      if (initial) return { resource, wonder: null, id, initial };
      const wonder = id == null ? null : await hydrate(await fetchJson("api/wonder-localization/wonders/" + id));
      return { resource, wonder, id };
    },
    applyLoaded({ resource, wonder, id }) {
      acceptResource(resource, resource.draft.wonders);
      selectedId = id;
      state.title = resource.draft.title;
      log.reset(resource.draft.log_text);
      displayWonder(wonder);
    },
    onLoaded() { updateStatus("已加载"); },
    afterLoad: ({ initial, id }) => initial ? loadDetail(id) : undefined,
    apply(payload) {
      // The commit has succeeded. Catalog hydration must never restore the old base/draft.
      acceptResource(payload, payload.wonders);
      setCurrent(null);
      detailError = null;
    },
    onSaved(payload) {
      if (typeof payload.log_text === "string") log.set(payload.log_text);
      log.report(payload);
      updateStatus("已保存");
      render();
      showToast("已保存", "success");
    },
    afterSave: (payload) => loadDetail(selectedId, payload.wonder, true),
    onError: reportError,
  });
  elements.retryDetailButton.addEventListener("click", () => {
    if (detailError) void loadDetail(detailError.wonderId, null, detailError.saved);
  });
  return { load: panel.load, save: panel.save, select, log, renderLog };
}
