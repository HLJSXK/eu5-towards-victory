import { fetchJson } from "./api.js";
import { ResourceState, resourceBase, setControlsBusy, setToolDirty } from "./resource_state.js";
import { renderTabs } from "./display.js";
import { createEditorPanel } from "./editor_panel.js";

const state = {
  resource: new ResourceState({
    saved: { groups: [], edits: {} },
    onChange: () => { syncControls(); updateRenderedTable(); },
    onDirtyChange: (dirty) => setToolDirty("cost-reward", dirty),
  }),
  get groups() { return this.resource.draft.groups; },
  get edits() { return this.resource.draft.edits; },
  get base() { return this.resource.base; },
  activeKey: null,
  filterText: "",
  onlyDirty: false,
};

const ROW_KEY_SEPARATOR = "\u001f";
const LONG_TEXT_LIMIT = 90;
const VALUE_NOTES = {
  country_reward: "One-shot unit; costs use the negative of the matching reward.",
  local_reward: "One-shot unit; costs use the negative of the matching reward.",
  character_reward: "One-shot unit; costs use the negative of the matching reward.",
  country_modifier: "Persistent modifier unit; numeric values are per-level increments; booleans are unscaled unlock units.",
  local_modifier: "Persistent modifier unit; numeric values are per-level increments.",
};
const VALUE_SPECIAL_NOTES = {
  [`country_reward${ROW_KEY_SEPARATOR}government_power`]: "Automatically maps to the government-type-appropriate government power value.",
  [`country_reward${ROW_KEY_SEPARATOR}inflation`]: "Inverted direction: a reward reduces inflation; a cost increases it.",
  [`country_modifier${ROW_KEY_SEPARATOR}monthly_towards_axis`]: "Represents monthly_towards_* value-movement modifiers.",
};

export function rowKey(categoryKey, tokenId) {
  return `${categoryKey}${ROW_KEY_SEPARATOR}${tokenId}`;
}

export function dirtyRowKeys(edits = {}) {
  const keys = new Set();
  for (const [categoryKey, tokens] of Object.entries(edits || {})) {
    for (const [tokenId, fields] of Object.entries(tokens || {})) {
      if (fields && Object.keys(fields).length) keys.add(rowKey(categoryKey, tokenId));
    }
  }
  return keys;
}

export function isTokenDirty(edits, categoryKey, tokenId) {
  return dirtyRowKeys(edits).has(rowKey(categoryKey, tokenId));
}

function tokenSearchText(token) {
  return [token.id, token.loc?.en, token.loc?.zh].filter(value => value !== undefined && value !== null)
    .join(" ").toLowerCase();
}

export function filterTokens(tokens, query = "", onlyDirty = false, categoryKey = "", edits = {}) {
  const needle = String(query || "").trim().toLowerCase();
  const dirty = onlyDirty ? dirtyRowKeys(edits) : null;
  return (tokens || []).filter((token) => {
    if (dirty && !dirty.has(rowKey(categoryKey, token.id))) return false;
    return !needle || tokenSearchText(token).includes(needle);
  });
}

export function valueNoteFor(categoryKey, tokenId, value) {
  const special = VALUE_SPECIAL_NOTES[rowKey(categoryKey, tokenId)];
  if (special) return special;
  if (categoryKey === "country_modifier" && typeof value === "boolean") {
    return "Boolean values are unscaled unlock units.";
  }
  return VALUE_NOTES[categoryKey] || "";
}

export async function copyText(text) {
  if (globalThis.navigator?.clipboard?.writeText) return globalThis.navigator.clipboard.writeText(String(text ?? ""));
  const area = document.createElement("textarea");
  area.value = String(text ?? "");
  area.setAttribute("readonly", "");
  area.className = "copy-fallback";
  document.body.appendChild(area);
  area.select();
  document.execCommand("copy");
  area.remove();
}

let editor;
if (typeof document !== "undefined") {
  editor = createEditorPanel({
    prefix: "cr", resourceId: "editor.cost_reward", resource: state.resource,
    request: () => ({ edits: state.edits, base: state.base }),
    apply: applyBootstrapPayload,
    refreshKeepingDrafts,
  });
}

function findToken(groups, categoryKey, tokenId) {
  return groups.find((group) => group.key === categoryKey)?.tokens.find((item) => item.id === tokenId);
}

