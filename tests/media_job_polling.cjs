// Run with: node --test tests/media_job_polling.cjs
const assert = require('node:assert/strict');
const { test } = require('node:test');

// Exercise the shared job panel as native modules; media page wiring is covered in Chrome.
async function studio(t) {
  const { createJobPanel } = await import('../towards_victory_editor_web/static/job_panel.js');
  const { setControlsBusy } = await import('../towards_victory_editor_web/static/resource_state.js');
  const previous = { document: global.document, fetch: global.fetch, setTimeout: global.setTimeout, clearTimeout: global.clearTimeout };
  const controls = {}, listeners = {}, timers = new Map();
  const formInput = { disabled: false };
  let timerId = 0;
  const control = (id) => controls[id] ||= {
    textContent: '', dataset: {}, disabled: false, hidden: false,
    addEventListener(event, handler) { listeners[id + ':' + event] = handler; }, appendChild() {},
  };
  global.document = { getElementById: control };
  global.setTimeout = fn => { timers.set(++timerId, fn); return timerId; };
  global.clearTimeout = id => timers.delete(id);
  t.after(() => Object.assign(global, previous));
  const panel = createJobPanel({ root: control('media-job'), prefix: 'media', allowCancel: true, onChange() {
    setControlsBusy([formInput], panel.poller.active);
    control('media-run').disabled = panel.poller.active;
  } });
  return { control, timers, listeners, formInput, panel, state: () => panel.poller };
}

function job(id, cursor, lines, reset = false) {
  return {
    line_cursor: cursor, lines, lines_reset: reset,
    outputs_may_be_partial: false, source_snapshots: [],
    operation: { id, status: 'running', error: null, resource_ids: [] },
    formal_output_changes: [], staging_extra_files: [],
    artifacts: [], metadata: {}, declared_outputs: [], missing_outputs: [],
  };
}

test('an interrupted publication warns about formal outputs and retained backups', async t => {
  const app = await studio(t);
  app.interrupted = { ...job('interrupted', 1, [], true),
    operation: { ...job('interrupted', 1, [], true).operation, status: 'failed', interrupted: true }, outputs_may_be_partial: true };
  app.state().start(app.interrupted);
  const message = app.control('media-status').textContent;
  assert.match(message, /可能部分发布/);
  assert.match(message, /保留的备份/);
  assert.doesNotMatch(message, /草稿已保留/);
});

test('a job interrupted before it started does not warn about partial publication', async t => {
  const app = await studio(t);
  app.queued = { ...job('queued', 1, [], true),
    operation: { ...job('queued', 1, [], true).operation, status: 'failed', interrupted: true }, outputs_may_be_partial: false };
  app.state().start(app.queued);
  assert.equal(app.control('media-status').textContent, '失败');
});

test('discarded intermediate files are separate from formal output conflicts', async t => {
  const app = await studio(t);
  app.completed = { ...job('generated', 1, [], true),
    operation: { ...job('generated', 1, [], true).operation, status: 'succeeded' },
    staging_extra_files: ['staging/intermediate.bin'] };
  app.state().start(app.completed);
  assert.equal(app.control('media-status').textContent, '已完成');
  assert.match(app.control('media-file-report').textContent, /不参与发布的中间文件/);
  assert.doesNotMatch(app.control('media-file-report').textContent, /未声明|需核对/);

  app.conflict = { ...job('conflict', 2, [], true),
    operation: { ...job('conflict', 2, [], true).operation, status: 'failed' },
    formal_output_changes: ['output.json'], outputs_may_be_partial: true };
  app.state().start(app.conflict);
  assert.match(app.control('media-status').textContent, /正式输出需人工核对/);
  assert.match(app.control('media-file-report').textContent, /正式输出在暂存区外发生变化/);
});

