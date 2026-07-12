const STAGE_W = 2048;
const STAGE_H = 1152;
const BRANCH_COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#0891b2"];

const state = {
  paths: [],
  activeId: null,
  selectedId: null,
  scale: 0.5,
  dragging: null,
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

function activePath() {
  return state.paths.find((p) => p.id === state.activeId) || null;
}

function nodeById(path, id) {
  return path.nodes.find((n) => n.id === id) || null;
}

function nodeColorClass(node) {
  return node.kind === "trunk" ? "trunk" : `branch-${node.branch_index}`;
}

function nodeColorHex(node) {
  return node.kind === "trunk" ? "#d97706" : BRANCH_COLORS[node.branch_index % BRANCH_COLORS.length];
}

function renderTabs() {
  const tabsEl = document.getElementById("tabs");
  tabsEl.innerHTML = "";
  state.paths.forEach((path) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tab" + (path.id === state.activeId ? " active" : "");
    btn.textContent = path.id;
    btn.addEventListener("click", () => {
      state.activeId = path.id;
      state.selectedId = null;
      renderTabs();
      renderStage();
      renderNodeList();
    });
    tabsEl.appendChild(btn);
  });
}

function applyZoom() {
  const stage = document.getElementById("stage");
  stage.style.width = STAGE_W * state.scale + "px";
  stage.style.height = STAGE_H * state.scale + "px";
  document.getElementById("zoomLabel").textContent = Math.round(state.scale * 100) + "%";
}

function renderStage() {
  const path = activePath();
  if (!path) return;

  document.getElementById("bgImage").src = path.preview_url;

  const nodesLayer = document.getElementById("nodesLayer");
  nodesLayer.innerHTML = "";
  const showLabels = document.getElementById("toggleLabels").checked;

  path.nodes.forEach((node) => {
    const el = document.createElement("div");
    el.className = "node " + nodeColorClass(node) + (node.id === state.selectedId ? " selected" : "");
    el.style.left = node.x * 100 + "%";
    el.style.top = node.y * 100 + "%";
    el.style.width = "4.4%";
    el.style.height = "7.8%";
    el.style.fontSize = STAGE_W * state.scale * 0.016 + "px";
    el.textContent = node.id;
    el.dataset.id = node.id;

    if (showLabels) {
      const label = document.createElement("div");
      label.className = "label";
      label.textContent = node.label;
      el.appendChild(label);
    }

    el.addEventListener("mousedown", (e) => onNodeDragStart(e, node.id));
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      state.selectedId = node.id;
      renderStage();
      renderNodeList();
    });
    nodesLayer.appendChild(el);
  });

  renderLinks(path);
}

function renderLinks(path) {
  const svg = document.getElementById("links");
  svg.innerHTML = "";
  if (!document.getElementById("toggleLinks").checked) return;

  path.nodes.forEach((node) => {
    if (!node.parent_id) return;
    const parent = nodeById(path, node.parent_id);
    if (!parent) return;
    const x1 = parent.x * 100;
    const y1 = parent.y * 100;
    const x2 = node.x * 100;
    const y2 = node.y * 100;
    const midX = (x1 + x2) / 2;
    const path2d = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path2d.setAttribute("d", `M ${x1}% ${y1}% Q ${midX}% ${y1}% ${midX}% ${(y1 + y2) / 2}% T ${x2}% ${y2}%`);
    path2d.style.stroke = node.kind === "trunk" ? "rgba(217,119,6,0.65)" : nodeColorHex(node) + "a6";
    svg.appendChild(path2d);
  });
}

