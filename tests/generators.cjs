// WP-09: generator panel grouping, selection/disabled state, and the field mapping into the shared
// report renderers. Native ES modules with a minimal fake DOM; the real page is covered by
// generators_browser.cjs (mounted from resource_state_browser.cjs).
const assert = require('node:assert/strict');
const { test } = require('node:test');

class Element {
  constructor() {
    this.textContent = ''; this.innerHTML = ''; this.dataset = {}; this.hidden = false; this.disabled = false;
    this.checked = false; this.indeterminate = false; this.className = ''; this.type = ''; this.children = [];
    this.listeners = new Map(); this.selectors = new Map();
  }
  appendChild(child) { this.children.push(child); return child; }
  addEventListener(type, fn) {
    if (!this.listeners.has(type)) this.listeners.set(type, new Set());
    this.listeners.get(type).add(fn);
  }
  removeEventListener(type, fn) { this.listeners.get(type)?.delete(fn); }
  emit(type, event = {}) { return Promise.all([...this.listeners.get(type) || []].map(fn => fn(event))); }
  querySelector(selector) {
    if (!this.selectors.has(selector)) this.selectors.set(selector, new Element());
    return this.selectors.get(selector);
  }
}

// The module's page entry reads `document.getElementById('generators-root')` and registers a
// `tool-activated` listener at import time. Dynamic import is cached per process, so this one document
// is installed once for the whole file and never replaced — the page instance always belongs to it.
const controls = new Map();
const pageListeners = new Map();
const control = (id) => {
  if (!controls.has(id)) controls.set(id, new Element());
  return controls.get(id);
};
global.document = {
  getElementById: control,
  createElement: () => new Element(),
  addEventListener(type, fn) {
    if (!pageListeners.has(type)) pageListeners.set(type, new Set());
    pageListeners.get(type).add(fn);
  },
  removeEventListener(type, fn) { pageListeners.get(type)?.delete(fn); },
};
global.window = Object.assign(new EventTarget(), { confirm: () => true });
const activateTool = (tool) => Promise.all([...pageListeners.get('tool-activated') || []]
  .map(fn => fn({ detail: { tool } })));

const CATALOG = { generators: [
  { script: 'scripts/gen_index.py', root: 'src', domain: 'index', data_inputs: [], outputs: ['data/index/icons.txt', 'data/index/icons_extra.txt'] },
  { script: 'scripts/gen_victory.py', root: 'src', domain: 'victory', data_inputs: ['data/victory_paths.yaml'], outputs: ['src/a.txt'] },
  { script: 'scripts/gen_victory_events.py', root: 'src', domain: 'victory', data_inputs: ['data/victory_paths.yaml'], outputs: ['src/b.txt'] },
  { script: 'scripts_engineering_department/gen_ed.py', root: 'src_engineering_department', domain: 'ed', data_inputs: ['data/wonder.yaml'], outputs: ['src_engineering_department/c.txt'] },
] };

// The page entry goes through the real api.js fetch; this stub answers it so the lazy-load test can
// drive that entry without touching the network.
const pageRequests = [];
globalThis.fetch = async (url) => {
  pageRequests.push(String(url));
  return Response.json(CATALOG);
};

const OK = {
  operation_id: 'gen-op-1',
  operation: { id: 'gen-op-1', operation_id: 'gen-op-1', kind: 'generator_run', status: 'succeeded',
    resource_ids: ['editor.localization'], events: [], error: null },
  results: [
    { script: 'scripts/gen_index.py', status: 'succeeded', exit_code: 0, duration_ms: 8123, output_tail: 'wrote 7 files\n' },
    { script: 'scripts/gen_victory.py', status: 'succeeded', exit_code: 0, duration_ms: 250, output_tail: '' },
  ],
  artifacts: [
    { path: 'data/index/icons.txt', size: 120, sha256: 'ab'.repeat(32), changed: true },
    { path: 'data/index/icons_extra.txt', size: 40, sha256: 'cd'.repeat(32), changed: false },
    { path: 'src/a.txt', size: 12, sha256: 'ef'.repeat(32), changed: false },
  ],
  rollback: { status: 'not_needed', errors: [] },
};

