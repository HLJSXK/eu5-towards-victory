const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { mkdtempSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');

const tools = ['cost-reward', 'victory-tree', 'wonder-localization', 'media-studio', 'wonder-cropper',
  'generators', 'localization', 'victory-paths', 'court-positions'];

// Own ports: resource_state_browser.cjs owns 8767/9337, and two Chrome sessions sharing a
// debugging port would make the second one attach to the first one's browser.
const PORT = 8769;
const DEBUG_PORT = 9339;

module.exports = async function cssAcceptance({ evaluate, ready, send }) {
  const baseline = process.env.WP13_BASELINE === '1';
  const scratch = mkdtempSync(join(tmpdir(), baseline ? 'eu5-wp13-before-' : 'eu5-wp13-after-'));
  const metrics = [];
  await send('Page.addScriptToEvaluateOnNewDocument', { source: `
    const originalFetch = window.fetch.bind(window);
    window.fetch = (url, options = {}) => {
      if ((options.method || 'GET').toUpperCase() !== 'GET') throw new Error('CSS acceptance is read-only');
      return originalFetch(url, options);
    };
  ` });
  await send('Page.navigate', { url: `http://127.0.0.1:${PORT}/` });
  await ready('document.querySelectorAll("#cr-tabs button").length >= 5');
  const selectors = ['#panels table', '#nodeList .node-row', '#language-tabs button', '#media-tool-list button',
    '#cropper-task-list button', '.generator-row', '.localization-group', '.victory-paths-field', '.court-positions-field'];
  try {
    for (const width of [1600, 1000, 390]) {
      await send('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: false });
      for (const [index, tool] of tools.entries()) {
        await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click()`);
        await ready(`document.querySelector(${JSON.stringify(selectors[index])})`);
        await evaluate(`new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))`);
        const measurement = await evaluate(`(() => {
          const panel = document.querySelector('.tool-panel.active');
          const container = document.querySelector('#tool-hub-panels');
          return {
            tool: panel.dataset.tool, width: innerWidth,
            scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth,
            panelScroll: panel.scrollWidth, panelWidth: panel.clientWidth,
            containerScroll: container.scrollWidth, containerWidth: container.clientWidth,
            canvasWidth: document.querySelector('.tool-victory-tree .canvas-wrap').getBoundingClientRect().width,
            tabs: [...document.querySelectorAll('.tool-hub-tab-btn')].map(button => {
              const bounds = button.getBoundingClientRect();
              return { left: bounds.left, right: bounds.right, top: bounds.top, bottom: bounds.bottom };
            }),
          };
        })()`);
        metrics.push(measurement);
        if (!baseline) {
          assert.equal(measurement.tool, tool);
          assert(measurement.scrollWidth <= measurement.clientWidth + 1, `${width}/${tool}: document overflow ${JSON.stringify(measurement)}`);
          assert(measurement.panelScroll <= measurement.panelWidth + 1, `${width}/${tool}: panel overflow ${JSON.stringify(measurement)}`);
          assert(measurement.containerScroll <= measurement.containerWidth + 1, `${width}/${tool}: container overflow`);
          assert.equal(measurement.tabs.length, 9);
          assert(measurement.tabs.every(bounds => bounds.left >= 0 && bounds.right <= width + 1 && bounds.top >= 0 && bounds.bottom <= 1000), `${width}/${tool}: nine tabs in viewport`);
          if (width === 390 && tool === 'victory-tree') assert(measurement.canvasWidth >= 300, `390px victory-tree canvas: ${measurement.canvasWidth}px < 300px`);
        }
        if (index < 5) {
          const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false });
          writeFileSync(join(scratch, `${width}-${tool}.png`), Buffer.from(shot.data, 'base64'));
        }
      }
    }
    if (!baseline) await checkTheme({ evaluate });
    console.log(`CSS Chrome acceptance ${baseline ? 'baseline captured' : 'passed'}: 27 viewports, 15 screenshots; ${scratch}`);
  } finally {
    writeFileSync(join(scratch, 'metrics.json'), JSON.stringify(metrics, null, 2));
    await send('Emulation.clearDeviceMetricsOverride');
  }
};

async function checkTheme({ evaluate }) {
  const styles = await evaluate(`(() => {
    const selectors = ['#cr-save-btn', '#vt-save-btn', '#save-button', '#media-run', '#cropper-save', '.generators-actions .primary-button', '.localization-actions .primary-button'];
    return selectors.map(selector => {
      const style = getComputedStyle(document.querySelector(selector));
      return { selector, radius: style.borderRadius, background: style.backgroundColor, color: style.color };
    });
  })()`);
  assert(styles.every(style => style.radius === '10px'), JSON.stringify(styles));
  assert(styles.every(style => style.background === styles[0].background && style.color === styles[0].color), JSON.stringify(styles));
  assert.equal(await evaluate('getComputedStyle(document.documentElement).colorScheme'), 'dark');
  assert.equal(await evaluate('getComputedStyle(document.querySelector(".tool-panel")).colorScheme'), 'light');
  const probe = `[getComputedStyle(document.querySelector('#cr-save-btn')).backgroundColor, getComputedStyle(document.querySelector('#cr-save-btn')).borderRadius].join('|')`;
  const before = await evaluate(probe);
  // Re-appending a <link> makes the browser load it again, so the sheet is briefly absent and the
  // button falls back to the user-agent style. Wait for the reload and a paint before comparing,
  // otherwise this reads a half-applied cascade rather than the link-order dependence it tests.
  await evaluate(`(async () => {
    const links = [...document.querySelectorAll('link[rel="stylesheet"]')].reverse();
    document.head.append(...links);
    await Promise.all(links.map(link => link.sheet ? Promise.resolve()
      : new Promise(resolve => { link.addEventListener('load', resolve, { once: true }); link.addEventListener('error', resolve, { once: true }); })));
    await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  })()`);
  assert.equal(await evaluate(probe), before);
  assert.equal(await evaluate(`[...document.querySelectorAll('#language-tabs button')].slice(0, 3).map(button => button.textContent).join('|')`), '英文|简体中文|机制');
}

async function main() {
  const root = resolve(__dirname, '..');
  const port = PORT;
  const debugPort = DEBUG_PORT;
  const profile = mkdtempSync(join(tmpdir(), 'eu5-wp13-chrome-'));
  const server = spawn(process.env.EU5_PYTHON || 'C:/Users/Hades/anaconda3/envs/eu5/python.exe',
    ['-m', 'uvicorn', 'towards_victory_editor_web.server:create_app', '--factory', '--host', '127.0.0.1', '--port', String(port)],
    { cwd: root, windowsHide: true, stdio: 'ignore' });
  let chrome;
  let socket;
  async function readyCheck(check, label) {
    const deadline = Date.now() + 60000;
    while (Date.now() < deadline) {
      if (await check()) return;
      await delay(100);
    }
    throw new Error(`Timed out: ${label}`);
  }
  try {
    await readyCheck(async () => { try { return (await fetch(`http://127.0.0.1:${port}/`)).ok; } catch { return false; } }, 'server');
    chrome = spawn(process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
      ['--headless', '--no-sandbox', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
        `--remote-debugging-port=${debugPort}`, `--user-data-dir=${profile}`, 'about:blank'],
      { windowsHide: true, stdio: 'ignore' });
    let target;
    await readyCheck(async () => {
      try { target = (await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json()).find(item => item.type === 'page'); return !!target; }
      catch { return false; }
    }, 'Chrome');
    socket = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { socket.onopen = resolve; socket.onerror = reject; });
    let requestId = 0;
    const pending = new Map();
    socket.onmessage = ({ data }) => {
      const response = JSON.parse(data);
      if (!response.id) return;
      const request = pending.get(response.id);
      pending.delete(response.id);
      response.error ? request.reject(new Error(JSON.stringify(response.error))) : request.resolve(response.result);
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      pending.set(++requestId, { resolve, reject });
      socket.send(JSON.stringify({ id: requestId, method, params }));
    });
    const evaluate = async expression => {
      const response = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
      return response.result.value;
    };
    await send('Runtime.enable');
    await send('Page.enable');
    await module.exports({ send, evaluate, ready: expression => readyCheck(() => evaluate(expression), expression) });
    await send('Browser.close');
  } finally {
    if (socket) socket.close();
    if (chrome) chrome.kill();
    server.kill();
  }
}

if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
