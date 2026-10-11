// Real ES modules and DOM, live GETs and read-only previews, intercepted writes; no game data is changed.
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
        if (path === '/api/wonder-localization/catalog' && probe.catalogFailure) return Response.json({ detail: 'catalog probe failure' }, { status: 503 });
        if (path === '/api/jobs' && options.method === 'POST') return Response.json(probe.job);
        if (path.endsWith('/cancel')) return Response.json({ detail: 'cancel probe failure' }, { status: 503 });
        if (path.startsWith('/api/jobs/')) {
          probe.polls++;
          if (probe.pollStatus) return Response.json({ detail: 'job query probe failure' }, { status: probe.pollStatus });
          if (probe.polls === 1) throw new TypeError('network probe failure');
          return Response.json({ ...probe.job, lines: [], lines_reset: false,
            operation: { ...probe.job.operation, error: probe.terminal ? 'generator probe failure' : null,
              status: probe.terminal ? 'failed' : 'running' } });
        }
        if (path.endsWith('/preview')) return liveFetch(url, options);
        if (options.method === 'POST') {
          await new Promise((resolve) => { probe.release = resolve; });
          if (probe.commitPayload) return Response.json(probe.commitPayload);
          return Response.json(probe.commitStatus === 500
            ? { detail: 'generation probe failure', operation_id: 'probe-commit', generation: { status: 'failed',
              steps: [{ id: 'probe.py', status: 'failed', returncode: 1 }], rollback: { status: 'succeeded', errors: [] } } }
            : { code: probe.code || 'resource_changed', detail: 'probe source changed' }, { status: probe.commitStatus || 409 });
        }
        if (probe.gates.has(path)) await new Promise((resolve) => { probe.release = resolve; });
        const response = await liveFetch(url, options);
        const malicious = '<img src=x onerror="window.__xss=true"> & "text"';
        if (path === '/api/resources/editor.victory_tree') {
          const payload = await response.json(); payload.draft.paths[0].nodes[0].label = malicious; return Response.json(payload);
        }
        if (path === '/api/resources/editor.wonder_crop') {
          const payload = await response.json(); payload.draft.tasks[0].pngPath = malicious; return Response.json(payload);
        }
        if (path === '/api/media/bootstrap') {
          const payload = await response.json(); payload.tools[0].label = malicious; return Response.json(payload);
        }
        return response;
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
      const prefix = tool === 'cost-reward' ? 'cr' : 'vt';
      await ready(`document.querySelector('#${prefix}-preview dialog').open`);
      assert.match(await evaluate(`document.querySelector('#${prefix}-preview tbody').textContent`), /0\.123/);
      assert.equal(await evaluate(`__probe.requests.filter(r => r.path === '/api/resources/${resource}/commit').length`), 0);
      await evaluate(`document.querySelector('#${prefix}-preview [data-cancel]').click()`);
      await ready(`!document.querySelector('${save}').disabled`);
      assert.equal(await evaluate(`Number(document.querySelector('${input}').value)`), 0.123);
      // Leaving the tool while the preview is in flight must not open an invisible modal that blocks the page.
      await evaluate(`document.querySelector('${save}').click(); document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click()`);
      await ready(`document.querySelector('#${prefix}-preview dialog').open`);
      assert(await evaluate(`document.querySelector('#${prefix}-preview dialog').getClientRects().length > 0`), `${tool} preview visible from another tool`);
      await evaluate(`document.querySelector('#${prefix}-preview [data-cancel]').click(); document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click()`);
      await ready(`!document.querySelector('${save}').disabled`);
      await evaluate(`document.querySelector('${save}').click()`);
      await ready(`document.querySelector('#${prefix}-preview dialog').open`);
      await evaluate(`__probe.release = null; document.querySelector('#${prefix}-preview [data-confirm]').click()`);
      await ready('!!__probe.release');
      assert(await evaluate(`__probe.requests.findLast(r => r.path === '/api/resources/${resource}/preview').body === __probe.requests.findLast(r => r.path === '/api/resources/${resource}/commit').body`));
      await evaluate('__probe.release()');
      await ready(`!document.querySelector('${save}').disabled`);
      assert.equal(await evaluate(`Number(document.querySelector('${input}').value)`), 0.123);
      assert.match(await evaluate(`document.querySelector('${log}').textContent`), /probe source changed/);
      await evaluate(`__probe.commitStatus = 500; document.querySelector('${save}').click()`);
      await ready(`document.querySelector('#${prefix}-preview dialog').open`);
      await evaluate(`__probe.release = null; document.querySelector('#${prefix}-preview [data-confirm]').click()`);
      await ready('!!__probe.release');
      await evaluate('__probe.release()');
      await ready(`!document.querySelector('${save}').disabled`);
      assert.match(await evaluate(`document.querySelector('${log}').textContent`), /probe-commit[\s\S]*probe.py[\s\S]*恢复结果: 已完成/);
      assert.equal(await evaluate(`Number(document.querySelector('${input}').value)`), 0.123);
      await evaluate(`__probe.commitStatus = null; __probe.gates.set('/api/resources/${resource}', true); document.querySelector('${reload}').click()`);
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
    await ready("document.querySelector('#wonder-preview dialog').open");
    assert.match(await evaluate("document.querySelector('#wonder-preview tbody').textContent"), /unified prompt probe/);
    assert.equal(await evaluate("__probe.requests.filter(r => r.path === '/api/resources/editor.wonder/commit').length"), 0);
    await evaluate("document.querySelector('#wonder-preview [data-cancel]').click()");
    await ready("!document.querySelector('#save-button').disabled");
    assert.equal(await evaluate("document.querySelector('[data-ritual-prompt-input]').value"), 'unified prompt probe');
    await evaluate("document.querySelector('#save-button').click(); document.querySelector('.tool-hub-tab-btn[data-tool=\"cost-reward\"]').click()");
    await ready("document.querySelector('#wonder-preview dialog').open");
    assert(await evaluate("document.querySelector('#wonder-preview dialog').getClientRects().length > 0"));
    await evaluate("__probe.release = null; document.querySelector('#wonder-preview [data-confirm]').click()");
    await ready('!!__probe.release');
    const commit = await evaluate("JSON.parse(__probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/commit').body)");
    assert.equal(commit.wonders[0].ritual_prompt, 'unified prompt probe');
    assert(await evaluate("__probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/preview').body === __probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/commit').body"));
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#save-button').disabled");
    await evaluate("document.querySelector('.tool-hub-tab-btn[data-tool=\"wonder-localization\"]').click()");
    assert.equal(await evaluate("document.querySelector('[data-ritual-prompt-input]').value"), 'unified prompt probe');
    assert(await evaluate("!document.querySelector('#dirty-badge').classList.contains('hidden')"));
    assert.match(await evaluate("document.querySelector('#log-output').textContent"), /probe source changed/);
    await evaluate("__probe.commitStatus = 500; document.querySelector('#save-button').click()");
    await ready("document.querySelector('#wonder-preview dialog').open");
    await evaluate("__probe.release = null; document.querySelector('#wonder-preview [data-confirm]').click()");
    await ready('!!__probe.release');
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#save-button').disabled");
    assert.match(await evaluate("document.querySelector('#log-output').textContent"), /probe-commit[\s\S]*probe.py[\s\S]*恢复结果: 已完成/);
    assert.equal(await evaluate("document.querySelector('[data-ritual-prompt-input]').value"), 'unified prompt probe');
    await evaluate('__probe.commitStatus = null');
    await evaluate(`(async () => {
      const resource = await (await fetch('/api/resources/editor.wonder')).json();
      const id = JSON.parse(__probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/commit').body).current_wonder_id;
      const wonder = await (await fetch('/api/wonder-localization/wonders/' + id)).json();
      wonder.catalog_version = 'probe-committed-catalog';
      __probe.commitPayload = { ...resource, wonders: resource.draft.wonders, wonder, operation_id: 'probe-saved', operation: { status: 'succeeded' } };
      __probe.catalogFailure = true;
      document.querySelector('#save-button').click();
    })()`);
    await ready("document.querySelector('#wonder-preview dialog').open");
    await evaluate("__probe.release = null; document.querySelector('#wonder-preview [data-confirm]').click()");
    await ready('!!__probe.release');
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#retry-detail-button').hidden && !document.querySelector('#retry-detail-button').disabled");
    assert.match(await evaluate("document.querySelector('#status-badge').textContent"), /已保存.*详情加载失败.*catalog probe failure/);
    assert(await evaluate("document.querySelector('#dirty-badge').classList.contains('hidden')"));
    assert.match(await evaluate("document.querySelector('#log-output').textContent"), /probe-saved/);
    const commitsBeforeRetry = await evaluate("__probe.requests.filter(r => r.path === '/api/resources/editor.wonder/commit').length");
    await evaluate("__probe.catalogFailure = false; __probe.commitPayload = null; document.querySelector('#retry-detail-button').click()");
    await ready("document.querySelector('#retry-detail-button').hidden && !document.querySelector('#save-button').disabled");
    assert.equal(await evaluate("__probe.requests.filter(r => r.path === '/api/resources/editor.wonder/commit').length"), commitsBeforeRetry);
    assert.match(await evaluate("document.querySelector('#log-output').textContent"), /probe-saved/);
    await evaluate("document.querySelector('#reload-button').click()");
    await ready("!document.querySelector('#reload-button').disabled");
    assert(await evaluate("document.querySelector('#dirty-badge').classList.contains('hidden')"));

    await evaluate("document.querySelector('.tool-hub-tab-btn[data-tool=\"wonder-cropper\"]').click()");
    await ready("document.querySelector('#cropper-meta').textContent.includes('裁剪')");
    await delay(500);
    await evaluate("document.querySelector('#cropper-canvas').dispatchEvent(new WheelEvent('wheel', { deltaY: 100, cancelable: true }))");
    const crop = await evaluate("document.querySelector('#cropper-meta').textContent");
    await evaluate("document.querySelector('#cropper-save').click()");
    assert(await evaluate("document.querySelector('#cropper-reload').disabled && [...document.querySelectorAll('#cropper-task-list button')].every(b => b.disabled)"));
    await evaluate('__probe.release()');
    await ready("!document.querySelector('#cropper-save').disabled");
    assert.equal(await evaluate("document.querySelector('#cropper-meta').textContent"), crop);
    assert.match(await evaluate("document.querySelector('#cropper-status').textContent"), /裁剪草稿已保留/);

    const job = { line_cursor: 1, lines: ['first log'], lines_reset: true,
      operation: { id: 'probe', status: 'running', error: null, resource_ids: [] }, source_snapshots: [], artifacts: [], metadata: {}, declared_outputs: [],
      formal_output_changes: [], staging_extra_files: [], missing_outputs: [] };
    await evaluate(`__probe.job = ${JSON.stringify(job)}; document.querySelector('.tool-hub-tab-btn[data-tool="media-studio"]').click(); document.querySelector('#media-run').click()`);
    await ready("document.querySelector('#media-status').textContent.includes('正在重试')");
    assert.equal(await evaluate("document.querySelector('#media-log').textContent"), 'first log');
    await ready("__probe.polls >= 2 && document.querySelector('#media-status').textContent === '运行中'");
    await evaluate("document.querySelector('#media-cancel').click()");
    await ready("document.querySelector('#media-status').textContent.includes('取消失败') && !document.querySelector('#media-cancel').disabled");
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
        assert.match(await evaluate(`document.querySelector('#${prefix}-status').textContent`), /已停止跟踪作业 probe.*服务端结果未知/);
        assert.equal(await evaluate(`document.querySelector('#${prefix}-log').textContent`), 'first log');
      }
    }
    const fileJob = { ...job, operation: { ...job.operation, status: 'failed', error: 'output probe failure' }, outputs_may_be_partial: true,
      publication_rollback_failed: true, declared_outputs: ['probe.dds'], missing_outputs: ['probe.dds'],
      source_snapshots: [{ path: '<input.png>', sha256: 'missing' }],
      staging_extra_files: ['staging/intermediate'], formal_output_changes: ['probe.dds'] };
    let report;
    for (const [tool, prefix, run] of [['media-studio', 'media', 'media-run'], ['wonder-cropper', 'cropper', 'cropper-apply']]) {
      await evaluate(`__probe.job = ${JSON.stringify(fileJob)}; __probe.pollStatus = null; document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click(); document.querySelector('#${run}').click()`);
      await ready(`document.querySelector('#${prefix}-status').textContent.includes('output probe failure')`);
      const text = await evaluate(`document.querySelector('#${prefix}-file-report').textContent`);
      if (report) assert.equal(text, report); else report = text;
      assert.match(text, /<input.png>（可选，缺失）[\s\S]*probe.dds（缺失）[\s\S]*发布恢复失败/);
      assert(await evaluate(`!document.querySelector('#${prefix}-files').hidden`));
    }
    assert(await evaluate(`document.querySelector('#media-tool-list button strong').textContent.includes('<img') && !document.querySelector('#media-tool-list img')`));
    await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="victory-tree"]').click()`);
    assert(await evaluate(`document.querySelector('#nodeList .title').textContent.includes('<img') && !document.querySelector('#nodeList img')`));
    assert(await evaluate(`document.querySelector('#cropper-meta').textContent.includes('<img') && !document.querySelector('#cropper-meta img') && !window.__xss`));
    const modules = await evaluate(`Promise.all([import('/static/display.js'), import('/static/job_panel.js'), import('/static/editor_panel.js')]).then(m => m.every(x => Object.keys(x).length > 0))`);
    assert(modules);
    assert.deepEqual(pageErrors, []);
    console.log('Chrome acceptance passed: live diffs in three editors, cancellation and exact preview/commit bodies, hidden-tool modal, 409/generation diagnostics, Wonder committed state and detail-only retry, four-editor state, media/cropper reports and polling, escaped data; no page exceptions.');
    await send('Browser.close');
  } finally {
    if (ws) ws.close();
    if (chrome) chrome.kill();
    server.kill();
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
