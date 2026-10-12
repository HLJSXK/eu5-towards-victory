// WP-10: global shell. Covers the dirty-indicator registry, the dedupe on repeated transitions,
// the operations list's three states, and the `tool-activated` event that WP-01 shipped without
// its own test (see docs/technical/Editor_Web_Refactor_TODO.md).
//
// Native ES modules with a minimal fake DOM, following tests/resource_state.cjs and
// tests/validation_panel.cjs. Real page wiring is covered by the Chrome scenario in
// resource_state_browser.cjs.
const assert = require('node:assert/strict');
const { test, before, after } = require('node:test');

function classList(owner) {
  return {
    toggle(name, force) {
      const on = force === undefined ? !owner.classes.has(name) : !!force;
      if (on) owner.classes.add(name); else owner.classes.delete(name);
      return on;
    },
    add(name) { owner.classes.add(name); },
    remove(name) { owner.classes.delete(name); },
    contains(name) { return owner.classes.has(name); },
  };
}

function element(extra = {}) {
  const node = {
    textContent: '', innerHTML: '', dataset: {}, hidden: false, disabled: false, title: '',
    classes: new Set(), children: [], listeners: new Map(), selectors: new Map(), attributes: new Map(),
    appendChild(child) { node.children.push(child); },
    addEventListener(type, fn) { if (!node.listeners.has(type)) node.listeners.set(type, new Set()); node.listeners.get(type).add(fn); },
    removeEventListener(type, fn) { node.listeners.get(type)?.delete(fn); },
    emits(type) { return [...node.listeners.get(type) || []]; },
    async emit(type, event = {}) { return Promise.all(node.emits(type).map(fn => fn(event))); },
    querySelector(selector) {
      if (!node.selectors.has(selector)) node.selectors.set(selector, element());
      return node.selectors.get(selector);
    },
    closest() { return node; },
    contains() { return true; },
    setAttribute(name, value) { node.attributes.set(name, value); },
    getAttribute(name) { return node.attributes.get(name) ?? null; },
  };
  node.classList = classList(node);
  return Object.assign(node, extra);
}

// The tabs are real objects here so the dot test can read the same node shared.js painted.
const tools = ['cost-reward', 'victory-tree', 'wonder-localization', 'wonder-cropper'];
const tabs = tools.map((tool) => {
  const button = element({ dataset: { tool } });
  button.selectors.set('.tool-hub-tab-dot', element({ hidden: true }));
  return button;
});
const panels = tools.map((tool) => element({ dataset: { tool } }));
const activated = [];
const confirmations = [];

global.document = {
  body: element(),
  // null for the operations host: its page entry would otherwise poll a real endpoint forever.
  getElementById: (id) => (id === 'operations-panel' ? null : element()),
  createElement: () => element(),
  querySelectorAll: (selector) => (selector === '.tool-hub-tab-btn' ? tabs : selector === '.tool-panel' ? panels : []),
  addEventListener() {},
  dispatchEvent(event) {
    if (event.type === 'tool-activated') activated.push(event.detail);
    return true;
  },
};
global.window = Object.assign(new EventTarget(), {
  confirm: (message) => { confirmations.push(message); return true; },
});

let shellModule, stateModule, operationsModule;

before(async () => {
  // shared.js runs its tab wiring on import, so the fake DOM must exist first.
  [shellModule, stateModule, operationsModule] = await Promise.all([
    import('../towards_victory_editor_web/static/shared.js'),
    import('../towards_victory_editor_web/static/resource_state.js'),
    import('../towards_victory_editor_web/static/operations_panel.js'),
  ]);
});

after(() => {
  stateModule.resetToolIndicators();
});

test('importing the shell activates the first tab and dispatches tool-activated once', async () => {
  const { activateTool } = shellModule;
  assert.equal(global.document.body.dataset.activeTool, 'cost-reward');
  assert.equal(tabs[0].classList.contains('active'), true);
  assert.equal(tabs[1].classList.contains('active'), false);
  assert.deepEqual(activated, [{ tool: 'cost-reward' }]);

  // WP-01 relied on this event to size the cropper canvas; the detail must name the clicked tool.
  await tabs[2].emit('click');
  assert.deepEqual(activated.at(-1), { tool: 'wonder-localization' });
  assert.equal(global.document.body.dataset.activeTool, 'wonder-localization');
  assert.equal(tabs[2].dataset.tool, 'wonder-localization');
  assert.deepEqual(panels.map((panel) => panel.classList.contains('active')), [false, false, true, false]);
  activateTool('cost-reward');
});

