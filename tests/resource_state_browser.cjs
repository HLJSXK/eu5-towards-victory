// Real ES modules and DOM, live GETs, intercepted writes; no game data is changed.
// Run with EU5_PYTHON and CHROME_PATH set if the Windows defaults do not apply.
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { mkdtempSync, mkdirSync } = require('node:fs');
const { join, resolve } = require('node:path');
const { setTimeout: delay } = require('node:timers/promises');

async function waitFor(check, label) {
  const until = Date.now() + 60000;
  while (Date.now() < until) {
    if (await check()) return;
    await delay(100);
  }
  throw new Error(`Timed out: ${label}`);
}

async function main() {
  const root = resolve(__dirname, '..');
  const scratch = join(root, '.pytest-browser-final');
  mkdirSync(scratch, { recursive: true });
  const server = spawn(process.env.EU5_PYTHON || 'C:/Users/Hades/anaconda3/envs/eu5/python.exe',
    ['-m', 'uvicorn', 'towards_victory_editor_web.server:create_app', '--factory', '--host', '127.0.0.1', '--port', '8767'],
    { cwd: root, windowsHide: true, stdio: 'ignore' });
  let chrome, ws;
  try {
    await waitFor(async () => { try { return (await fetch('http://127.0.0.1:8767/')).ok; } catch { return false; } }, 'server');
    chrome = spawn(process.env.CHROME_PATH || 'C:/Program Files/Google/Chrome/Application/chrome.exe',
      ['--headless', '--no-sandbox', '--disable-gpu', '--no-first-run', '--no-default-browser-check',
        '--remote-debugging-port=9337', `--user-data-dir=${mkdtempSync(join(scratch, 'chrome-'))}`, 'about:blank'],
      { windowsHide: true, stdio: 'ignore' });
    let target;
    await waitFor(async () => {
      try { target = (await (await fetch('http://127.0.0.1:9337/json/list')).json()).find((item) => item.type === 'page'); return !!target; }
      catch { return false; }
    }, 'Chrome');
    ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((done, fail) => { ws.onopen = done; ws.onerror = fail; });
    let id = 0;
    const pending = new Map();
    const pageErrors = [];
    ws.onmessage = ({ data }) => {
      const response = JSON.parse(data);
      if (response.method === 'Runtime.exceptionThrown') pageErrors.push(response.params.exceptionDetails.text);
      if (!response.id) return;
      const pair = pending.get(response.id);
      pending.delete(response.id);
      response.error ? pair.reject(new Error(JSON.stringify(response.error))) : pair.resolve(response.result);
    };
    const send = (method, params = {}) => new Promise((resolve, reject) => {
      pending.set(++id, { resolve, reject }); ws.send(JSON.stringify({ id, method, params }));
    });
    const evaluate = async (expression) => {
      const result = await send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    const ready = (expression) => waitFor(() => evaluate(expression), expression);
    await send('Runtime.enable');
    await send('Page.enable');
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `
      window.confirm = () => true;
      window.__probe = { requests: [], gates: new Map(), release: null, job: null, polls: 0 };
      const liveFetch = window.fetch.bind(window);
      window.fetch = async (url, options = {}) => {
        const path = new URL(url, location.href).pathname;
        const probe = window.__probe;
        probe.requests.push({ path, body: options.body, method: options.method || 'GET' });
        if (path === '/api/jobs' && options.method === 'POST') return Response.json(probe.job);
        if (path.endsWith('/cancel')) return Response.json({ detail: 'cancel probe failure' }, { status: 503 });
        if (path.startsWith('/api/jobs/')) {
          probe.polls++;
          if (probe.pollStatus) return Response.json({ detail: 'job query probe failure' }, { status: probe.pollStatus });
          if (probe.polls === 1) throw new TypeError('network probe failure');
          return Response.json({ ...probe.job, lines: [], lines_reset: false, error: probe.terminal ? 'generator probe failure' : null,
            status: probe.terminal ? 'failed' : 'running' });
        }
        if (options.method === 'POST') {
          await new Promise((resolve) => { probe.release = resolve; });
          return Response.json({ code: probe.code || 'resource_changed', detail: 'probe source changed' }, { status: 409 });
        }
        if (probe.gates.has(path)) await new Promise((resolve) => { probe.release = resolve; });
        return liveFetch(url, options);
      };
    ` });
    await send('Page.navigate', { url: 'http://127.0.0.1:8767/' });
    await ready("!!document.querySelector('#panels input') && !!document.querySelector('#nodeList input') && document.querySelector('.tool-wonder-localization').dataset.busy === 'false'");

    for (const [tool, input, save, reload, tab, log, resource] of [
      ['cost-reward', '#panels input[type=number]', '#cr-save-btn', '#cr-reload-btn', '#cr-tabs button', '#cr-log', 'editor.cost_reward'],
      ['victory-tree', '#nodeList input', '#vt-save-btn', '#vt-reload-btn', '#vt-tabs button', '#vt-log', 'editor.victory_tree'],
    ]) {
      await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click();
        { const input = document.querySelector('${input}'); input.value = '0.123'; input.dispatchEvent(new Event('${tool === 'cost-reward' ? 'input' : 'change'}', { bubbles: true })); }
        document.querySelector('${save}').click();`);
      assert(await evaluate(`document.querySelector('${input}').disabled && document.querySelector('${save}').disabled && document.querySelector('${reload}').disabled && document.querySelector('${tab}').disabled`), `${tool} commit controls`);
      await evaluate('__probe.release()');
      await ready(`!document.querySelector('${save}').disabled`);
      assert.equal(await evaluate(`Number(document.querySelector('${input}').value)`), 0.123);
      assert.match(await evaluate(`document.querySelector('${log}').textContent`), /probe source changed/);
      await evaluate(`__probe.gates.set('/api/resources/${resource}', true); document.querySelector('${reload}').click()`);
      assert(await evaluate(`document.querySelector('${input}').disabled && document.querySelector('${tab}').disabled`), `${tool} reload controls`);
      await evaluate(`__probe.gates.clear(); __probe.release()`);
      await ready(`!document.querySelector('${save}').disabled`);
    }

    await evaluate("document.querySelector('.tool-hub-tab-btn[data-tool=\"wonder-localization\"]').click(); document.querySelectorAll('#wonder-kind-tabs button')[1].click(); document.querySelector('#wonder-list button').click()");
    await ready("document.querySelector('.tool-wonder-localization').dataset.busy === 'false'");
    await evaluate("[...document.querySelectorAll('#language-tabs button')].find(b => b.textContent.includes('仪式设计')).click()");
    await ready("!!document.querySelector('[data-ritual-prompt-input]')");
    await evaluate("{ const input = document.querySelector('[data-ritual-prompt-input]'); input.value = 'unified prompt probe'; input.dispatchEvent(new Event('input', { bubbles: true })); } document.querySelector('#save-button').click()");
    assert(await evaluate("document.querySelector('[data-ritual-prompt-input]').disabled && document.querySelector('#reload-button').disabled && [...document.querySelectorAll('#wonder-list button')].every(b => b.disabled)"));
    const commit = await evaluate("JSON.parse(__probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/commit').body)");
    assert.equal(commit.wonders[0].ritual_prompt, 'unified prompt probe');
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#save-button').disabled");
    assert.equal(await evaluate("document.querySelector('[data-ritual-prompt-input]').value"), 'unified prompt probe');
    assert(await evaluate("!document.querySelector('#dirty-badge').classList.contains('hidden')"));
    await evaluate("document.querySelector('#reload-button').click()");
    await ready("!document.querySelector('#reload-button').disabled");
    assert(await evaluate("document.querySelector('#dirty-badge').classList.contains('hidden')"));

    await evaluate("document.querySelector('.tool-hub-tab-btn[data-tool=\"wonder-cropper\"]').click()");
    await ready("document.querySelector('#cropper-meta').textContent.includes('Crop')");
    await delay(500);
    await evaluate("document.querySelector('#cropper-canvas').dispatchEvent(new WheelEvent('wheel', { deltaY: 100, cancelable: true }))");
    const crop = await evaluate("document.querySelector('#cropper-meta').textContent");
    await evaluate("document.querySelector('#cropper-save').click()");
    assert(await evaluate("document.querySelector('#cropper-reload').disabled && [...document.querySelectorAll('#cropper-task-list button')].every(b => b.disabled)"));
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#cropper-save').disabled");
    assert.equal(await evaluate("document.querySelector('#cropper-meta').textContent"), crop);
    assert.match(await evaluate("document.querySelector('#cropper-status').textContent"), /Your crop is preserved/);

    const job = { id: 'probe', status: 'running', line_cursor: 1, lines: ['first log'], lines_reset: true,
      operation: {}, resource_ids: [], source_snapshots: [], artifacts: [], metadata: {}, declared_outputs: [],
      formal_output_changes: [], staging_extra_files: [], missing_outputs: [] };
    await evaluate(`__probe.job = ${JSON.stringify(job)}; document.querySelector('.tool-hub-tab-btn[data-tool="media-studio"]').click(); document.querySelector('#media-run').click()`);
    await ready("document.querySelector('#media-status').textContent.includes('retrying')");
    assert.equal(await evaluate("document.querySelector('#media-log').textContent"), 'first log');
    await ready("__probe.polls >= 2 && document.querySelector('#media-status').textContent === 'running'");
    await evaluate("document.querySelector('#media-cancel').click()");
    await ready("document.querySelector('#media-status').textContent.includes('Cancellation failed') && !document.querySelector('#media-cancel').disabled");
    await evaluate('__probe.terminal = true');
    await ready("document.querySelector('#media-status').textContent.includes('generator probe failure')");
    assert.equal(await evaluate("document.querySelector('#media-log').textContent"), 'first log');
    assert(await evaluate("!document.querySelector('#media-run').disabled && document.querySelector('#media-cancel').disabled"));
    for (const [tool, prefix, run] of [['media-studio', 'media', 'media-run'], ['wonder-cropper', 'cropper', 'cropper-apply']]) {
      for (const status of [404, 422]) {
        await evaluate(`__probe.terminal = false; __probe.pollStatus = ${status}; document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click(); document.querySelector('#${run}').click()`);
        await ready(`document.querySelector('#${prefix}-status').textContent.includes('job query probe failure')`);
        if (status === 422) {
          assert(await evaluate(`!document.querySelector('#${prefix}-poll-stop').hidden && document.querySelector('#${run}').disabled`));
          await evaluate(`document.querySelector('#${prefix}-poll-stop').click()`);
        }
        assert(await evaluate(`!document.querySelector('#${run}').disabled`));
        assert.match(await evaluate(`document.querySelector('#${prefix}-status').textContent`), /Stopped tracking job probe.*outcome unknown/);
        assert.equal(await evaluate(`document.querySelector('#${prefix}-log').textContent`), 'first log');
      }
    }
    assert.deepEqual(pageErrors, []);
    console.log('Chrome resource-state acceptance passed: four editors, unified Prompt, polling recovery, cancellation failure, job error, 404 unlock and 422 stop tracking on both pages; no page exceptions.');
    await send('Browser.close');
  } finally {
    if (ws) ws.close();
    if (chrome) chrome.kill();
    server.kill();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
