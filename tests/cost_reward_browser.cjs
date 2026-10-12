const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { mkdtempSync } = require('node:fs');
const { join } = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');

async function waitFor(check, label) {
  const deadline = Date.now() + 60000;
  while (Date.now() < deadline) {
    if (await check()) return;
    await delay(100);
  }
  throw new Error(`Timed out: ${label}`);
}

async function main() {
  const root = require('node:path').resolve(__dirname, '..');
  const port = 8768;
  const debugPort = 9338;
  const server = spawn(process.env.EU5_PYTHON || 'C:/Users/Hades/anaconda3/envs/eu5/python.exe',
    ['-m', 'uvicorn', 'towards_victory_editor_web.server:create_app', '--factory', '--host', '127.0.0.1', '--port', String(port)],
    { cwd: root, windowsHide: true, stdio: 'ignore' });
  let chrome;
  let ws;
  try {
    await waitFor(async () => {
      try { return (await fetch(`http://127.0.0.1:${port}/`)).ok; } catch { return false; }
    }, 'editor server');
    chrome = spawn(process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe', [
      '--headless', '--no-sandbox', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
      `--remote-debugging-port=${debugPort}`, `--user-data-dir=${mkdtempSync(join(require('node:os').tmpdir(), 'eu5-cost-reward-'))}`,
      'about:blank',
    ], { windowsHide: true, stdio: 'ignore' });
    let target;
    await waitFor(async () => {
      try {
        target = (await (await fetch(`http://127.0.0.1:${debugPort}/json/list`)).json()).find(item => item.type === 'page');
        return !!target;
      } catch { return false; }
    }, 'Chrome');
    ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    let id = 0;
    const pending = new Map();
    ws.onmessage = ({ data }) => {
      const response = JSON.parse(data);
      if (!response.id) return;
      const request = pending.get(response.id);
      pending.delete(response.id);
      response.error ? request.reject(new Error(JSON.stringify(response.error))) : request.resolve(response.result);
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      pending.set(++id, { resolve, reject });
      ws.send(JSON.stringify({ id, method, params }));
    });
    const evaluate = async (expression) => {
      const response = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (response.exceptionDetails) throw new Error(JSON.stringify(response.exceptionDetails));
      return response.result.value;
    };

    await send('Runtime.enable');
    await send('Page.enable');
    await send('Page.navigate', { url: `http://127.0.0.1:${port}/` });
    await waitFor(() => evaluate('document.querySelectorAll("#cr-tabs button").length >= 5'), 'cost/reward tabs');
    await evaluate('document.querySelectorAll("#cr-tabs button")[3].click()');
    await waitFor(() => evaluate('document.querySelector("#panels table[data-cost-reward-table]")?.dataset.visibleRows === "395"'), '395 modifier rows');
    const renderMs = await evaluate('Number(document.querySelector("#panels table[data-cost-reward-table]").dataset.renderMs)');
    assert(Number.isFinite(renderMs) && renderMs <= 2500, `395-row render took ${renderMs}ms`);

    await evaluate(`(() => {
      const inputs = [...document.querySelectorAll('#panels table[data-cost-reward-table] input[type="number"]')].slice(0, 2);
      inputs[0].value = '0.12345'; inputs[0].dispatchEvent(new Event('input', { bubbles: true }));
      inputs[1].value = '0.23456'; inputs[1].dispatchEvent(new Event('input', { bubbles: true }));
    })()`);
    await waitFor(() => evaluate('document.querySelectorAll("#panels tr.dirty-row").length === 2'), 'two dirty rows');
    assert.equal(await evaluate('document.querySelector("#cr-dirty-count").textContent'), '已改动 2 行');
    await evaluate('document.querySelector("#cr-only-dirty").click()');
    await waitFor(() => evaluate('document.querySelector("#panels table[data-cost-reward-table]").dataset.visibleRows === "2"'), 'only dirty rows');
    assert.equal(await evaluate('document.querySelectorAll("#panels table[data-cost-reward-table] tbody tr:not([hidden])").length'), 2);
    assert.equal(await evaluate('document.querySelectorAll("#panels tr.dirty-row").length'), 2);
    console.log(`Cost/reward Chrome acceptance passed: two dirty rows, count 2, only-dirty rows 2, 395-row render ${renderMs.toFixed(1)}ms.`);
  } finally {
    if (ws) { try { await new Promise(resolve => { ws.onclose = resolve; ws.close(); }); } catch {} }
    if (chrome) chrome.kill();
    server.kill();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