test('the dirty registry adds and removes entries and only notifies on a real change', async (t) => {
  const { setToolDirty, setToolJobs, toolIndicator, dirtyToolNames, subscribeToolIndicators } = stateModule;
  t.after(() => stateModule.resetToolIndicators());
  const seen = [];
  const unsubscribe = subscribeToolIndicators((tool, indicator) => seen.push([tool, indicator.dirty, indicator.jobs]));

  assert.deepEqual(dirtyToolNames(), []);
  assert.equal(setToolDirty('cost-reward', true), true);
  assert.equal(setToolDirty('cost-reward', true), false); // repeated event: no second notification
  assert.equal(setToolDirty('cost-reward', true), false);
  assert.deepEqual(dirtyToolNames(), ['cost-reward']);
  assert.deepEqual(seen, [['cost-reward', true, 0]]);

  // An entry survives while either fact holds, and is dropped once both are false.
  assert.equal(setToolJobs('cost-reward', 2), true);
  assert.equal(setToolDirty('cost-reward', false), true);
  assert.deepEqual(dirtyToolNames(), []);
  assert.equal(toolIndicator('cost-reward').jobs, 2);
  assert.equal(setToolJobs('cost-reward', 0), true);
  assert.deepEqual(seen, [['cost-reward', true, 0], ['cost-reward', true, 2], ['cost-reward', false, 2], ['cost-reward', false, 0]]);

  // An unknown tool reads as clean rather than throwing, so painting never breaks.
  assert.deepEqual(toolIndicator('generators'), { dirty: false, jobs: 0 });
  assert.equal(setToolJobs('cost-reward', 0), false); // removing an absent entry is a no-op
  unsubscribe();
  assert.equal(setToolDirty('victory-tree', true), true);
  assert.equal(seen.length, 4, 'an unsubscribed listener hears nothing more');
});

test('a dirty tool paints its tab dot and an active job shows the running marker', async (t) => {
  const { setToolDirty, setToolJobs, resetToolIndicators } = stateModule;
  t.after(() => resetToolIndicators());
  // A private window per shell: beforeunload listeners must not leak between tests.
  const shell = shellModule.createToolShell({ win: new EventTarget(), tabs });
  t.after(() => shell.destroy());

  setToolDirty('wonder-localization', true);
  const dot = tabs[2].querySelector('.tool-hub-tab-dot');
  assert.equal(dot.hidden, false);
  assert.equal(dot.classList.contains('dirty'), true);
  assert.match(dot.title, /有未保存的更改/);
  assert.equal(tabs[2].dataset.dirty, 'true');

  setToolJobs('wonder-localization', 1);
  assert.equal(dot.classList.contains('running'), true);
  assert.equal(dot.dataset.jobs, '1');
  assert.match(dot.title, /1 个作业在运行/);

  setToolDirty('wonder-localization', false);
  setToolJobs('wonder-localization', 0);
  assert.equal(dot.hidden, true);
  assert.equal(dot.classList.contains('dirty'), false);
  assert.equal(tabs[0].querySelector('.tool-hub-tab-dot').hidden, true, 'other tabs stay clean');
});

test('beforeunload is only blocked while some tool is dirty', async (t) => {
  const { setToolDirty, resetToolIndicators } = stateModule;
  t.after(() => resetToolIndicators());
  const win = new EventTarget();
  const shell = shellModule.createToolShell({ win, tabs });
  // Dispatch a real event through the window: this covers the registered listener, not just the body.
  // Node's Event.returnValue is a read-only getter, while browsers allow the legacy assignment the
  // handler makes, so the property is shadowed with a writable own value.
  const fire = () => {
    const event = new Event('beforeunload', { cancelable: true });
    Object.defineProperty(event, 'returnValue', { value: undefined, writable: true, configurable: true });
    win.dispatchEvent(event);
    return event;
  };

  const clean = fire();
  assert.equal(clean.defaultPrevented, false, 'a clean workspace leaves without a prompt');
  assert.equal(shell.leave(clean), undefined, 'and the handler itself declines');

  setToolDirty('victory-tree', true);
  const dirty = fire();
  assert.equal(dirty.defaultPrevented, true, 'leaving with unsaved changes must be confirmed');
  assert.equal(dirty.returnValue, '');
  assert.deepEqual(shell.dirtyTools(), ['victory-tree']);
  assert.deepEqual(shell.leave({ preventDefault() {}, returnValue: undefined }), ['victory-tree']);

  setToolDirty('victory-tree', false);
  assert.equal(fire().defaultPrevented, false, 'the prompt goes away once the draft is gone');
  shell.destroy();
  setToolDirty('victory-tree', true);
  assert.equal(fire().defaultPrevented, false, 'destroy() unregisters the listener');
});

test('ResourceState reports only real dirty transitions through onDirtyChange', async () => {
  const { ResourceState } = stateModule;
  const seen = [];
  const state = new ResourceState({ saved: { value: 1 }, onDirtyChange: (dirty) => seen.push(dirty) });
  // Construction must stay silent: editors pass onDirtyChange inline before their object literal exists.
  assert.deepEqual(seen, []);
  assert.equal(state.dirty, false);

  state.mutate((draft) => { draft.value = 2; });
  state.mutate((draft) => { draft.value = 3; });
  assert.deepEqual(seen, [true], 'a second edit while already dirty is not a new transition');
  assert.equal(state.dirty, true);

  state.setDraft({ value: 1 });
  assert.deepEqual(seen, [true, false]);
  state.setDraft({ value: 1 });
  assert.deepEqual(seen, [true, false], 'restoring the saved value twice reports one transition');

  // replace() (and therefore reset()) reports too, which is how a reload clears the tab dot.
  state.mutate((draft) => { draft.value = 9; });
  state.replace({ saved: { value: 4 } });
  assert.deepEqual(seen, [true, false, true, false]);
});