async function fixture({ response = OK, gate = null, runError = null } = {}) {
  const { createGeneratorsPanel } = await import('../towards_victory_editor_web/static/generators.js');
  const root = new Element();
  const calls = [];
  const panel = createGeneratorsPanel(root, {
    load: async () => { calls.push({ url: '/api/generators' }); return CATALOG; },
    run: async (body) => {
      calls.push({ url: '/api/generators/run', body });
      if (gate) await gate.promise;
      if (runError) throw runError;
      return response;
    },
  });
  const groups = root.querySelector('.generators-groups');
  const sections = () => groups.children;
  const part = (selector) => root.querySelector(selector);
  const row = (group, index) => sections()[group].children[1].children[index];
  const scriptText = (group, index) => row(group, index).children[0].children[1].textContent;
  const checkbox = (group, index) => row(group, index).children[0].children[0];
  const groupToggle = (index) => sections()[index].children[0].children[0];
  const groupTitle = (index) => sections()[index].children[0].children[1].textContent;
  const groupCount = (index) => sections()[index].children[0].children[2].textContent;
  const runButton = () => part('[data-run]');
  const reloadButton = () => part('[data-reload]');
  const dryRun = () => part('[data-dry-run]');
  const plan = () => part('[data-plan]');
  // createLogView.report wraps the shared report text in newlines, so the raw log starts with one.
  const log = () => control('gen-log').textContent;
  const status = () => control('gen-status');
  const pick = async (group, index) => {
    const box = checkbox(group, index);
    box.checked = true;
    await box.emit('change');
  };
  return { root, panel, calls, sections, part, row, scriptText, checkbox, groupToggle, groupTitle, groupCount,
    runButton, reloadButton, dryRun, plan, log, status, pick };
}

test('catalogue renders one section per root/domain in catalogue order, with counts and rows', async () => {
  const f = await fixture();
  await f.panel.reload();
  assert.deepEqual(f.sections().map((_, index) => f.groupTitle(index)),
    ['src / index', 'src / victory', 'src_engineering_department / ed']);
  assert.equal(f.sections().length, 3, 'three groups');
  assert.equal(f.scriptText(0, 0), 'scripts/gen_index.py');
  assert.equal(f.scriptText(1, 1), 'scripts/gen_victory_events.py');
  assert.equal(f.sections()[1].children[1].children.length, 2, 'victory group holds both scripts');
  assert.equal(f.groupCount(0), '1 个脚本');
  assert.equal(f.groupCount(1), '2 个脚本');
  assert.equal(f.row(0, 0).children[1].textContent, '2 个产物');
  // Inputs and outputs come straight from the contract fields, not from a local re-derivation.
  const details = f.row(1, 0).children[2].children[1].textContent;
  assert.match(details, /输入：\n {2}data\/victory_paths\.yaml/);
  assert.match(details, /产物：\n {2}src\/a\.txt/);
  // The "sequential, no dependency graph" statement is always visible.
  assert.match(f.plan().textContent, /没有依赖图/);
  assert.equal(f.root.dataset.busy, 'false');
});

test('run stays disabled until a script is selected; group toggle and order follow the click order', async () => {
  const f = await fixture();
  await f.panel.reload();
  assert.equal(f.runButton().disabled, true, 'nothing selected');
  assert.match(f.plan().textContent, /尚未选择脚本/);

  await f.pick(1, 0);
  assert.equal(f.runButton().disabled, false);
  assert.equal(f.groupToggle(1).indeterminate, true, 'partial group selection');
  assert.equal(f.groupToggle(1).checked, false);

  // A second selection from another group appends: order is the user's click order, not catalogue order.
  await f.pick(0, 0);
  assert.equal(f.plan().textContent,
    '执行顺序：1. scripts/gen_victory.py → 2. scripts/gen_index.py');

  // The group toggle selects every script of that group and clears the indeterminate state. Scripts
  // already picked keep their earlier position; the new ones append, so the order stays the click order.
  f.groupToggle(1).checked = true;
  await f.groupToggle(1).emit('change');
  assert.equal(f.groupToggle(1).checked, true);
  assert.equal(f.groupToggle(1).indeterminate, false);
  assert.equal(f.plan().textContent,
    '执行顺序：1. scripts/gen_victory.py → 2. scripts/gen_index.py → 3. scripts/gen_victory_events.py');

  // Deselecting everything disables the run button again.
  f.groupToggle(1).checked = false;
  await f.groupToggle(1).emit('change');
  const box = f.checkbox(0, 0);
  box.checked = false;
  await box.emit('change');
  assert.equal(f.runButton().disabled, true);
  assert.equal(f.groupToggle(1).indeterminate, false);
  assert.match(f.plan().textContent, /尚未选择脚本/);
});

test('a run sends the selected scripts in order and renders steps and artifacts through the shared renderer', async () => {
  const f = await fixture();
  await f.panel.reload();
  await f.pick(0, 0);
  await f.pick(1, 0);
  await f.panel.run();

  assert.deepEqual(f.calls.at(-1),
    { url: '/api/generators/run', body: { scripts: ['scripts/gen_index.py', 'scripts/gen_victory.py'], dry_run: false } });
  // Every line comes from formatOperationReport; the panel only mapped exit_code/duration_ms and role.
  assert.equal(f.log(),
    '\n操作 ID: gen-op-1\n操作状态: 已完成\n生成结果: 已完成\n'
    + '  scripts/gen_index.py: 已完成 (退出码 0) / 8.123s\n'
    + '  scripts/gen_victory.py: 已完成 (退出码 0) / 0.25s\n'
    + '  data/index/icons.txt: 已变化\n'
    + '  data/index/icons_extra.txt: 未变化\n'
    + '  src/a.txt: 未变化\n'
    + '恢复结果: 无需恢复\n'
    + '\n[scripts/gen_index.py]\nwrote 7 files\n');
  assert.equal(f.status().textContent, '2 个脚本；已完成；1/3 个产物有变化');
  assert.equal(control('gen-files').hidden, false);
  assert.equal(control('gen-file-report').textContent,
    '资源: editor.localization\n输出:\n'
    + '  data/index/icons.txt（已变化）\n'
    + '  data/index/icons_extra.txt（未变化）\n'
    + '  src/a.txt（未变化）');
  assert.equal(f.runButton().disabled, false, 'selection is kept after a run');
});

