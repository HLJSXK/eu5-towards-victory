const cropState = {
  tasks: [], index: -1, image: null, rect: null, saved: false,
  view: { left: 0, top: 0, width: 0, height: 0, scale: 1 }, drag: null,
};
const canvas = document.getElementById("cropper-canvas");
const context = canvas.getContext("2d");
const RATIO = 27 / 11;

async function cropJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || payload.error || response.statusText);
  return payload;
}

function activeTask() { return cropState.tasks[cropState.index]; }
function clamp(value, low, high) { return Math.max(low, Math.min(high, value)); }
function largestCenterRect(width, height) {
  const cropWidth = width / height >= RATIO ? height * RATIO : width;
  const cropHeight = cropWidth / RATIO;
  return { x: (width - cropWidth) / 2, y: (height - cropHeight) / 2, width: cropWidth, height: cropHeight };
}
function clampRect(rect, width, height) {
  const maxRect = largestCenterRect(width, height);
  let cropWidth = Math.abs(rect.width); let cropHeight = Math.abs(rect.height);
  if (cropWidth < 1 || cropHeight < 1) return maxRect;
  if (cropWidth / cropHeight > RATIO) cropHeight = cropWidth / RATIO; else cropWidth = cropHeight * RATIO;
  cropWidth = Math.min(cropWidth, maxRect.width, width);
  cropHeight = Math.min(cropWidth / RATIO, height); cropWidth = cropHeight * RATIO;
  return { x: clamp(rect.x, 0, Math.max(0, width - cropWidth)), y: clamp(rect.y, 0, Math.max(0, height - cropHeight)), width: cropWidth, height: cropHeight };
}
function rectFromPoints(start, end, width, height) {
  const dx = end.x - start.x; const dy = end.y - start.y; const absDx = Math.abs(dx); const absDy = Math.abs(dy);
  if (absDx < 1 && absDy < 1) return largestCenterRect(width, height);
  let cropWidth; let cropHeight;
  if (absDy <= 0.001 || absDx / RATIO >= absDy) { cropWidth = Math.max(absDx, 1); cropHeight = cropWidth / RATIO; }
  else { cropHeight = Math.max(absDy, 1); cropWidth = cropHeight * RATIO; }
  return clampRect({ x: dx >= 0 ? start.x : start.x - cropWidth, y: dy >= 0 ? start.y : start.y - cropHeight, width: cropWidth, height: cropHeight }, width, height);
}
function resizeFromCenter(factor) {
  if (!cropState.image || !cropState.rect) return;
  const rect = cropState.rect; const center = { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  cropState.rect = clampRect({ x: center.x - rect.width * factor / 2, y: center.y - rect.height * factor / 2, width: rect.width * factor, height: rect.height * factor }, cropState.image.naturalWidth, cropState.image.naturalHeight);
  cropState.saved = false; renderInspector(); draw();
}
function resizeCanvasToDisplay() {
  const box = canvas.getBoundingClientRect(); const ratio = window.devicePixelRatio || 1;
  const width = Math.max(1, Math.floor(box.width * ratio)); const height = Math.max(1, Math.floor(box.height * ratio));
  if (canvas.width !== width || canvas.height !== height) { canvas.width = width; canvas.height = height; }
}
function imageToCanvas(point) { return { x: cropState.view.left + point.x * cropState.view.scale, y: cropState.view.top + point.y * cropState.view.scale }; }
function canvasToImage(event) {
  const box = canvas.getBoundingClientRect(); const scale = canvas.width / box.width;
  const x = (event.clientX - box.left) * scale; const y = (event.clientY - box.top) * scale;
  return { canvasX: x, canvasY: y, x: (x - cropState.view.left) / cropState.view.scale, y: (y - cropState.view.top) / cropState.view.scale };
}
function rectCanvasBounds() {
  const rect = cropState.rect; const topLeft = imageToCanvas({ x: rect.x, y: rect.y });
  return { x1: topLeft.x, y1: topLeft.y, x2: topLeft.x + rect.width * cropState.view.scale, y2: topLeft.y + rect.height * cropState.view.scale };
}
function hitTest(point) {
  const bounds = rectCanvasBounds();
  for (const [mode, x, y] of [["resize_nw", bounds.x1, bounds.y1], ["resize_ne", bounds.x2, bounds.y1], ["resize_sw", bounds.x1, bounds.y2], ["resize_se", bounds.x2, bounds.y2]]) {
    if (Math.abs(point.canvasX - x) <= 14 && Math.abs(point.canvasY - y) <= 14) return mode;
  }
  return point.canvasX >= bounds.x1 && point.canvasX <= bounds.x2 && point.canvasY >= bounds.y1 && point.canvasY <= bounds.y2 ? "move" : "create";
}
function draw() {
  resizeCanvasToDisplay(); context.clearRect(0, 0, canvas.width, canvas.height); context.fillStyle = "#0f1115"; context.fillRect(0, 0, canvas.width, canvas.height);
  if (!cropState.image || !cropState.image.complete) return;
  const padding = 24 * (window.devicePixelRatio || 1);
  cropState.view.scale = Math.max(Math.min((canvas.width - padding * 2) / cropState.image.naturalWidth, (canvas.height - padding * 2) / cropState.image.naturalHeight, 1), 0.05);
  cropState.view.width = cropState.image.naturalWidth * cropState.view.scale; cropState.view.height = cropState.image.naturalHeight * cropState.view.scale;
  cropState.view.left = (canvas.width - cropState.view.width) / 2; cropState.view.top = (canvas.height - cropState.view.height) / 2;
  context.drawImage(cropState.image, cropState.view.left, cropState.view.top, cropState.view.width, cropState.view.height);
  if (!cropState.rect) return;
  const bounds = rectCanvasBounds(); const right = cropState.view.left + cropState.view.width; const bottom = cropState.view.top + cropState.view.height;
  context.save(); context.fillStyle = "rgba(0,0,0,.58)";
  context.fillRect(cropState.view.left, cropState.view.top, cropState.view.width, bounds.y1 - cropState.view.top); context.fillRect(cropState.view.left, bounds.y2, cropState.view.width, bottom - bounds.y2);
  context.fillRect(cropState.view.left, bounds.y1, bounds.x1 - cropState.view.left, bounds.y2 - bounds.y1); context.fillRect(bounds.x2, bounds.y1, right - bounds.x2, bounds.y2 - bounds.y1);
  const color = cropState.saved ? "#f6c453" : "#71c7ec";
  context.strokeStyle = color; context.lineWidth = 3; context.strokeRect(bounds.x1, bounds.y1, bounds.x2 - bounds.x1, bounds.y2 - bounds.y1);
  context.lineWidth = 1; context.beginPath();
  for (const fraction of [1 / 3, 2 / 3]) { context.moveTo(bounds.x1 + (bounds.x2 - bounds.x1) * fraction, bounds.y1); context.lineTo(bounds.x1 + (bounds.x2 - bounds.x1) * fraction, bounds.y2); context.moveTo(bounds.x1, bounds.y1 + (bounds.y2 - bounds.y1) * fraction); context.lineTo(bounds.x2, bounds.y1 + (bounds.y2 - bounds.y1) * fraction); }
  context.stroke();
  for (const [x, y] of [[bounds.x1, bounds.y1], [bounds.x2, bounds.y1], [bounds.x1, bounds.y2], [bounds.x2, bounds.y2]]) { context.fillStyle = color; context.fillRect(x - 5, y - 5, 10, 10); context.strokeStyle = "#111"; context.strokeRect(x - 5, y - 5, 10, 10); }
  context.restore();
}
function renderTasks() {
  const root = document.getElementById("cropper-task-list"); root.innerHTML = "";
  cropState.tasks.forEach((task, index) => { const button = document.createElement("button"); button.type = "button"; button.className = `cropper-task${index === cropState.index ? " active" : ""}${task.saved ? " saved" : ""}`; button.textContent = `${task.name}  ${task.width}x${task.height}`; button.addEventListener("click", () => selectTask(index)); root.appendChild(button); });
}
function renderInspector() {
  const task = activeTask(); if (!task || !cropState.rect) return;
  document.getElementById("cropper-title").textContent = `${cropState.index + 1}/${cropState.tasks.length} ${task.name}`;
  document.getElementById("cropper-meta").innerHTML = `<dt>Source</dt><dd>${task.pngPath}</dd><dt>Output</dt><dd>${task.ddsPath}</dd><dt>Image</dt><dd>${task.width} x ${task.height}</dd><dt>Crop</dt><dd>${cropState.rect.x.toFixed(1)}, ${cropState.rect.y.toFixed(1)}, ${cropState.rect.width.toFixed(1)} x ${cropState.rect.height.toFixed(1)}</dd>`;
}
function selectTask(index) {
  cropState.index = index; const task = activeTask(); if (!task) return;
  cropState.rect = { ...task.rect }; cropState.saved = task.saved; cropState.image = new Image(); cropState.image.onload = () => { draw(); renderInspector(); }; cropState.image.src = `/api/cropper/image/${index}?v=${Date.now()}`; renderTasks(); renderInspector();
}
canvas.addEventListener("pointerdown", (event) => { if (!cropState.image || !cropState.rect) return; canvas.setPointerCapture(event.pointerId); const point = canvasToImage(event); cropState.drag = { mode: hitTest(point), start: point, rect: { ...cropState.rect } }; });
canvas.addEventListener("pointermove", (event) => {
  if (!cropState.drag || !cropState.image) return;
  const point = canvasToImage(event); const drag = cropState.drag; const rect = drag.rect; const width = cropState.image.naturalWidth; const height = cropState.image.naturalHeight;
  if (drag.mode === "move") cropState.rect = clampRect({ x: rect.x + point.x - drag.start.x, y: rect.y + point.y - drag.start.y, width: rect.width, height: rect.height }, width, height);
  else if (drag.mode.startsWith("resize")) { const anchors = { resize_nw: { x: rect.x + rect.width, y: rect.y + rect.height }, resize_ne: { x: rect.x, y: rect.y + rect.height }, resize_sw: { x: rect.x + rect.width, y: rect.y }, resize_se: { x: rect.x, y: rect.y } }; cropState.rect = rectFromPoints(anchors[drag.mode], point, width, height); }
  else cropState.rect = rectFromPoints(drag.start, point, width, height);
  cropState.saved = false; renderInspector(); draw();
});
canvas.addEventListener("pointerup", () => { cropState.drag = null; }); canvas.addEventListener("pointercancel", () => { cropState.drag = null; });
canvas.addEventListener("wheel", (event) => { event.preventDefault(); resizeFromCenter(event.deltaY < 0 ? 1.08 : 0.92); }, { passive: false }); window.addEventListener("resize", draw);
document.addEventListener("keydown", (event) => {
  if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
  const next = cropState.index + (event.key === "ArrowRight" ? 1 : -1);
  if (next >= 0 && next < cropState.tasks.length) { event.preventDefault(); selectTask(next); }
});

document.getElementById("cropper-save").addEventListener("click", async () => { if (cropState.index < 0) return; const result = await cropJson(`/api/cropper/${cropState.index}/save`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ rect: cropState.rect }) }); document.getElementById("cropper-log").textContent += `${result.message}\n`; cropState.tasks[cropState.index] = result.task; cropState.saved = true; renderTasks(); renderInspector(); draw(); });
document.getElementById("cropper-remove").addEventListener("click", async () => { if (cropState.index < 0) return; const result = await cropJson(`/api/cropper/${cropState.index}/remove`, { method: "POST" }); document.getElementById("cropper-log").textContent += `${result.message}\n`; cropState.tasks[cropState.index] = result.task; cropState.rect = { ...result.task.rect }; cropState.saved = false; renderTasks(); renderInspector(); draw(); });
document.getElementById("cropper-apply").addEventListener("click", async () => {
  const button = document.getElementById("cropper-apply"); button.disabled = true;
  try { const job = await cropJson("/api/cropper/apply", { method: "POST" }); const poll = async () => { const current = await cropJson(`/api/jobs/${job.id}`); document.getElementById("cropper-log").textContent = (current.lines || []).join("\n"); document.getElementById("cropper-status").textContent = current.status; if (["queued", "running", "cancelling"].includes(current.status)) window.setTimeout(poll, 600); else button.disabled = false; }; await poll(); }
  catch (error) { document.getElementById("cropper-log").textContent += `${error.message}\n`; button.disabled = false; }
});
cropJson("/api/cropper/bootstrap").then((payload) => { cropState.tasks = payload.tasks || []; document.getElementById("cropper-log").textContent = (payload.logs || []).join("\n"); if (cropState.tasks.length) selectTask(0); else document.getElementById("cropper-status").textContent = "No generated PNG files found"; }).catch((error) => { document.getElementById("cropper-status").textContent = error.message; });