function renderNodeList() {
  const path = activePath();
  const listEl = document.getElementById("nodeList");
  listEl.innerHTML = "";
  if (!path) return;

  function addGroupHeader(title, color) {
    const header = document.createElement("div");
    header.className = "group-header";
    header.innerHTML = `<span class="swatch" style="background:${color}"></span>${title}`;
    listEl.appendChild(header);
  }

  function addRow(node) {
    const row = document.createElement("div");
    row.className = "node-row" + (node.id === state.selectedId ? " selected" : "");
    row.innerHTML = `
      <div class="n" style="color:${nodeColorHex(node)}">${node.id}</div>
      <div class="title" title="${node.label}">${node.label}</div>
      <input type="number" step="0.001" min="0" max="1" value="${node.x.toFixed(3)}" data-axis="x">
      <input type="number" step="0.001" min="0" max="1" value="${node.y.toFixed(3)}" data-axis="y">
    `;
    row.addEventListener("click", (e) => {
      if (e.target.tagName === "INPUT") return;
      state.selectedId = node.id;
      renderStage();
      renderNodeList();
    });
    row.querySelectorAll("input").forEach((inp) => {
      inp.addEventListener("change", () => {
        const v = Math.max(0, Math.min(1, parseFloat(inp.value) || 0));
        node[inp.dataset.axis] = v;
        renderStage();
        renderNodeList();
      });
    });
    listEl.appendChild(row);
  }

  addGroupHeader("主干", "#d97706");
  path.nodes.filter((n) => n.kind === "trunk").forEach(addRow);

  for (let b = 0; b < 5; b++) {
    const branchNodes = path.nodes.filter((n) => n.kind === "branch" && n.branch_index === b);
    if (!branchNodes.length) continue;
    addGroupHeader(`分支 ${b + 1}`, BRANCH_COLORS[b]);
    branchNodes.forEach(addRow);
  }
}

function onNodeDragStart(e, id) {
  e.preventDefault();
  e.stopPropagation();
  state.selectedId = id;
  state.dragging = { id };
  renderStage();
  renderNodeList();
}

document.addEventListener("mousemove", (e) => {
  if (!state.dragging) return;
  const stage = document.getElementById("stage");
  const rect = stage.getBoundingClientRect();
  let x = (e.clientX - rect.left) / rect.width;
  let y = (e.clientY - rect.top) / rect.height;
  x = Math.max(0, Math.min(1, x));
  y = Math.max(0, Math.min(1, y));
  const path = activePath();
  const node = nodeById(path, state.dragging.id);
  node.x = x;
  node.y = y;
  renderStage();
});

document.addEventListener("mouseup", () => {
  if (state.dragging) renderNodeList();
  state.dragging = null;
});

document.getElementById("stage").addEventListener("click", (e) => {
  const bgImage = document.getElementById("bgImage");
  const stage = document.getElementById("stage");
  if (e.target !== bgImage && e.target !== stage) return;
  if (state.selectedId == null) return;
  const rect = stage.getBoundingClientRect();
  const path = activePath();
  const node = nodeById(path, state.selectedId);
  node.x = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
  node.y = Math.max(0, Math.min(1, (e.clientY - rect.top) / rect.height));
  renderStage();
  renderNodeList();
});

document.getElementById("zoom").addEventListener("input", (e) => {
  state.scale = parseFloat(e.target.value);
  applyZoom();
  renderStage();
});
document.getElementById("toggleLinks").addEventListener("change", renderStage);
document.getElementById("toggleLabels").addEventListener("change", renderStage);

document.getElementById("reset-btn").addEventListener("click", () => {
  const path = activePath();
  if (!path) return;
  if (!confirm(`将 ${path.id} 的所有节点重置为默认布局？`)) return;
  path.nodes.forEach((node) => {
    node.x = node.default_x;
    node.y = node.default_y;
  });
  state.selectedId = null;
  renderStage();
  renderNodeList();
});

function applyBootstrapPayload(payload) {
  state.paths = payload.paths || [];
  if (!state.activeId || !state.paths.some((p) => p.id === state.activeId)) {
    state.activeId = state.paths.length ? state.paths[0].id : null;
  }
  setLog(payload.log || "");
  renderTabs();
  applyZoom();
  renderStage();
  renderNodeList();
}

async function loadBootstrap() {
  const payload = await fetchJson("/api/bootstrap");
  applyBootstrapPayload(payload);
}

async function save() {
  const saveBtn = document.getElementById("save-btn");
  saveBtn.disabled = true;
  try {
    const edits = {};
    state.paths.forEach((path) => {
      const coords = {};
      path.nodes.forEach((n) => {
        coords[n.id] = { x: n.x, y: n.y };
      });
      edits[path.id] = coords;
    });
    const payload = await fetchJson("/api/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ edits }),
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