test('dry_run reports skipped steps, no artifacts and says nothing was executed or written', async () => {
  const f = await fixture({ response: {
    ...OK,
    results: OK.results.map((result) => ({ ...result, status: 'skipped', exit_code: null, duration_ms: 0, output_tail: '' })),
    artifacts: [],
  } });
  await f.panel.reload();
  await f.pick(0, 0);
  f.dryRun().checked = true;
  await f.panel.run();
  assert.equal(f.calls.at(-1).body.dry_run, true);
  assert.equal(f.log(),
    '\n操作 ID: gen-op-1\n操作状态: 已完成\n生成结果: 已完成\n'
    + '  scripts/gen_index.py: 已跳过 / 0s\n'
    + '  scripts/gen_victory.py: 已跳过 / 0s\n'
    + '恢复结果: 无需恢复\n');
  assert.match(f.status().textContent, /dry_run：未执行脚本、未写入文件/);
  // A dry run declares no outputs, so the file report lists only the resource lock.
  assert.equal(control('gen-files').hidden, false);
  assert.equal(control('gen-file-report').textContent, '资源: editor.localization');
});

test('a timed-out step renders through the shared report instead of a raw identifier', async () => {
  const f = await fixture({ response: {
    ...OK,
    operation: { ...OK.operation, status: 'failed' },
    results: [
      { script: 'scripts/gen_index.py', status: 'succeeded', exit_code: 0, duration_ms: 120, output_tail: '' },
      { script: 'scripts/gen_victory.py', status: 'timed_out', exit_code: null, duration_ms: 120000, output_tail: 'partial\n' },
    ],
    artifacts: [],
    rollback: { status: 'completed', errors: [] },
  } });
  await f.panel.reload();
  await f.pick(1, 0);
  await f.panel.run();
  // No exit code and a 120 s duration: the shared renderer prints the status label plus the duration.
  assert.match(f.log(), /scripts\/gen_victory\.py: 已超时 \/ 120s\n/);
  assert.match(f.log(), /恢复结果: 已恢复\n/);
  assert.match(f.status().textContent, /失败/);
});

test('a failed run reports the server detail as an error and releases the panel', async () => {
  const f = await fixture({ runError: new Error('scripts/gen_victory.py exited with 1') });
  await f.panel.reload();
  await f.pick(1, 0);
  await f.panel.run();
  assert.equal(f.status().dataset.kind, 'error');
  assert.match(f.status().textContent, /exited with 1/);
  assert.match(f.log(), /\[error\] scripts\/gen_victory\.py exited with 1/);
  assert.equal(f.root.dataset.running, 'false', 'the panel is not stuck in the running state');
  assert.equal(f.runButton().disabled, false);
  assert.equal(f.checkbox(1, 0).disabled, false, 'checkboxes are usable again');
});

test('rows and actions are locked while a run is in flight', async () => {
  let release;
  const promise = new Promise((resolve) => { release = resolve; });
  const f = await fixture({ gate: { promise } });
  await f.panel.reload();
  await f.pick(0, 0);
  const pending = f.panel.run();
  assert.equal(f.root.dataset.running, 'true');
  assert.equal(f.runButton().disabled, true);
  assert.equal(f.reloadButton().disabled, true);
  assert.equal(f.dryRun().disabled, true);
  assert.equal(f.checkbox(0, 0).disabled, true);
  assert.match(f.plan().textContent, /正在按顺序执行 1 个脚本/);
  release();
  await pending;
  assert.equal(f.root.dataset.running, 'false');
  assert.equal(f.checkbox(0, 0).disabled, false);
  assert.equal(f.reloadButton().disabled, false);
});

test('the page entry loads the catalogue once, only when the generators tab is activated', async () => {
  const root = control('generators-root');
  assert.equal(pageRequests.length, 0, 'nothing is requested before the tab is opened');
  assert.equal(root.dataset.busy, 'false');
  await activateTool('victory-tree');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(pageRequests.length, 0, 'another tab does not load the catalogue');
  await activateTool('generators');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(pageRequests, ['/api/generators']);
  assert.match(control('gen-status').textContent, /已加载 4 个已登记生成器/);
  await activateTool('generators');
  await activateTool('cost-reward');
  await activateTool('generators');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(pageRequests.length, 1, 'the second activation reuses the loaded catalogue');
});
