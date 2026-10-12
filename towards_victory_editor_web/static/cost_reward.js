import { fetchJson } from "./api.js";
import { ResourceState, resourceBase, setControlsBusy, setToolDirty } from "./resource_state.js";
import { renderTabs } from "./display.js";
import { createEditorPanel } from "./editor_panel.js";

const state = {
  resource: new ResourceState({
    saved: { groups: [], edits: {} },
    onChange: () => syncControls(),
    onDirtyChange: (dirty) => setToolDirty("cost-reward", dirty),
  }),
  get groups() { return this.resource.draft.groups; },
  get edits() { return this.resource.draft.edits; },
  get base() { return this.resource.base; },
  activeKey: null,
};

const editor = createEditorPanel({
  prefix: "cr", resourceId: "editor.cost_reward", resource: state.resource,
  request: () => ({ edits: state.edits, base: state.base }),
  apply: applyBootstrapPayload,
  refreshKeepingDrafts,
});

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
  setControlsBusy(document.querySelectorAll("#cr-tabs button, #panels input, #panels textarea, #panels select, #cr-save-btn, #cr-reload-btn"), state.resource.busy);
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

function renderRewardModifierTable(group) {
  const table = document.createElement("table");

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  ["id", "value", "loc.en", "loc.zh"].forEach((label) => {
    const th = document.createElement("th");
    th.textContent = label;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  group.tokens.forEach((token) => {
    const tr = document.createElement("tr");

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

    appendReadonlyCell(tr, token.scope).classList.add("wrap-cell");

    const noteCell = document.createElement("td");
    const noteInput = document.createElement("textarea");
    noteInput.rows = 2;
    noteInput.value = token.completion_note || "";
    noteInput.addEventListener("input", () => stageEdit(group.key, token.id, "completion_note", noteInput.value));
    noteCell.appendChild(noteInput);
    tr.appendChild(noteCell);

    appendReadonlyCell(tr, (token.loc && token.loc.en) || "").classList.add("wrap-cell");
    appendReadonlyCell(tr, (token.loc && token.loc.zh) || "").classList.add("wrap-cell");

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
}

function renderTriggerTaskTable(group) {
  const table = document.createElement("table");

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

    appendReadonlyCell(tr, token.id);
    appendReadonlyCell(tr, token.trigger);
    appendReadonlyCell(tr, token.scope);
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
  wrap.appendChild(renderTable(group));
  panelsEl.appendChild(wrap);
  syncControls();
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

void editor.load();