async function refreshKeepingDrafts() {
  editor.status.set("正在同步其他编辑器的变更，保留草稿", "working");
  try {
    await state.resource.run("loading", () => fetchJson("api/resources/editor.cost_reward"), { apply: (payload) => {
      const oldSaved = state.resource.saved.groups, edits = state.edits, warnings = [];
      const groups = structuredClone(payload.draft.groups), kept = {};
      for (const [categoryKey, tokens] of Object.entries(edits)) {
        for (const [tokenId, fields] of Object.entries(tokens)) {
          const token = findToken(groups, categoryKey, tokenId);
          if (!token) {
            warnings.push(`[warning] 条目已在其他编辑器中删除，草稿已丢弃：${categoryKey} / ${tokenId}`);
            continue;
          }
          for (const [field, value] of Object.entries(fields)) {
            const before = findToken(oldSaved, categoryKey, tokenId)?.[field];
            if (before !== token[field]) warnings.push(`[warning] 原值已在其他编辑器中改变：${categoryKey} / ${tokenId} / ${field}: ${JSON.stringify(before)} → ${JSON.stringify(token[field])}；保留用户草稿`);
            token[field] = value;
            ((kept[categoryKey] ||= {})[tokenId] ||= {})[field] = value;
          }
        }
      }
      state.resource.replace({ base: resourceBase(payload), saved: { ...payload.draft, edits: {} },
        draft: { ...payload.draft, groups, edits: kept } });
      editor.log.set(payload.draft.log || "");
      if (warnings.length) editor.log.append(`\n${warnings.join("\n")}\n`);
      renderCategoryTabs();
      renderPanels();
      editor.status.set(warnings.length ? "已同步，草稿已保留；原值冲突见日志" : "已同步，草稿已保留");
    } });
  } catch (error) {
    editor.log.append(`\n[error] 同步失败，原状态与草稿已保留: ${error.message}\n`);
    editor.status.set(`同步失败，原状态与草稿已保留: ${error.message}`, "error");
  }
}

function syncControls() {
  setControlsBusy(document.querySelectorAll("#cr-tabs button, #panels input, #panels textarea, #panels select, #cr-filter, #cr-only-dirty, #cr-save-btn, #cr-reload-btn"), state.resource.busy);
}

function stageEdit(categoryKey, tokenId, field, rawValue) {
  state.resource.mutate((draft) => {
    const token = draft.groups.find((group) => group.key === categoryKey).tokens.find((item) => item.id === tokenId);
    const original = state.resource.saved.groups.find((group) => group.key === categoryKey).tokens.find((item) => item.id === tokenId)[field];
    draft.edits[categoryKey] ||= {};
    draft.edits[categoryKey][tokenId] ||= {};
    if (String(original ?? "") === String(rawValue)) {
      token[field] = original;
      delete draft.edits[categoryKey][tokenId][field];
      if (!Object.keys(draft.edits[categoryKey][tokenId]).length) delete draft.edits[categoryKey][tokenId];
      if (!Object.keys(draft.edits[categoryKey]).length) delete draft.edits[categoryKey];
    } else {
      token[field] = rawValue;
      draft.edits[categoryKey][tokenId][field] = rawValue;
    }
  });
}

function dirtyCountForGroup(group) {
  if (!group) return 0;
  const dirty = dirtyRowKeys(state.edits);
  return group.tokens.reduce((count, token) => count + (dirty.has(rowKey(group.key, token.id)) ? 1 : 0), 0);
}

function matchesFilter(token, categoryKey, dirty) {
  const needle = String(state.filterText || "").trim().toLowerCase();
  if (state.onlyDirty && !dirty.has(rowKey(categoryKey, token.id))) return false;
  return !needle || tokenSearchText(token).includes(needle);
}

function updateRenderedTable() {
  const group = state.groups.find((item) => item.key === state.activeKey);
  const table = document.querySelector("#panels table[data-cost-reward-table]");
  const count = document.getElementById("cr-dirty-count");
  if (!group || !table) return;
  const dirty = dirtyRowKeys(state.edits);
  if (count) count.textContent = `已改动 ${dirtyCountForGroup(group)} 行`;
  for (const row of table.tBodies[0]?.rows || []) {
    const tokenId = row.dataset.tokenId;
    const isDirty = dirty.has(rowKey(group.key, tokenId));
    row.classList.toggle("dirty-row", isDirty);
    const token = group.tokens.find((item) => String(item.id) === tokenId);
    row.hidden = !token || !matchesFilter(token, group.key, dirty);
  }
  const visible = [...(table.tBodies[0]?.rows || [])].filter((row) => !row.hidden).length;
  table.dataset.visibleRows = String(visible);
  const visibleCount = document.getElementById("cr-visible-count");
  if (visibleCount) visibleCount.textContent = `显示 ${visible} / ${group.tokens.length} 行`;
}

