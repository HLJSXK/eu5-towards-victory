// WP-10: global shell. The tab bar used to be the whole of this module; it now also paints the
// per-tool dirty dot / running-job marker and asks for confirmation before leaving with unsaved work.
// The indicator values themselves live in resource_state.js so editors (and their VM test) can report
// dirtiness without loading this module.
import { dirtyToolNames, runningToolNames, subscribeToolIndicators, toolIndicator } from "./resource_state.js";

const tabButtons = document.querySelectorAll(".tool-hub-tab-btn");
const toolPanels = document.querySelectorAll(".tool-panel");

export function activateTool(toolName) {
  tabButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tool === toolName);
  });
  toolPanels.forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.tool === toolName);
  });
  document.body.dataset.activeTool = toolName;
  document.dispatchEvent(new CustomEvent("tool-activated", { detail: { tool: toolName } }));
}

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => activateTool(btn.dataset.tool));
});

activateTool(tabButtons[0].dataset.tool);

// Derive the dot text from the same indicator object the panel renders, so both agree.
export function indicatorLabel(indicator) {
  const parts = [];
  if (indicator.dirty) parts.push("有未保存的更改");
  if (indicator.jobs > 0) parts.push(`${indicator.jobs} 个作业在运行`);
  return parts.join("；");
}

export function renderToolIndicators(tabs = tabButtons) {
  for (const button of tabs) {
    const dot = button.querySelector(".tool-hub-tab-dot");
    const indicator = toolIndicator(button.dataset.tool);
    if (!dot) continue;
    dot.hidden = !indicator.dirty && indicator.jobs === 0;
    dot.classList.toggle("dirty", indicator.dirty);
    dot.classList.toggle("running", indicator.jobs > 0);
    dot.dataset.jobs = String(indicator.jobs);
    dot.title = indicatorLabel(indicator);
    // Exposed on the button as well: the label is what a user reads, these are what a test asserts.
    button.dataset.dirty = indicator.dirty ? "true" : "false";
    button.dataset.jobs = String(indicator.jobs);
  }
}

export function createToolShell({ win = window, tabs = tabButtons } = {}) {
  const leave = (event) => {
    const dirty = dirtyToolNames();
    if (!dirty.length) return undefined;
    event.preventDefault();
    // Legacy browsers need returnValue set; modern ones only need preventDefault.
    event.returnValue = "";
    return dirty;
  };
  const unsubscribe = subscribeToolIndicators(() => renderToolIndicators(tabs));
  win.addEventListener("beforeunload", leave);
  renderToolIndicators(tabs);
  return {
    dirtyTools: dirtyToolNames,
    runningTools: runningToolNames,
    leave,
    render: () => renderToolIndicators(tabs),
    destroy() {
      unsubscribe();
      win.removeEventListener("beforeunload", leave);
    },
  };
}

// Page entry: index.html loads this module next to the tab bar.
const shell = createToolShell();
window.__toolShell = shell;
