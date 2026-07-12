const STAGE_W = 2048;
const STAGE_H = 1152;
const BRANCH_COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#0891b2"];
// Each victory path's own theme color (conquest=red, prosperity=green,
// trade=gold, diplomatic=gray, cultural=purple, science=blue). The connector
// lines for a path's whole tree (trunk + every branch) all use a single pale
// tint of that path's theme color and a uniform width, so once overlaid on
// the real background art in-game they read as one soft, consistent guide
// per path rather than a rainbow of per-branch UI-editor colors.
const PATH_LINE_COLORS = {
  conquest: "#fca5a5",
  prosperity: "#86efac",
  trade: "#fcd34d",
  diplomatic: "#d1d5db",
  cultural: "#d8b4fe",
  science: "#93c5fd",
};
const LINE_WIDTH = 0.6;
const SVG_NS = "http://www.w3.org/2000/svg";

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

// Uniform Catmull-Rom -> cubic Bezier conversion. Produces ONE continuous path
// through an ordered list of points with matching tangents at every interior
// point (C1-continuous), instead of independently-curved per-edge segments
// that would kink at each node. Standard 1/6 tangent-scale conversion.
function catmullRomPath(points) {
  if (points.length < 2) return "";
  if (points.length === 2) {
    return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  }
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i - 1] || points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2] || p2;
    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }
  return d;
}

function drawChain(svg, nodes, color, strokeWidth) {
  if (nodes.length < 2) return;
  const points = nodes.map((n) => ({ x: n.x * 100, y: n.y * 100 }));
  const path2d = document.createElementNS(SVG_NS, "path");
  path2d.setAttribute("d", catmullRomPath(points));
  path2d.style.stroke = color;
  path2d.style.strokeWidth = strokeWidth;
  svg.appendChild(path2d);
}

// Tree-logic connectors: one smooth spline for the trunk chain (t1..t5), and
// one smooth spline per branch running from its fork point (a trunk node)
// through its own chain of nodes — rather than one curve per edge, so each
// chain reads as a single continuous line matching the tree's actual branches.
function renderLinks(path) {
  const svg = document.getElementById("links");
  svg.innerHTML = "";
  if (!document.getElementById("toggleLinks").checked) return;

  const lineColor = PATH_LINE_COLORS[path.id] || "#e5e7eb";

  const trunkNodes = path.nodes.filter((n) => n.kind === "trunk");
  drawChain(svg, trunkNodes, lineColor, LINE_WIDTH);

  for (let b = 0; b < 5; b++) {
    const branchNodes = path.nodes.filter((n) => n.kind === "branch" && n.branch_index === b);
    if (!branchNodes.length) continue;
    const attachNode = nodeById(path, branchNodes[0].parent_id);
    const chain = attachNode ? [attachNode, ...branchNodes] : branchNodes;
    drawChain(svg, chain, lineColor, LINE_WIDTH);
  }
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
