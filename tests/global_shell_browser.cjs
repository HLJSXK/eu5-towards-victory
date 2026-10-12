// WP-10: global shell acceptance. Mounted from resource_state_browser.cjs.
// Real DOM and real modules; the operations endpoint is intercepted, so no list is read from the
// server and nothing is written. The only business-state change is a cost/reward draft field, which
// is cleared again before the scenario returns.
const assert = require('node:assert/strict');

module.exports = async function globalShellAcceptance({ evaluate, ready }) {
  const dot = (tool) => `document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"] .tool-hub-tab-dot')`;
  const dotState = (tool) => evaluate(`(() => { const node = ${dot(tool)};
    return { hidden: node.hidden, dirty: node.classList.contains('dirty'), running: node.classList.contains('running'),
      jobs: node.dataset.jobs, title: node.title }; })()`);

  // --- dirty dot: edit cost/reward, then switch tools -------------------------------------------
  // Earlier scenarios leave this editor in an unknown state; reload first so "starts clean" is real.
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').click()`);
  await ready("!!document.querySelector('#panels input[type=number]')");
  await evaluate(`document.querySelector('#cr-reload-btn').click()`);
  await ready("!document.querySelector('#cr-reload-btn').disabled && !document.querySelector('#cr-save-btn').disabled");
  await ready(`${dot('cost-reward')}.hidden`);
  const clean = await dotState('cost-reward');
  assert.equal(clean.hidden, true, 'cost/reward starts clean');
  await evaluate(`{ const input = document.querySelector('#panels input[type=number]');
    input.value = '0.321'; input.dispatchEvent(new Event('input', { bubbles: true })); }`);
  await ready(`${dot('cost-reward')} && !${dot('cost-reward')}.hidden`);
  const dirty = await dotState('cost-reward');
  assert.equal(dirty.dirty, true);
  assert.match(dirty.title, /有未保存的更改/);

  // Switching to another tool must not clear it, and the tab label must survive the dot span.
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="victory-tree"]').click()`);
  assert.equal((await dotState('cost-reward')).hidden, false, 'the dot survives a tool switch');
  assert.equal(await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').dataset.dirty`), 'true');
  assert.match(await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').textContent`), /花费\/奖励编辑器/);
  assert.equal((await dotState('victory-tree')).hidden, true, 'an untouched tool stays clean');

  // --- beforeunload is blocked while a draft is dirty -------------------------------------------
  const blocked = await evaluate(`(() => { const event = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(event); return event.defaultPrevented; })()`);
  assert.equal(blocked, true, 'leaving with unsaved changes must be confirmed');
  assert.deepEqual(await evaluate('window.__toolShell.dirtyTools()'), ['cost-reward']);

  // --- operations panel: a constructed job response, never a real one ---------------------------
  const now = await evaluate('Date.now() / 1000');
  await evaluate(`__probe.intercept = async (path) => {
    if (path === '/api/operations') return Response.json({ operations: [
      { id: 'probe-run', kind: 'resource_commit', status: 'running', resource_ids: ['editor.cost_reward'], created_at: ${now} },
      { id: 'probe-fail', kind: 'media_job', status: 'failed', resource_ids: ['media.historical'],
        error: 'operations probe failure', created_at: ${now} },
      { id: 'probe-done', kind: 'generator_run', status: 'succeeded', resource_ids: [], created_at: ${now} }] });
    if (path === '/api/operations/probe-run') return Response.json({ id: 'probe-run', operation_id: 'probe-run',
      kind: 'resource_commit', status: 'running', resource_ids: ['editor.cost_reward'], created_at: ${now},
      events: [{ at: ${now}, level: 'info', message: 'probe event line' }] });
    return null;
  }`);
  await evaluate('window.__operationsPanel.refresh()');
  await ready("document.querySelector('#operations-panel .operations-row')");
  assert.equal(await evaluate("document.querySelector('#operations-panel').dataset.state"), 'loaded');
  assert.match(await evaluate("document.querySelector('#operations-panel .operations-status-bar').textContent"),
    /共 3 项：在跑 1，失败 1，最近 1/);
  assert.match(await evaluate("document.querySelector('#operations-panel .operations-results').textContent"),
    /在跑作业[\s\S]*失败项[\s\S]*最近操作/);
  assert.match(await evaluate("document.querySelector('[data-operation-id=\"probe-fail\"]').textContent"), /operations probe failure/);

  // The running operation marks its own tool, without disturbing the dirty dot.
  await ready(`${dot('cost-reward')}.classList.contains('running')`);
  const running = await dotState('cost-reward');
  assert.equal(running.running, true);
  assert.equal(running.jobs, '1');
  assert.equal(running.dirty, true, 'dirty and running are reported together');

  // Expanding a row pulls the detail through the shared display renderer.
  await evaluate(`document.querySelector('[data-operation-toggle="probe-run"]').click()`);
  await ready("!document.querySelector('[data-operation-detail=\"probe-run\"]').hidden");
  const detail = await evaluate("document.querySelector('[data-operation-detail=\"probe-run\"]').textContent");
  assert.match(detail, /probe-run/);
  assert.match(detail, /probe event line/);
  assert.equal(await evaluate(`document.querySelector('[data-operation-toggle="probe-run"]').textContent`), '收起');
  await evaluate(`document.querySelector('[data-operation-toggle="probe-run"]').click()`);
  await ready("document.querySelector('[data-operation-detail=\"probe-run\"]').hidden");

  // --- the victory tree no longer inherits the shared "保存并重新生成" wording --------------------
  // Read-only live preview; the dialog is cancelled before commit, so no file is written.
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="victory-tree"]').click()`);
  await ready("!!document.querySelector('#nodeList input')");
  await evaluate(`{ const input = document.querySelector('#nodeList input');
    input.value = '0.432'; input.dispatchEvent(new Event('change', { bubbles: true })); }`);
  await ready(`${dot('victory-tree')} && !${dot('victory-tree')}.hidden`);
  await evaluate(`document.querySelector('#vt-save-btn').click()`);
  await ready("document.querySelector('#vt-preview dialog').open");
  const treeCopy = await evaluate(`(() => ({ summary: document.querySelector('#vt-preview .diff-summary').textContent,
    status: document.querySelector('#vt-status').textContent, dialog: document.querySelector('#vt-preview dialog').textContent }))()`);
  assert.equal(/重新生成/.test(treeCopy.summary), false, `victory tree preview summary: ${treeCopy.summary}`);
  assert.match(treeCopy.summary, /保存坐标（不触发生成）/);
  assert.equal(/重新生成/.test(treeCopy.dialog), false, 'no regeneration wording anywhere in the victory tree preview');
  assert.equal(/重新生成/.test(await evaluate("document.querySelector('#vt-save-btn').textContent")), false);
  await evaluate(`document.querySelector('#vt-preview [data-cancel]').click()`);
  await ready("!document.querySelector('#vt-save-btn').disabled");
  await evaluate(`document.querySelector('#vt-reload-btn').click()`);
  await ready("!document.querySelector('#vt-reload-btn').disabled");
  await ready(`${dot('victory-tree')}.hidden`);

  // --- back to a clean workspace: no dot, no leave confirmation ---------------------------------
  await evaluate("__probe.intercept = async (path) => path === '/api/operations' ? Response.json({ operations: [] }) : null");
  await evaluate('window.__operationsPanel.refresh()');
  await ready(`${dot('cost-reward')} && !${dot('cost-reward')}.classList.contains('running')`);
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').click()`);
  await evaluate(`document.querySelector('#cr-reload-btn').click()`);
  await ready("!document.querySelector('#cr-reload-btn').disabled && document.querySelector('#cr-save-btn').disabled === false");
  await ready(`${dot('cost-reward')}.hidden`);
  const released = await evaluate(`(() => { const event = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(event); return event.defaultPrevented; })()`);
  assert.equal(released, false, 'a clean workspace leaves without a prompt');
  assert.deepEqual(await evaluate('window.__toolShell.dirtyTools()'), []);
  await evaluate('__probe.intercept = null');
  console.log('Global shell acceptance passed: dirty dot on edits, dot cleared on reload, beforeunload blocked only while dirty, operations panel rendered running/failed/recent with detail expansion, victory tree preview copy carries no 重新生成.');
};
