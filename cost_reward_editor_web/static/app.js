const state = {
  groups: [],
  edits: {},
  activeKey: null,
};

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const text = await response.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch (err) {
    payload = null;
  }
  if (!response.ok) {
    const detail = payload && payload.detail ? payload.detail : text || response.statusText;
    throw new Error(detail);
  }
  return payload;
}

function setLog(text) {
  document.getElementById("log").textContent = text || "";
}

function appendLog(text) {
  const log = document.getElementById("log");
  log.textContent += text;
  log.scrollTop = log.scrollHeight;
}

function clearEdits() {
  state.edits = {};
}

function stageEdit(categoryKey, tokenId, field, rawValue) {
  if (!state.edits[categoryKey]) state.edits[categoryKey] = {};
  if (!state.edits[categoryKey][tokenId]) state.edits[categoryKey][tokenId] = {};
  state.edits[categoryKey][tokenId][field] = rawValue;
}

function renderTabs() {
  const tabsEl = document.getElementById("tabs");
  tabsEl.innerHTML = "";
  state.groups.forEach((group) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tab" + (group.key === state.activeKey ? " active" : "");
    btn.textContent = `${group.label_zh}（${group.tokens.length}）`;
    btn.addEventListener("click", () => {
      state.activeKey = group.key;
      renderTabs();
      renderPanels();
    });
    tabsEl.appendChild(btn);
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
}

function applyBootstrapPayload(payload) {
  state.groups = payload.groups || [];
  if (!state.activeKey || !state.groups.some((g) => g.key === state.activeKey)) {
    state.activeKey = state.groups.length ? state.groups[0].key : null;
  }
  clearEdits();
  setLog(payload.log || "");
  renderTabs();
  renderPanels();
}

async function loadBootstrap() {
  const payload = await fetchJson("/api/bootstrap");
  applyBootstrapPayload(payload);
}

async function save() {
  const saveBtn = document.getElementById("save-btn");
  saveBtn.disabled = true;
  try {
    const payload = await fetchJson("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ edits: state.edits }),
    });
    applyBootstrapPayload(payload);
    appendLog("\n[ok] Saved.\n");
  } catch (err) {
    appendLog(`\n[error] ${err.message}\n`);
  } finally {
    saveBtn.disabled = false;
  }
}

document.getElementById("save-btn").addEventListener("click", save);
document.getElementById("reload-btn").addEventListener("click", () => {
  loadBootstrap().catch((err) => appendLog(`\n[error] ${err.message}\n`));
});

loadBootstrap().catch((err) => appendLog(`\n[error] ${err.message}\n`));
