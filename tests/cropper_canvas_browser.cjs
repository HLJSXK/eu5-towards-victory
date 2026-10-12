// WP-01: the cropper canvas must draw on first activation of its tab, without "重新加载裁剪".
// Mounted from resource_state_browser.cjs; reloads the page, reads only (GET + image), writes nothing.
const assert = require('node:assert/strict');
const { setTimeout: delay } = require('node:timers/promises');

async function settle(evaluate, expression, label, timeout = 60000) {
  const until = Date.now() + timeout;
  while (Date.now() < until) {
    try { if (await evaluate(expression)) return; } catch { /* page is navigating */ }
    await delay(100);
  }
  throw new Error(`Timed out: ${label}`);
}

module.exports = async function cropperCanvasOnFirstActivation({ evaluate, send }) {
  await evaluate('window.__beforeCropperReload = true');
  await send('Page.reload', { ignoreCache: true });
  await settle(evaluate, "!window.__beforeCropperReload && document.readyState === 'complete'", 'page reload');
  assert.notEqual(await evaluate('document.body.dataset.activeTool'), 'wonder-cropper');
  // The first crop image loads while the panel is still hidden; that onload draw sizes the canvas to 1x1.
  await settle(evaluate, "document.querySelector('#cropper-meta').textContent.includes('裁剪') && performance.getEntriesByType('resource').some((entry) => entry.name.includes('/api/cropper/image/'))", 'hidden cropper image');
  await delay(300);
  const hidden = await evaluate("[document.querySelector('#cropper-canvas').width, document.querySelector('#cropper-canvas').height]");
  assert.deepEqual(hidden, [1, 1], 'precondition: hidden canvas was drawn at 1x1');
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="wonder-cropper"]').click()`);
  const probe = `(() => {
    const canvas = document.querySelector('#cropper-canvas');
    if (canvas.width <= 1 || canvas.height <= 1) return null;
    const [r, g, b] = canvas.getContext('2d').getImageData(Math.floor(canvas.width / 2), Math.floor(canvas.height / 2), 1, 1).data;
    return { width: canvas.width, height: canvas.height, center: [r, g, b] };
  })()`;
  const until = Date.now() + 1000;
  let state = null;
  while (Date.now() < until) {
    state = await evaluate(probe);
    if (state && state.center.join() !== [0x0f, 0x11, 0x15].join()) break;
    await delay(50);
  }
  assert(state && state.width > 1 && state.height > 1, `cropper canvas sized on activation: ${JSON.stringify(state)}`);
  assert.notDeepEqual(state.center, [0x0f, 0x11, 0x15], 'cropper canvas center shows the image, not the #0f1115 background');
  console.log(`Cropper canvas acceptance passed: first tab activation drew ${state.width}x${state.height}, center rgb(${state.center.join(',')}).`);
};