function renderFilterControls(group, panelsEl) {
  const controls = document.createElement("div");
  controls.className = "cost-reward-controls";

  const label = document.createElement("label");
  label.className = "cost-reward-search";
  label.textContent = "过滤 id / loc";
  const input = document.createElement("input");
  input.type = "search";
  input.id = "cr-filter";
  input.placeholder = "输入 id 或 loc 文本";
  input.value = state.filterText;
  input.addEventListener("input", () => {
    state.filterText = input.value;
    updateRenderedTable();
  });
  label.appendChild(input);
  controls.appendChild(label);

  const dirtyLabel = document.createElement("label");
  dirtyLabel.className = "cost-reward-only-dirty";
  const dirtyInput = document.createElement("input");
  dirtyInput.type = "checkbox";
  dirtyInput.id = "cr-only-dirty";
  dirtyInput.checked = state.onlyDirty;
  dirtyInput.addEventListener("change", () => {
    state.onlyDirty = dirtyInput.checked;
    updateRenderedTable();
  });
  dirtyLabel.append(dirtyInput, "仅显示已改动");
  controls.appendChild(dirtyLabel);

  const summary = document.createElement("span");
  summary.className = "cost-reward-summary";
  summary.id = "cr-dirty-count";
  controls.appendChild(summary);
  const visible = document.createElement("span");
  visible.className = "cost-reward-summary";
  visible.id = "cr-visible-count";
  controls.appendChild(visible);
  panelsEl.appendChild(controls);
  return group;
}

function renderCategoryTabs() {
  renderTabs(document.getElementById("cr-tabs"), {
    items: state.groups, active: state.activeKey,
    key: (group) => group.key,
    label: (group) => `${group.label_zh}（${group.tokens.length}）`,
    busy: () => state.resource.busy,
    select: (key) => {
      state.activeKey = key;
      renderCategoryTabs();
      renderPanels();
    },
  });
}

function appendReadonlyCell(tr, text) {
  const td = document.createElement("td");
  td.textContent = text || "";
  td.className = "readonly";
  tr.appendChild(td);
  return td;
}

function appendCopyButton(parent, text) {
  const button = document.createElement("button");
  button.type = "button";
  button.className = "copy-text-button";
  button.textContent = "复制";
  button.addEventListener("click", async () => {
    await copyText(text);
    button.textContent = "已复制";
    setTimeout(() => { button.textContent = "复制"; }, 1200);
  });
  parent.appendChild(button);
}

function appendExpandableReadonlyCell(tr, text) {
  const td = appendReadonlyCell(tr, "");
  td.classList.add("long-text-cell");
  const content = document.createElement("span");
  content.className = "long-text-content";
  content.textContent = text || "";
  td.appendChild(content);
  if (String(text || "").length > LONG_TEXT_LIMIT) {
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = "展开";
    details.append(summary);
    const expanded = document.createElement("div");
    expanded.className = "long-text-expanded";
    expanded.textContent = text;
    details.appendChild(expanded);
    td.appendChild(details);
  }
  appendCopyButton(td, text || "");
  return td;
}

function appendExpandableTextareaCell(tr, group, token) {
  const td = document.createElement("td");
  td.className = "long-text-cell editable-long-text";
  const textarea = document.createElement("textarea");
  textarea.rows = 2;
  textarea.value = token.completion_note || "";
  textarea.addEventListener("input", () => stageEdit(group.key, token.id, "completion_note", textarea.value));
  td.appendChild(textarea);
  const actions = document.createElement("div");
  actions.className = "long-text-actions";
  const expand = document.createElement("button");
  expand.type = "button";
  expand.className = "expand-text-button";
  expand.textContent = "展开";
  expand.addEventListener("click", () => {
    td.classList.toggle("expanded");
    expand.textContent = td.classList.contains("expanded") ? "收起" : "展开";
  });
  actions.appendChild(expand);
  const copyButton = document.createElement("button");
  copyButton.type = "button";
  copyButton.className = "copy-text-button";
  copyButton.textContent = "复制";
  copyButton.addEventListener("click", async () => {
    await copyText(textarea.value);
    copyButton.textContent = "已复制";
    setTimeout(() => { copyButton.textContent = "复制"; }, 1200);
  });
  actions.appendChild(copyButton);
  td.appendChild(actions);
  tr.appendChild(td);
  return td;
}