test('operation groups split running, failed and finished without repeating a row', async () => {
  const { operationGroups, runningCounts, toolForOperation, operationSummary } = operationsModule;
  const operations = [
    { id: 'a', kind: 'resource_commit', status: 'running', resource_ids: ['editor.cost_reward'], created_at: 1 },
    { id: 'b', kind: 'generator_run', status: 'queued', resource_ids: [], created_at: 2 },
    { id: 'c', kind: 'resource_commit', status: 'failed', resource_ids: ['editor.wonder'], error: 'boom', created_at: 3 },
    { id: 'd', kind: 'media_job', status: 'succeeded', resource_ids: ['media.historical'], created_at: 4 },
    { id: 'e', kind: 'commit', status: 'cancelled', resource_ids: ['editor.localization'], created_at: 5 },
  ];
  const groups = operationGroups(operations);
  assert.deepEqual(groups.running.map((operation) => operation.id), ['a', 'b']);
  assert.deepEqual(groups.failed.map((operation) => operation.id), ['c']);
  assert.deepEqual(groups.recent.map((operation) => operation.id), ['d', 'e']);
  assert.equal(new Set([...groups.running, ...groups.failed, ...groups.recent]).size, operations.length);

  assert.equal(toolForOperation(operations[0]), 'cost-reward');
  assert.equal(toolForOperation(operations[1]), 'generators');
  assert.equal(toolForOperation(operations[3]), 'media-studio');
  assert.equal(toolForOperation({ kind: 'resource_commit', resource_ids: ['something.else'] }), null);
  assert.deepEqual([...runningCounts(operations)], [['cost-reward', 1], ['generators', 1]]);
  assert.match(operationSummary(operations[0]), /运行中 · 资源保存/);
  assert.match(operationSummary({ id: 'x', status: 'failed', kind: 'commit', created_at: 5, started_at: 5, finished_at: 7.5 }), /失败 · 保存 · .* · 2\.5 秒/);
});

test('the operations list renders loaded, empty and failed states and escapes payloads', async (t) => {
  const { createOperationsPanel } = operationsModule;
  const timers = [];
  const root = element();
  const state = { operations: [], fail: null };
  const panel = createOperationsPanel(root, {
    fetch: async (url) => {
      if (state.fail) throw new Error(state.fail);
      assert.match(url, /^api\/operations\?limit=25$/);
      return { operations: state.operations };
    },
    schedule: (callback) => { timers.push(callback); return timers.length; },
    cancel: () => {},
  });
  const results = root.querySelector('.operations-results');

  // Loaded: three sections, running first, and the report escapes the payload.
  const xss = '<img src=x onerror="window.__xss=true">';
  state.operations = [
    { id: 'run-1', kind: 'resource_commit', status: 'running', resource_ids: ['editor.victory_tree'], created_at: 1 },
    { id: 'fail-1', kind: 'resource_commit', status: 'failed', resource_ids: ['editor.wonder'], error: xss, created_at: 2 },
    { id: 'done-1', kind: 'media_job', status: 'succeeded', resource_ids: ['media.historical'], created_at: 3 },
  ];
  await panel.refresh();
  assert.equal(root.dataset.state, 'loaded');
  assert.match(root.querySelector('.operations-status-bar').textContent, /共 3 项：在跑 1，失败 1，最近 1/);
  assert.match(results.innerHTML, /在跑作业[\s\S]*失败项[\s\S]*最近操作/);
  assert.equal(results.innerHTML.includes(xss), false, 'the payload is escaped, not injected');
  assert.match(results.innerHTML, /&lt;img src=x/);
  assert.match(results.innerHTML, /data-operation-id="run-1"/);
  assert.equal(stateModule.toolIndicator('victory-tree').jobs, 1);
  assert.equal(stateModule.toolIndicator('media-studio').jobs, 0);

  // Empty: every section says so instead of rendering a bare heading.
  state.operations = [];
  await panel.refresh();
  assert.equal(root.dataset.state, 'empty');
  assert.match(results.innerHTML, /没有正在运行的作业。[\s\S]*没有失败的操作。[\s\S]*暂无已完成的操作。/);
  assert.equal(stateModule.toolIndicator('victory-tree').jobs, 0, 'a finished job clears the tab marker');

  // Failed: the query error is surfaced and the markers are cleared rather than left stale.
  stateModule.setToolJobs('cost-reward', 1);
  state.fail = 'operations probe failure';
  await panel.refresh();
  assert.equal(root.dataset.state, 'failed');
  assert.match(root.querySelector('.operations-status-bar').textContent, /操作列表查询失败: operations probe failure/);
  assert.equal(stateModule.toolIndicator('cost-reward').jobs, 0);
  assert.equal(root.querySelector('[data-operations-refresh]').disabled, false);

  // Polling schedules itself and stops on request.
  state.fail = null;
  panel.poll();
  assert.equal(timers.length, 1);
  stateModule.resetToolIndicators();
});
