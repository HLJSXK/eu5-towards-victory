// Native modules: exercise the Wonder adapter and shared preview/save controller together.
const assert = require('node:assert/strict');
const { test } = require('node:test');

class Element {
  constructor() { this.dataset = {}; this.children = []; this.selectors = new Map(); this.listeners = new Map(); this.textContent = ''; }
  querySelector(key) { if (!this.selectors.has(key)) this.selectors.set(key, new Element()); return this.selectors.get(key); }
  appendChild(child) { this.children.push(child); }
  addEventListener(key, fn) { if (!this.listeners.has(key)) this.listeners.set(key, new Set()); this.listeners.get(key).add(fn); }
  removeEventListener(key, fn) { this.listeners.get(key)?.delete(fn); }
  async emit(key, event = {}) { await Promise.all([...this.listeners.get(key) || []].map(fn => fn(event))); }
  showModal() { this.open = true; }
  close() { this.open = false; }
}

async function until(check) {
  for (let i = 0; i < 50; i++) { if (check()) return; await new Promise(setImmediate); }
  assert.fail('Expected UI state');
}

const resourcePayload = {
  change_set: { base: [{ path: 'source', sha256: 'new' }] },
  draft: { title: 'Wonder', wonders: [{ id: 1 }, { id: 2 }], initial_wonder_id: 1, log_text: '' },
};
const detail = { summary: { id: 1 }, languages: {}, mechanics: {}, status: 'Loaded' };
const committed = { ...resourcePayload, wonder: detail, wonders: resourcePayload.draft.wonders,
  operation_id: 'saved-1', operation: { status: 'succeeded' }, log_text: 'server log' };
const preview = { diff: [{ kind: 'field', path: 'data/source.yaml', wonder_id: 2, wonder_key: 'test',
  language: 'english', field: 'title', value_kind: 'text', before: 'old', after: 'old draft' }] };

async function fixture(t) {
  const { createWonderEditor } = await import('../towards_victory_editor_web/static/wonder_editor.js');
  const { ResourceState } = await import('../towards_victory_editor_web/static/resource_state.js');
  const previous = { document: global.document, window: global.window, fetch: global.fetch };
  const root = new Element(), elements = Object.fromEntries(['logOutput', 'copyLogButton', 'saveButton', 'reloadButton', 'retryDetailButton'].map(k => [k, new Element()]));
  const prompts = [], calls = [];
  global.document = { getElementById: () => root, createElement: () => new Element() };
  global.window = Object.assign(new EventTarget(), { confirm: message => { prompts.push(message); return true; } });
  t.after(() => Object.assign(global, previous));
  const state = {
    currentWonder: detail,
    resource: new ResourceState({ base: { source: 'old' }, saved: { wonders: [], pageDrafts: {} },
      draft: { wonders: [], pageDrafts: { 2: { values: { english: { title: 'old draft' } }, mechanics: {} } } } }),
    get pageDrafts() { return this.resource.draft.pageDrafts; },
    get busy() { return this.resource.busy; },
  };
  const hooks = { hydrate: async payload => payload, render() {} };
  const editor = createWonderEditor({ state, elements,
    dirtyCount: () => Object.keys(state.pageDrafts).length,
    draftHasChanges: draft => Object.keys(draft.values.english).length > 0,
    currentId: () => state.currentWonder?.summary.id ?? null,
    setCurrent: payload => { state.currentWonder = payload; }, hydrate: payload => hooks.hydrate(payload),
    invalidateDesigns() {}, syncSelection() {}, render() { hooks.render(); editor.renderLog(); },
    updateStatus(text, kind = 'default') { state.status = text; state.statusKind = kind; }, showToast() {},
  });
  function respond(fn) { global.fetch = async (url, options = {}) => { calls.push({ url, ...options }); const result = await fn(url, options); return result instanceof Response ? result : Response.json(result); }; }
  respond(url => url.endsWith('/preview') ? preview : url.endsWith('/commit') ? committed : url === 'api/resources/editor.wonder' ? resourcePayload : detail);
  return { editor, state, elements, prompts, calls, hooks, respond, dialog: root.querySelector('dialog') };
}

test('reload confirms all page drafts and publishes resource and detail together', async t => {
  const app = await fixture(t);
  await app.editor.load({ confirmDirty: true });
  assert.equal(app.prompts.length, 1);
  assert.equal(app.state.resource.base.source, 'new');
  assert.deepEqual(app.state.pageDrafts, {});
  assert.equal(app.state.currentWonder.summary.id, 1);
});

test('cancelled reload keeps drafts/base without requests', async t => {
  const app = await fixture(t);
  global.window.confirm = () => false;
  await app.editor.load({ confirmDirty: true });
  assert.equal(app.calls.length, 0);
  assert.equal(app.state.resource.base.source, 'old');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
});

