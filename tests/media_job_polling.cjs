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
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/media_studio.js'), 'utf8'), context);
  return { context, control, state: () => vm.runInContext('state', context) };
}

function job(id, cursor, lines, reset = false) {
  return {
    id, line_cursor: cursor, lines, lines_reset: reset, status: 'running',
    outputs_may_be_partial: false, resource_ids: [], source_snapshots: [],
    artifacts: [], metadata: {}, declared_outputs: [], missing_outputs: [],
  };
}

test('a late poll after cancellation cannot append duplicate lines', async () => {
  const app = studio();
  const state = app.state();
  state.jobId = 'first';
  app.context.initial = job('first', 1, ['one'], true);
  vm.runInContext('renderJob(initial)', app.context);

  let respond;
  app.context.testFetch = () => new Promise((resolve) => { respond = resolve; });
  vm.runInContext('jsonFetch = testFetch', app.context);
  const pending = vm.runInContext('pollJob()', app.context);
  app.context.cancelled = job('first', 3, ['one', 'two', 'three'], true);
  vm.runInContext('renderJob(cancelled)', app.context);
  respond(job('first', 2, ['two']));
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
  app.context.testFetch = () => new Promise((resolve) => { respond = resolve; });
  vm.runInContext('jsonFetch = testFetch', app.context);
  const pending = vm.runInContext('pollJob()', app.context);
  state.jobId = 'second';
  state.lineCursor = 0;
  app.context.second = job('second', 2, ['new one', 'new two'], true);
  vm.runInContext('renderJob(second)', app.context);
  respond(job('first', 3, ['old two', 'old three']));
  await pending;

  assert.equal(app.control('media-log').textContent, 'new one\nnew two');
  assert.equal(state.lineCursor, 2);
  assert.equal(state.jobId, 'second');
});
