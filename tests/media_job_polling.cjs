// Run with: node --test tests/media_job_polling.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function studio() {
  const controls = {};
  const listeners = {};
  const timers = new Map();
  const formInput = { disabled: false };
  let timerId = 0;
  const control = (id) => controls[id] ||= {
    textContent: '', disabled: false, hidden: false,
    addEventListener(event, handler) { listeners[id + ":" + event] = handler; }, appendChild() {},
  };
  const context = vm.createContext({
    document: { getElementById: control, querySelectorAll: () => [formInput] },
    setTimeout: (fn) => { timers.set(++timerId, fn); return timerId; },
    clearTimeout: (id) => timers.delete(id),
    window: { setTimeout: () => 1, clearTimeout() {} },
    fetch: () => new Promise(() => {}),
  });
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/api.js'), 'utf8').replace(/^export /gm, ''), context);
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/resource_state.js'), 'utf8').replace(/^export /gm, ''), context);
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/media_studio.js'), 'utf8').replace(/^import .*;\r?\n/gm, ''), context);
  return { context, control, timers, listeners, formInput, state: () => vm.runInContext('poller', context) };
}

function job(id, cursor, lines, reset = false) {
  return {
    id, line_cursor: cursor, lines, lines_reset: reset, status: 'running',
    outputs_may_be_partial: false, resource_ids: [], source_snapshots: [],
    operation: {},
    formal_output_changes: [], staging_extra_files: [],
    artifacts: [], metadata: {}, declared_outputs: [], missing_outputs: [],
  };
}

test('an interrupted publication warns about formal outputs and retained backups', () => {
  const app = studio();
  app.context.interrupted = { ...job('interrupted', 1, [], true), status: 'failed',
    operation: { interrupted: true }, outputs_may_be_partial: true };
  vm.runInContext('poller.start(interrupted)', app.context);
  const message = app.control('media-status').textContent;
  assert.match(message, /may be partially published/);
  assert.match(message, /retained backups/);
  assert.doesNotMatch(message, /preserved/);
});

test('a job interrupted before it started does not warn about partial publication', () => {
  const app = studio();
  app.context.queued = { ...job('queued', 1, [], true), status: 'failed',
    operation: { interrupted: true }, outputs_may_be_partial: false };
  vm.runInContext('poller.start(queued)', app.context);
  assert.equal(app.control('media-status').textContent, 'failed');
});

test('discarded intermediate files are separate from formal output conflicts', () => {
  const app = studio();
  app.context.completed = { ...job('generated', 1, [], true), status: 'succeeded',
    staging_extra_files: ['staging/intermediate.bin'] };
  vm.runInContext('poller.start(completed)', app.context);
  assert.equal(app.control('media-status').textContent, 'succeeded');
  assert.match(app.control('media-file-report').textContent, /Intermediate files excluded from publication/);
  assert.doesNotMatch(app.control('media-file-report').textContent, /Undeclared|review required/);

  app.context.conflict = { ...job('conflict', 2, [], true), status: 'failed',
    formal_output_changes: ['output.json'], outputs_may_be_partial: true };
  vm.runInContext('poller.start(conflict)', app.context);
  assert.match(app.control('media-status').textContent, /formal outputs require review/);
  assert.match(app.control('media-file-report').textContent, /Formal outputs changed outside staging/);
});

