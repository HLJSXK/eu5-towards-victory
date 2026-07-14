const tabButtons = document.querySelectorAll(".tool-hub-tab-btn");
const toolPanels = document.querySelectorAll(".tool-panel");

function activateTool(toolName) {
  tabButtons.forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.tool === toolName);
  });
  toolPanels.forEach((panel) => {
    panel.classList.toggle("active", panel.dataset.tool === toolName);
  });
  document.body.dataset.activeTool = toolName;
}

tabButtons.forEach((btn) => {
  btn.addEventListener("click", () => activateTool(btn.dataset.tool));
});

activateTool(tabButtons[0].dataset.tool);