test('a late poll after cancellation cannot append duplicate lines', async t => {
  const app = await studio(t);
  const state = app.state();
  app.initial = job('first', 1, ['one'], true);
  app.state().start(app.initial);

  let respond;
  global.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.cancelled = job('first', 3, ['one', 'two', 'three'], true);
  app.state().accept(app.cancelled);
  respond(Response.json(job('first', 2, ['two'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'one\ntwo\nthree');
  assert.equal(state.cursor, 3);
});

test('a late response from an earlier job cannot change the current job', async t => {
  const app = await studio(t);
  const state = app.state();
  app.first = job('first', 1, ['old'], true);
  app.state().start(app.first);

  let respond;
  global.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.second = job('second', 2, ['new one', 'new two'], true);
  app.state().start(app.second);
  respond(Response.json(job('first', 3, ['old two', 'old three'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'new one\nnew two');
  assert.equal(state.cursor, 2);
  assert.equal(state.jobId, 'second');
});

test('transient polling failure retains the cursor and logs, then resumes', async t => {
  const app = await studio(t);
  app.state().start(job('retry', 1, ['one'], true));
  global.fetch = async () => { throw new Error('offline'); };
  await app.state().poll();
  assert.equal(app.state().cursor, 1);
  assert.equal(app.control('media-log').textContent, 'one');
  assert.match(app.control('media-status').textContent, /正在重试.*offline/);
  assert.equal(app.timers.size, 1);
  global.fetch = async (url) => {
    assert.equal(url, '/api/jobs/retry?after_line=1');
    return Response.json({ ...job('retry', 2, ['two']),
      operation: { ...job('retry', 2, ['two']).operation, status: 'failed', error: 'generator failed' } });
  };
  await app.state().poll();
  assert.equal(app.control('media-log').textContent, 'one\ntwo');
  assert.match(app.control('media-status').textContent, /失败: generator failed/);
  assert.equal(app.state().active, false);
  assert.equal(app.timers.size, 0);
});

test('a nontransient polling failure allows stopping without losing the job or accepting late responses', async t => {
  const app = await studio(t);
  app.state().start(job('retry', 1, ['one'], true));
  global.fetch = async () => Response.json({ detail: 'invalid cursor' }, { status: 422 });
  await app.state().poll();
  assert.equal(app.timers.size, 0);
  assert.equal(app.control('media-poll-retry').hidden, false);
  assert.equal(app.state().jobId, 'retry');
  assert.equal(app.control('media-poll-stop').hidden, false);
  let respond;
  global.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.listeners['media-poll-stop:click']();
  respond(Response.json(job('retry', 2, ['late'])));
  await pending;
  assert.equal(app.state().active, false);
  assert.equal(app.control('media-run').disabled, false);
  assert.equal(app.formInput.disabled, false);
  assert.equal(app.control('media-log').textContent, 'one');
  assert.match(app.control('media-status').textContent, /已停止跟踪作业 retry.*服务端结果未知.*invalid cursor/);
});

for (const status of [404, 410]) test(`${status} stops tracking and unlocks the form while preserving diagnostics`, async t => {
  const app = await studio(t);
  app.state().start(job('missing', 1, ['one'], true));
  assert.equal(app.formInput.disabled, true);
  global.fetch = async () => Response.json({ detail: 'unknown job' }, { status });
  await app.state().poll();
  assert.equal(app.state().active, false);
  assert.equal(app.timers.size, 0);
  assert.equal(app.state().jobId, 'missing');
  assert.equal(app.control('media-log').textContent, 'one');
  assert.equal(app.control('media-run').disabled, false);
  assert.equal(app.formInput.disabled, false);
  assert.equal(app.control('media-poll-retry').hidden, true);
  assert.match(app.control('media-status').textContent, /已停止跟踪作业 missing.*服务端结果未知.*unknown job/);
});

test('cancellation failure remains visible across polling and allows another cancel', async t => {
  const app = await studio(t);
  app.state().start(job('cancel', 1, ['one'], true));
  global.fetch = async () => { throw new Error('cancel offline'); };
  await app.listeners['media-cancel:click']();
  assert.equal(app.state().active, true);
  assert.equal(app.control('media-cancel').disabled, false);
  app.state().accept(job('cancel', 2, ['two']));
  assert.match(app.control('media-status').textContent, /取消失败: cancel offline/);
  assert.equal(app.control('media-log').textContent, 'one\ntwo');
});

test('a cancellation failure is cleared once the job reaches a terminal state', async t => {
  const app = await studio(t);
  app.state().start(job('cancel', 1, ['one'], true));
  global.fetch = async () => { throw new Error('cancel offline'); };
  await app.listeners['media-cancel:click']();
  app.state().accept({ ...job('cancel', 2, ['two']),
    operation: { ...job('cancel', 2, ['two']).operation, status: 'succeeded' } });
  assert.equal(app.control('media-status').textContent, '已完成');
  assert.notEqual(app.control('media-status').dataset.kind, 'error');
});

test('same-cursor terminal cancellation discards a late running response', async t => {
  const app = await studio(t);
  app.state().start(job('cancel', 1, ['one'], true));
  let respond;
  global.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.state().accept({ ...job('cancel', 1, []),
    operation: { ...job('cancel', 1, []).operation, status: 'cancelled' } });
  respond(Response.json(job('cancel', 1, [])));
  await pending;
  assert.equal(app.control('media-status').textContent, '已取消');
  assert.equal(app.state().active, false);
});

test('a job detached by Stop tracking stays cancellable and resumes tracking from the cancel snapshot', async t => {
  const app = await studio(t);
  app.state().start(job('detached', 1, ['one'], true));
  global.fetch = async () => Response.json({ detail: 'invalid cursor' }, { status: 422 });
  await app.state().poll();
  app.listeners['media-poll-stop:click']();
  assert.equal(app.state().active, false);
  assert.equal(app.control('media-cancel').disabled, false);
  assert.match(app.control('media-status').textContent, /可取消/);
  global.fetch = async () => Response.json({ ...job('detached', 2, ['one', 'cancel requested'], true),
    operation: { ...job('detached', 2, [], true).operation, status: 'cancelling' } });
  await app.listeners['media-cancel:click']();
  assert.equal(app.state().active, true);
  assert.equal(app.control('media-log').textContent, 'one\ncancel requested');
  assert.equal(app.control('media-run').disabled, true);
});


test('accepted cancellation reports a rendering failure without claiming the request failed', async t => {
  const app = await studio(t);
  app.state().start(job('cancel-render', 1, ['one'], true));
  let value = '';
  Object.defineProperty(app.control('media-file-report'), 'textContent', {
    get: () => value, set(next) { value = next; throw new Error('file report render failed'); },
  });
  global.fetch = async () => Response.json({ ...job('cancel-render', 2, ['cancelled']),
    operation: { ...job('cancel-render', 2, []).operation, status: 'cancelled' } });
  await app.listeners['media-cancel:click']();
  assert.equal(app.state().active, false);
  assert.match(app.control('media-status').textContent, /取消请求已受理，但页面更新失败/);
  assert.match(app.control('media-log').textContent, /file report render failed/);
});


for (const phase of ['bootstrap', 'submit']) test('media ' + phase + ' failure reaches the copyable log', async t => {
  const app = await studio(t);
  const previousWindow = global.window;
  global.window = {};
  global.document.querySelectorAll = () => [];
  t.after(() => { global.window = previousWindow; });
  global.fetch = async url => {
    if (phase === 'submit' && url === '/api/media/bootstrap') return Response.json({ tools: [] });
    throw new Error(phase + ' probe failed');
  };
  await import('../towards_victory_editor_web/static/media_studio.js?' + phase);
  for (let i = 0; i < 4; i++) await new Promise(setImmediate);
  if (phase === 'submit') await app.listeners['media-run:click']();
  assert.match(app.control('media-log').textContent, new RegExp(phase + ' probe failed'));
});