function renderRewardModifierTable(group) {
  const table = document.createElement("table");
  table.dataset.costRewardTable = "true";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["id", "value / unit or note", "loc.en", "loc.zh"].forEach((label) => {
    const th = document.createElement("th");
    th.textContent = label;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  group.tokens.forEach((token) => {
    const tr = document.createElement("tr");
    tr.dataset.tokenId = String(token.id);

    appendReadonlyCell(tr, token.id);

    const valueCell = document.createElement("td");
    const valueInput = document.createElement("input");
    if (typeof token.value === "boolean") {
      valueInput.type = "checkbox";
      valueInput.checked = token.value;
      valueInput.addEventListener("change", () => stageEdit(group.key, token.id, "value", valueInput.checked));
    } else {
      valueInput.type = "number";
      valueInput.step = "any";
      if (!group.key.endsWith("_modifier")) {
        valueInput.min = "0";
      }
      valueInput.value = token.value;
      valueInput.addEventListener("input", () => stageEdit(group.key, token.id, "value", valueInput.value));
    }
    valueCell.appendChild(valueInput);
    const note = document.createElement("small");
    note.className = "value-note";
    note.textContent = valueNoteFor(group.key, token.id, token.value);
    valueCell.appendChild(note);
    tr.appendChild(valueCell);

    appendReadonlyCell(tr, (token.loc && token.loc.en) || "");
    appendReadonlyCell(tr, (token.loc && token.loc.zh) || "");

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function renderOnActionTaskTable(group) {
  const table = document.createElement("table");
  table.dataset.costRewardTable = "true";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["id", "on_action", "category", "wired", "scope", "completion_note", "loc.en", "loc.zh"].forEach((label) => {
    const th = document.createElement("th");
    th.textContent = label;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  group.tokens.forEach((token) => {
    const tr = document.createElement("tr");
    tr.dataset.tokenId = String(token.id);

    appendReadonlyCell(tr, token.id);
    appendReadonlyCell(tr, token.on_action);
    appendReadonlyCell(tr, token.category);

    const wiredCell = document.createElement("td");
    const wiredInput = document.createElement("input");
    wiredInput.type = "checkbox";
    wiredInput.checked = !!token.wired;
    wiredInput.addEventListener("change", () => stageEdit(group.key, token.id, "wired", wiredInput.checked));
    wiredCell.appendChild(wiredInput);
    tr.appendChild(wiredCell);

    appendExpandableReadonlyCell(tr, token.scope);
    appendExpandableTextareaCell(tr, group, token);

    appendReadonlyCell(tr, (token.loc && token.loc.en) || "").classList.add("wrap-cell");
    appendReadonlyCell(tr, (token.loc && token.loc.zh) || "").classList.add("wrap-cell");

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function renderTriggerTaskTable(group) {
  const table = document.createElement("table");
  table.dataset.costRewardTable = "true";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["id", "trigger", "scope", "category", "comparison", "representative_threshold", "loc.en", "loc.zh"].forEach((label) => {
    const th = document.createElement("th");
    th.textContent = label;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  group.tokens.forEach((token) => {
    const tr = document.createElement("tr");
    tr.dataset.tokenId = String(token.id);

    appendReadonlyCell(tr, token.id);
    appendReadonlyCell(tr, token.trigger);
    appendExpandableReadonlyCell(tr, token.scope);
    appendReadonlyCell(tr, token.category);

    const comparisonCell = document.createElement("td");
    const comparisonSelect = document.createElement("select");
    ["gte", "lte", "boolean"].forEach((option) => {
      const opt = document.createElement("option");
      opt.value = option;
      opt.textContent = option;
      if (token.comparison === option) opt.selected = true;
      comparisonSelect.appendChild(opt);
    });
    comparisonCell.appendChild(comparisonSelect);
    tr.appendChild(comparisonCell);

    const thresholdCell = document.createElement("td");
    const thresholdInput = document.createElement("input");
    thresholdInput.type = "number";
    thresholdInput.step = "any";
    const isBoolean = token.comparison === "boolean";
    thresholdInput.value = isBoolean || token.representative_threshold === null || token.representative_threshold === undefined
      ? ""
      : token.representative_threshold;
    thresholdInput.disabled = isBoolean;
    thresholdInput.addEventListener("input", () =>
      stageEdit(group.key, token.id, "representative_threshold", thresholdInput.value)
    );
    thresholdCell.appendChild(thresholdInput);
    tr.appendChild(thresholdCell);

    comparisonSelect.addEventListener("change", () => {
      if (state.resource.busy) return;
      stageEdit(group.key, token.id, "comparison", comparisonSelect.value);
      if (comparisonSelect.value === "boolean") {
        thresholdInput.value = "";
        thresholdInput.disabled = true;
        stageEdit(group.key, token.id, "representative_threshold", "");
      } else {
        thresholdInput.disabled = false;
      }
    });

    appendReadonlyCell(tr, (token.loc && token.loc.en) || "").classList.add("wrap-cell");
    appendReadonlyCell(tr, (token.loc && token.loc.zh) || "").classList.add("wrap-cell");

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function renderTable(group) {
  if (group.key === "on_action_task") return renderOnActionTaskTable(group);
  if (group.key === "trigger_task") return renderTriggerTaskTable(group);
  return renderRewardModifierTable(group);
}

function renderPanels() {
  const panelsEl = document.getElementById("panels");
  panelsEl.innerHTML = "";
  const group = state.groups.find((g) => g.key === state.activeKey);
  if (!group) return;

  const heading = document.createElement("h2");
  heading.textContent = `${group.label_zh} / ${group.label_en}`;
  panelsEl.appendChild(heading);
  renderFilterControls(group, panelsEl);

  if (group.key === "on_action_task" || group.key === "trigger_task") {
    const notice = document.createElement("p");
    notice.className = "hint task-pool-notice";
    notice.textContent = "当前无机制消费此目录（见 docs/design/Cost_Reward_Unit_Concepts.md 第 6 节）。";
    panelsEl.appendChild(notice);
  }

  if (group.key.endsWith("_modifier")) {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent = "value 表示每提升一级所增加的持续 modifier 增量（非一次性数值），可以为负数（如花费类修正）。";
    panelsEl.appendChild(hint);
  }

  if (group.key.endsWith("_reward")) {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent = "本目录不单独存代价（cost）行：需要代价时，取本条 value 的相反数即可。";
    panelsEl.appendChild(hint);
  }

  if (group.key === "on_action_task") {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent =
      "wired = 该 on_action 是否已在 data/pulse_registry.yaml 中桥接；勾选/取消勾选只更新此处的记录状态，" +
      "并不会自动改写 pulse_registry.yaml —— 实际接入 on_action 仍需按需编辑该注册表并重新运行 " +
      "scripts/in_game/common/on_action/gen_tv_pulse_registry.py。本目录不存奖励，只记录任务如何被检测到。";
    panelsEl.appendChild(hint);
  }

  if (group.key === "trigger_task") {
    const hint = document.createElement("p");
    hint.className = "hint";
    hint.textContent =
      "representative_threshold 只是示意性的“1 unit”式起始值，供未来玩法调优，并非里程碑式的最终数值。" +
      "comparison 为 boolean 时 representative_threshold 必须留空；为 gte/lte 时必须填写数值。";
    panelsEl.appendChild(hint);
  }

  if (group.tokens.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "当前没有属于此类别的 token。";
    panelsEl.appendChild(empty);
    return;
  }

  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  const tableRenderStart = globalThis.performance?.now?.() ?? Date.now();
  const table = renderTable(group);
  table.dataset.renderMs = String((globalThis.performance?.now?.() ?? Date.now()) - tableRenderStart);
  wrap.appendChild(table);
  panelsEl.appendChild(wrap);
  syncControls();
  updateRenderedTable();
}

function applyBootstrapPayload(payload) {
  const draft = payload.draft;
  state.resource.replace({ base: resourceBase(payload), saved: { ...draft, edits: {} } });
  if (!state.activeKey || !state.groups.some((g) => g.key === state.activeKey)) {
    state.activeKey = state.groups.length ? state.groups[0].key : null;
  }
  editor.log.set(draft.log || "");
  renderCategoryTabs();
  renderPanels();
}

if (editor) void editor.load();