test('initial detail failure leaves the summary loaded and retry can select the first wonder', async t => {
  const app = await fixture(t);
  app.state.currentWonder = null;
  app.respond(url => {
    if (url !== 'api/resources/editor.wonder') throw new Error('initial detail failed');
    return resourcePayload;
  });
  await app.editor.load({ context: { initial: true } });
  assert.deepEqual(app.state.resource.draft.wonders, resourcePayload.draft.wonders);
  assert.equal(app.state.currentWonder, null);
  assert.equal(app.state.resource.base.source, 'new');
  app.respond(() => detail);
  await app.editor.select(1);
  assert.equal(app.state.currentWonder.summary.id, 1);
});

for (const failure of ['resource', 'detail', 'catalog']) test('failed ' + failure + ' reload retains all drafts/base/detail', async t => {
  const app = await fixture(t), before = app.state.currentWonder;
  app.respond(url => {
    if (failure === 'resource' || failure === 'detail' && url !== 'api/resources/editor.wonder') throw new Error('load failed');
    return url === 'api/resources/editor.wonder' ? resourcePayload : detail;
  });
  if (failure === 'catalog') app.hooks.hydrate = async () => { throw new Error('catalog failed'); };
  await app.editor.load({ confirmDirty: true });
  assert.equal(app.state.resource.base.source, 'old');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
  assert.equal(app.state.currentWonder, before);
  assert.equal(app.state.busy, false);
  assert.match(app.editor.log.text, /failed/);
});

test('save uses the immediately tracked page drafts for preview and commit', async t => {
  const app = await fixture(t);
  const pending = app.editor.save(); await until(() => app.dialog.open);
  assert.equal(app.state.busy, true);
  assert.equal(app.state.resource.mutate(d => { d.pageDrafts = {}; }), false);
  await app.editor.save(); assert.equal(app.calls.length, 1);
  assert.equal(app.state.resource.base.source, 'old');
  await app.dialog.querySelector('[data-confirm]').emit('click'); await pending;
  assert.equal(app.calls[0].body, app.calls[1].body);
  assert.deepEqual(JSON.parse(app.calls[0].body), { regenerate: true, current_wonder_id: 1, base: { source: 'old' },
    wonders: [{ wonder_id: 2, values: { english: { title: 'old draft' } }, mechanics: {} }] });
  assert.equal(app.state.resource.base.source, 'new');
  assert.equal(app.state.resource.dirty, false);
  assert.match(app.editor.log.text, /saved-1/);
});

for (const action of ['cancel', 'escape']) test(action + ' from preview keeps all drafts and base', async t => {
  const app = await fixture(t);
  const pending = app.editor.save(); await until(() => app.dialog.open);
  if (action === 'cancel') await app.dialog.querySelector('[data-cancel]').emit('click');
  else await app.dialog.emit('cancel', { preventDefault() {} });
  await pending;
  assert.equal(app.calls.length, 1);
  assert.equal(app.state.resource.base.source, 'old');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
  assert.equal(app.state.busy, false);
});

for (const endpoint of ['preview', 'commit']) for (const status of [409, 500]) test(endpoint + ' ' + status + ' keeps drafts and diagnostics', async t => {
  const app = await fixture(t);
  app.respond(url => url.endsWith('/' + endpoint) ? Response.json({ detail: 'data/wonder.yaml failed', code: 'resource_changed',
    operation_id: 'failed-1', log_text: 'server log', generation: { status: 'failed', rollback: { status: 'succeeded', errors: [] } } }, { status }) : preview);
  const pending = app.editor.save();
  if (endpoint === 'commit') { await until(() => app.dialog.open); await app.dialog.querySelector('[data-confirm]').emit('click'); }
  await pending;
  assert.equal(app.state.resource.base.source, 'old');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
  assert.equal(app.state.statusKind, 'error');
  assert.match(app.state.status, /data\/wonder.yaml/);
  assert.match(app.editor.log.text, /server log[\s\S]*failed-1[\s\S]*恢复结果[\s\S]*data\/wonder.yaml/);
});

test('repeated failures replace the previous operation report', async t => {
  const app = await fixture(t); let attempt = 0;
  app.respond(() => Response.json({ detail: 'generator failed', operation_id: 'op-' + ++attempt }, { status: 500 }));
  await app.editor.save(); await app.editor.save();
  assert.match(app.editor.log.text, /op-2/); assert.doesNotMatch(app.editor.log.text, /op-1/);
});

