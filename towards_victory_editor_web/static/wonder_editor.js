import { fetchJson } from "./api.js";
import { createLatestLogView } from "./display.js";
import { createEditorPanel } from "./editor_panel.js";
import { resourceBase } from "./resource_state.js";
import { applyDraftToWonderPayload, draftValueForField } from "./wonder_drafts.js";

function originalFields(payload) {
  const fields = [];
  for (const [language, content] of Object.entries(payload.languages || {})) {
    for (const section of content.sections || []) for (const field of section.fields || []) {
      fields.push({ scope: "localization", language, key: field.key, value: field.original_value });
    }
  }
  for (const section of payload.mechanics?.sections || []) for (const field of section.fields || []) {
    fields.push({ scope: "mechanics", key: field.key, value: field.original_value });
  }
  return fields;
}

function selectionId(resource, preferred) {
  return resource.draft.wonders.some(wonder => wonder.id === preferred) ? preferred : resource.draft.initial_wonder_id;
}

export function createWonderEditor({ state, elements, dirtyCount, draftHasChanges,
  currentId, setCurrent, hydrate, invalidateDesigns, syncSelection, render, updateStatus, showToast }) {
  const log = createLatestLogView(elements.logOutput);
  let selectedId = null;
  let detailError = null;
  const originals = new Map();
  let refreshWarnings = [];

  function diagnostic(message = "") {
    log.diagnostic([...refreshWarnings, message].filter(Boolean).join("\n"));
  }

  function renderLog() {
    log.render();
    elements.copyLogButton.disabled = !log.text;
    elements.retryDetailButton.hidden = !detailError;
  }

  function reportError(error, label, { keepReport = false } = {}) {
    if (typeof error.log_text === "string") log.set(error.log_text);
    if (!keepReport) log.report(error);
    const message = label + ": " + error.message;
    diagnostic("[error] " + message);
    updateStatus(message, "error");
    renderLog();
    showToast(message, "error");
  }

  function acceptResource(payload, wonders) {
    originals.clear();
    refreshWarnings = [];
    state.resource.replace({ base: resourceBase(payload), saved: { wonders, pageDrafts: {} } });
    invalidateDesigns();
  }

  function displayWonder(payload) {
    detailError = null;
    diagnostic();
    if (payload) originals.set(payload.summary.id, originalFields(payload));
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
    await panel.sync();
  }

  async function refreshKeepingDrafts() {
    let refreshed = false;
    updateStatus("正在同步其他编辑器的变更，保留草稿", "working");
    try {
      await state.resource.run("loading", async () => {
        const resource = await fetchJson("api/resources/editor.wonder");
        const id = selectionId(resource, currentId() ?? selectedId);
        const ids = new Set(Object.keys(state.pageDrafts).map(Number));
        if (id != null) ids.add(id);
        // Read every drafted page as well as the visible one so conflicts cannot hide on another page.
        const details = await Promise.all([...ids].map(async wonderId =>
          hydrate(await fetchJson("api/wonder-localization/wonders/" + wonderId))));
        return { resource, id, details };
      }, { apply: ({ resource, id, details }) => {
        const pageDrafts = state.pageDrafts;
        const warnings = [];
        for (const wonder of details) {
          const fields = originalFields(wonder), wonderId = wonder.summary.id;
          for (const old of originals.get(wonderId) || []) {
            if (draftValueForField(pageDrafts[wonderId], old) === undefined) continue;
            const value = fields.find(field => field.scope === old.scope && field.language === old.language && field.key === old.key)?.value;
            if (old.value !== value) warnings.push(`[warning] 原值已在其他编辑器中改变：${wonderId} / ${old.language || old.scope} / ${old.key}: ${JSON.stringify(old.value)} → ${JSON.stringify(value)}；保留用户草稿`);
          }
          originals.set(wonderId, fields);
        }
        const wonders = resource.draft.wonders;
        state.resource.replace({ base: resourceBase(resource), saved: { wonders, pageDrafts: {} }, draft: { wonders, pageDrafts } });
        refreshed = true;
        // Reapply name/level previews for all drafted list entries, including hidden pages.
        for (const wonder of details) {
          const preview = applyDraftToWonderPayload(wonder, pageDrafts[wonder.summary.id]);
          Object.assign(state.resource.draft.wonders.find(item => item.id === wonder.summary.id), preview);
        }
        invalidateDesigns();
        selectedId = id;
        state.title = resource.draft.title;
        refreshWarnings = warnings;
        log.set(resource.draft.log_text);
        displayWonder(details.find(wonder => wonder.summary.id === id) || null);
        updateStatus(warnings.length ? "已同步，草稿已保留；原值冲突见日志" : "已同步，草稿已保留");
      } });
    } catch (error) {
      reportError(error, refreshed ? "已同步并保留草稿，但页面更新失败" : "同步失败，原状态与草稿已保留", { keepReport: true });
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
      const id = selectionId(resource, currentId() ?? selectedId);
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
    refreshKeepingDrafts,
    onError: reportError,
  });
  elements.retryDetailButton.addEventListener("click", () => {
    if (detailError) void loadDetail(detailError.wonderId, null, detailError.saved);
  });
  return { load: panel.load, save: panel.save, select, log, renderLog };
}
