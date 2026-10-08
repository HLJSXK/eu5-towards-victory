// Run with: node --test tests/media_job_polling.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function studio() {
  const controls = {};
  const control = (id) => controls[id] ||= {
    textContent: '', disabled: false, hidden: false,
    addEventListener() {}, appendChild() {},
  };
  const context = vm.createContext({
    document: { getElementById: control },
    window: { setTimeout: () => 1, clearTimeout() {} },
    fetch: () => new Promise(() => {}),
  });
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/api.js'), 'utf8').replace(/^export /gm, ''), context);
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/media_studio.js'), 'utf8').replace(/^import .*;\r?\n/gm, ''), context);
  return { context, control, state: () => vm.runInContext('state', context) };
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
  app.state().jobId = 'interrupted';
  app.context.interrupted = { ...job('interrupted', 1, [], true), status: 'failed',
    operation: { interrupted: true }, outputs_may_be_partial: true };
  vm.runInContext('renderJob(interrupted)', app.context);
  const message = app.control('media-status').textContent;
  assert.match(message, /may be partially published/);
  assert.match(message, /retained backups/);
  assert.doesNotMatch(message, /preserved/);
});

test('a job interrupted before it started does not warn about partial publication', () => {
  const app = studio();
  app.state().jobId = 'queued';
  app.context.queued = { ...job('queued', 1, [], true), status: 'failed',
    operation: { interrupted: true }, outputs_may_be_partial: false };
  vm.runInContext('renderJob(queued)', app.context);
  assert.equal(app.control('media-status').textContent, 'failed');
});

test('discarded intermediate files are separate from formal output conflicts', () => {
  const app = studio();
  app.state().jobId = 'generated';
  app.context.completed = { ...job('generated', 1, [], true), status: 'succeeded',
    staging_extra_files: ['staging/intermediate.bin'] };
  vm.runInContext('renderJob(completed)', app.context);
  assert.equal(app.control('media-status').textContent, 'succeeded');
  assert.match(app.control('media-file-report').textContent, /Intermediate files excluded from publication/);
  assert.doesNotMatch(app.control('media-file-report').textContent, /Undeclared|review required/);

  app.state().jobId = 'conflict';
  app.context.conflict = { ...job('conflict', 2, [], true), status: 'failed',
    formal_output_changes: ['output.json'], outputs_may_be_partial: true };
  vm.runInContext('renderJob(conflict)', app.context);
  assert.match(app.control('media-status').textContent, /formal outputs require review/);
  assert.match(app.control('media-file-report').textContent, /Formal outputs changed outside staging/);
});

test('a late poll after cancellation cannot append duplicate lines', async () => {
  const app = studio();
  const state = app.state();
  state.jobId = 'first';
  app.context.initial = job('first', 1, ['one'], true);
  vm.runInContext('renderJob(initial)', app.context);

  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = vm.runInContext('pollJob()', app.context);
  app.context.cancelled = job('first', 3, ['one', 'two', 'three'], true);
  vm.runInContext('renderJob(cancelled)', app.context);
  respond(Response.json(job('first', 2, ['two'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'one\ntwo\nthree');
  assert.equal(state.lineCursor, 3);
});

test('a late response from an earlier job cannot change the current job', async () => {
  const app = studio();
  const state = app.state();
  state.jobId = 'first';
  app.context.first = job('first', 1, ['old'], true);
  vm.runInContext('renderJob(first)', app.context);

  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  const pending = vm.runInContext('pollJob()', app.context);
  state.jobId = 'second';
  state.lineCursor = 0;
  app.context.second = job('second', 2, ['new one', 'new two'], true);
  vm.runInContext('renderJob(second)', app.context);
  respond(Response.json(job('first', 3, ['old two', 'old three'])));
  await pending;

  assert.equal(app.control('media-log').textContent, 'new one\nnew two');
  assert.equal(state.lineCursor, 2);
  assert.equal(state.jobId, 'second');
});