test('committed base survives catalog failure; explicit retry only loads detail and preserves the operation report', async t => {
  const app = await fixture(t);
  app.hooks.hydrate = async () => { throw new Error('catalog failed'); };
  const pending = app.editor.save(); await until(() => app.dialog.open);
  await app.dialog.querySelector('[data-confirm]').emit('click'); await pending;
  assert.equal(app.state.resource.base.source, 'new'); assert.equal(app.state.resource.dirty, false);
  assert.equal(app.state.currentWonder, null);
  assert.equal(app.elements.retryDetailButton.hidden, false);
  assert.match(app.state.status, /已保存.*详情加载失败/);
  assert.match(app.editor.log.text, /saved-1[\s\S]*catalog failed/);
  app.hooks.hydrate = async payload => payload;
  await app.elements.retryDetailButton.emit('click');
  await until(() => !app.state.busy);
  assert.equal(app.state.currentWonder.summary.id, 1);
  assert.equal(app.elements.retryDetailButton.hidden, true);
  assert.equal(app.calls.filter(c => c.method === 'POST').length, 2);
  assert.match(app.editor.log.text, /saved-1/);
});

function notifyCommit(paths = ['source']) {
  window.dispatchEvent(new CustomEvent('resource-committed', { detail: { resourceId: 'editor.cost_reward', writtenPaths: paths } }));
}

function page(id, original = 'old') {
  return { summary: { id, key: 'w' + id }, meta: {},
    languages: { english: { sections: [{ fields: [{ key: 'title', original_value: original, value: original }] }] } }, mechanics: {} };
}

test('external commits rebase every drafted page and report hidden-page original conflicts', async t => {
  const app = await fixture(t);
  app.respond(url => page(Number(url.split('/').at(-1))));
  await app.editor.select(2); await app.editor.select(1);
  app.respond(url => url === 'api/resources/editor.wonder' ? resourcePayload : page(Number(url.split('/').at(-1)), 'external'));
  notifyCommit(['unrelated']); assert.equal(app.state.busy, false);
  notifyCommit(); await until(() => !app.state.busy);
  assert.equal(app.state.resource.base.source, 'new');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
  assert.deepEqual(app.state.resource.saved.pageDrafts, {});
  assert.equal(app.state.resource.dirty, true);
  assert.match(app.editor.log.text, /原值已在其他编辑器中改变：2.*title.*old.*external/);
  app.respond(url => url.endsWith('/preview') ? preview : committed);
  const pending = app.editor.save(); await until(() => app.dialog.open);
  const body = JSON.parse(app.calls.at(-1).body);
  assert.equal(body.base.source, 'new');
  assert.deepEqual(body.wonders, [{ wonder_id: 2, ...{ values: { english: { title: 'old draft' } }, mechanics: {} } }]);
  await app.dialog.querySelector('[data-confirm]').emit('click'); await pending;
  assert.equal(app.state.resource.dirty, false);
});

test('external refresh waits for an active request and preserves drafts on failure', async t => {
  const app = await fixture(t);
  const pending = app.editor.save(); await until(() => app.dialog.open);
  notifyCommit(); assert.equal(app.calls.length, 1);
  app.respond(() => { throw new Error('refresh offline'); });
  await app.dialog.querySelector('[data-cancel]').emit('click'); await pending;
  assert.equal(app.state.resource.base.source, 'old');
  assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
  assert.equal(app.state.currentWonder, detail);
  assert.match(app.state.status, /同步失败.*原状态与草稿已保留.*refresh offline/);
  assert.match(app.editor.log.text, /refresh offline/);
});

test('reload falls back to the initial wonder when the selected entry was deleted', async t => {
  const app = await fixture(t);
  app.respond(url => url === 'api/resources/editor.wonder'
    ? { ...resourcePayload, draft: { ...resourcePayload.draft, wonders: [{ id: 2 }], initial_wonder_id: 2 } } : page(2));
  await app.editor.load({ confirmDirty: true });
  assert.equal(app.state.currentWonder.summary.id, 2);
  assert(app.calls.some(call => call.url.endsWith('/wonders/2')));
  assert(!app.calls.some(call => call.url.endsWith('/wonders/1')));
});

test('a successful commit with failed rendering retains the new base and offers detail retry', async t => {
  const app = await fixture(t);
  app.hooks.render = () => { throw new Error('render probe'); };
  const pending = app.editor.save(); await until(() => app.dialog.open);
  await app.dialog.querySelector('[data-confirm]').emit('click'); await pending;
  assert.equal(app.state.resource.base.source, 'new');
  assert.equal(app.state.resource.dirty, false);
  assert.match(app.state.status, /已保存.*详情加载失败/);
  assert.equal(app.elements.retryDetailButton.hidden, false);
  app.hooks.render = () => {};
  await app.elements.retryDetailButton.emit('click'); await until(() => !app.state.busy);
  assert.equal(app.calls.filter(call => call.url.endsWith('/commit')).length, 1);
});