test('a late poll after cancellation cannot append duplicate lines', async () => {
  const app = studio();
  const state = app.state();
  app.context.initial = job('first', 1, ['one'], true);
  vm.runInContext('poller.start(initial)', app.context);

  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = vm.runInContext('poller.poll()', app.context);
  app.context.cancelled = job('first', 3, ['one', 'two', 'three'], true);
  vm.runInContext('poller.accept(cancelled)', app.context);
  respond(Response.json(job('first', 2, ['two'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'one\ntwo\nthree');
  assert.equal(state.cursor, 3);
});

test('a late response from an earlier job cannot change the current job', async () => {
  const app = studio();
  const state = app.state();
  app.context.first = job('first', 1, ['old'], true);
  vm.runInContext('poller.start(first)', app.context);

  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = vm.runInContext('poller.poll()', app.context);
  app.context.second = job('second', 2, ['new one', 'new two'], true);
  vm.runInContext('poller.start(second)', app.context);
  respond(Response.json(job('first', 3, ['old two', 'old three'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'new one\nnew two');
  assert.equal(state.cursor, 2);
  assert.equal(state.jobId, 'second');
});

test('transient polling failure retains the cursor and logs, then resumes', async () => {
  const app = studio();
  app.state().start(job('retry', 1, ['one'], true));
  app.context.fetch = async () => { throw new Error('offline'); };
  await app.state().poll();
  assert.equal(app.state().cursor, 1);
  assert.equal(app.control('media-log').textContent, 'one');
  assert.match(app.control('media-status').textContent, /retrying.*offline/);
  assert.equal(app.timers.size, 1);
  app.context.fetch = async (url) => {
    assert.equal(url, '/api/jobs/retry?after_line=1');
    return Response.json({ ...job('retry', 2, ['two']), status: 'failed', error: 'generator failed' });
  };
  await app.state().poll();
  assert.equal(app.control('media-log').textContent, 'one\ntwo');
  assert.match(app.control('media-status').textContent, /failed: generator failed/);
  assert.equal(app.state().active, false);
  assert.equal(app.timers.size, 0);
});

test('a nontransient polling failure allows stopping without losing the job or accepting late responses', async () => {
  const app = studio();
  app.state().start(job('retry', 1, ['one'], true));
  app.context.fetch = async () => Response.json({ detail: 'invalid cursor' }, { status: 422 });
  await app.state().poll();
  assert.equal(app.timers.size, 0);
  assert.equal(app.control('media-poll-retry').hidden, false);
  assert.equal(app.state().jobId, 'retry');
  assert.equal(app.control('media-poll-stop').hidden, false);
  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.listeners['media-poll-stop:click']();
  respond(Response.json(job('retry', 2, ['late'])));
  await pending;
  assert.equal(app.state().active, false);
  assert.equal(app.control('media-run').disabled, false);
  assert.equal(app.formInput.disabled, false);
  assert.equal(app.control('media-log').textContent, 'one');
  assert.match(app.control('media-status').textContent, /Stopped tracking job retry.*outcome unknown.*invalid cursor/);
});

for (const status of [404, 410]) test(`${status} stops tracking and unlocks the form while preserving diagnostics`, async () => {
  const app = studio();
  app.state().start(job('missing', 1, ['one'], true));
  assert.equal(app.formInput.disabled, true);
  app.context.fetch = async () => Response.json({ detail: 'unknown job' }, { status });
  await app.state().poll();
  assert.equal(app.state().active, false);
  assert.equal(app.timers.size, 0);
  assert.equal(app.state().jobId, 'missing');
  assert.equal(app.control('media-log').textContent, 'one');
  assert.equal(app.control('media-run').disabled, false);
  assert.equal(app.formInput.disabled, false);
  assert.equal(app.control('media-poll-retry').hidden, true);
  assert.match(app.control('media-status').textContent, /Stopped tracking job missing.*outcome unknown.*unknown job/);
});

test('cancellation failure remains visible across polling and allows another cancel', async () => {
  const app = studio();
  app.state().start(job('cancel', 1, ['one'], true));
  app.context.fetch = async () => { throw new Error('cancel offline'); };
  await app.listeners['media-cancel:click']();
  assert.equal(app.state().active, true);
  assert.equal(app.control('media-cancel').disabled, false);
  app.state().accept(job('cancel', 2, ['two']));
  assert.match(app.control('media-status').textContent, /Cancellation failed: cancel offline/);
  assert.equal(app.control('media-log').textContent, 'one\ntwo');
});

test('same-cursor terminal cancellation discards a late running response', async () => {
  const app = studio();
  app.state().start(job('cancel', 1, ['one'], true));
  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = app.state().poll();
  app.state().accept({ ...job('cancel', 1, []), status: 'cancelled' });
  respond(Response.json(job('cancel', 1, [])));
  await pending;
  assert.equal(app.control('media-status').textContent, 'cancelled');
  assert.equal(app.state().active, false);
});

test('a job detached by Stop tracking stays cancellable and resumes tracking from the cancel snapshot', async () => {
  const app = studio();
  app.state().start(job('detached', 1, ['one'], true));
  app.context.fetch = async () => Response.json({ detail: 'invalid cursor' }, { status: 422 });
  await app.state().poll();
  app.listeners['media-poll-stop:click']();
  assert.equal(app.state().active, false);
  assert.equal(app.control('media-cancel').disabled, false);
  assert.match(app.control('media-status').textContent, /can be cancelled/);
  app.context.fetch = async () => Response.json({ ...job('detached', 2, ['one', 'cancel requested'], true), status: 'cancelling' });
  await app.listeners['media-cancel:click']();
  assert.equal(app.state().active, true);
  assert.equal(app.control('media-log').textContent, 'one\ncancel requested');
  assert.equal(app.control('media-run').disabled, true);
});
