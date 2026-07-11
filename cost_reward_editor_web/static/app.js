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

function renderTable(group) {
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

    const idCell = document.createElement("td");
    idCell.textContent = token.id;
    idCell.className = "readonly";
    tr.appendChild(idCell);

    const valueCell = document.createElement("td");
    const valueInput = document.createElement("input");
    valueInput.type = "number";
    valueInput.step = "any";
    if (!group.key.endsWith("_modifier")) {
      valueInput.min = "0";
    }
    valueInput.value = token.value;
    valueInput.addEventListener("input", () => stageEdit(group.key, token.id, "value", valueInput.value));
    valueCell.appendChild(valueInput);
    tr.appendChild(valueCell);

    const locEnCell = document.createElement("td");
    locEnCell.textContent = (token.loc && token.loc.en) || "";
    locEnCell.className = "readonly";
    tr.appendChild(locEnCell);

    const locZhCell = document.createElement("td");
    locZhCell.textContent = (token.loc && token.loc.zh) || "";
    locZhCell.className = "readonly";
    tr.appendChild(locZhCell);

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  return table;
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

  if (group.tokens.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-state";
    empty.textContent = "当前没有属于此类别的 token。";
    panelsEl.appendChild(empty);
    return;
  }

  panelsEl.appendChild(renderTable(group));
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
