// Native ES module imports; DOM behavior is also checked in resource_state_browser.cjs.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const modules = Promise.all([
  import('../towards_victory_editor_web/static/display.js'),
  import('../towards_victory_editor_web/static/editor_panel.js'),
  import('../towards_victory_editor_web/static/job_panel.js'),
  import('../towards_victory_editor_web/static/resource_state.js'),
]);

class Element {
  constructor() {
    this.textContent = ''; this.innerHTML = ''; this.dataset = {};
    this.disabled = false; this.hidden = false; this.children = [];
    this.listeners = new Map(); this.selectors = new Map();
  }
  appendChild(child) { this.children.push(child); }
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
  showModal() { this.open = true; }
  close() { this.open = false; }
}

function dom(t) {
  const original = { document: global.document, window: global.window, fetch: global.fetch };
  const controls = new Map();
  const control = (id) => {
    if (!controls.has(id)) controls.set(id, new Element());
    return controls.get(id);
  };
  global.document = { getElementById: control, createElement: () => new Element() };
  global.window = { confirm: () => true };
  t.after(() => { for (const [key, value] of Object.entries(original)) global[key] = value; });
  return control;
}

async function until(check) {
  for (let i = 0; i < 20; i++) {
    if (check()) return;
    await new Promise(setImmediate);
  }
  assert.fail('Expected async UI state');
}

async function editorFixture(t) {
  const [, { createEditorPanel }, , { ResourceState, setControlsBusy }] = await modules;
  const control = dom(t);
  const resource = new ResourceState({
    base: { source: 'old' }, saved: { value: 1 }, draft: { value: 2 },
    onChange: (state) => setControlsBusy([control('field'), control('cr-save-btn'), control('cr-reload-btn')], state.busy),
  });
  const editor = createEditorPanel({
    prefix: 'cr', resourceId: 'editor.cost_reward', resource,
    request: () => ({ edits: { value: resource.draft.value }, base: resource.base }),
    apply: (payload) => resource.replace({ base: { source: 'new' }, saved: payload.draft }),
  });
  const dialog = control('cr-preview').querySelector('dialog');
  const preview = { valid: true, diff: [{ path: 'source', id: 'sample', field: 'value', before: 1, after: 2 }] };
  return { editor, resource, control, dialog, preview };
}

test('shared logs, tabs and HTML escaping keep data as text and restore newly rendered controls', async (t) => {
  const [{ escapeHtml, createLogView, createStatusView, renderTabs }, , , { setControlsBusy }] = await modules;
  const control = dom(t);
  const text = '<img src=x onerror="bad()"> & \'quoted\'';
  assert.equal(escapeHtml(text), '&lt;img src=x onerror=&quot;bad()&quot;&gt; &amp; &#39;quoted&#39;');
  const log = createLogView(control('log'));
  log.set(text); log.append('\nnext');
  assert.equal(control('log').textContent, text + '\nnext');
  assert.equal(control('log').innerHTML, '');
  createStatusView(control('status')).set(text, 'error');
  assert.equal(control('status').dataset.kind, 'error');
  let busy = true, selected;
  renderTabs(control('tabs'), { items: [{ id: text }], active: text, key: item => item.id,
    label: item => item.id, busy: () => busy, select: id => { selected = id; } });
  const tab = control('tabs').children[0];
  assert.equal(tab.textContent, text);
  assert.equal(tab.disabled, true);
  await tab.emit('click'); assert.equal(selected, undefined);
  busy = false;
  setControlsBusy([tab], false);
  assert.equal(tab.disabled, false, 'tabs created during a load must unlock with other controls');
  await tab.emit('click'); assert.equal(selected, text);
});

test('generation diagnostics include the operation, attempted artifacts and separate recovery result', async () => {
  const [{ formatOperationReport }] = await modules;
  const text = formatOperationReport({ operation_id: 'commit-1', operation: { status: 'failed', persistence_error: 'disk locked' },
    generation: { status: 'failed', error: 'generator failed', steps: [{ id: 'generate.py', status: 'failed', returncode: 2, duration_seconds: 1.5 }],
      artifacts: [{ path: 'attempt.txt', changed: true }], missing_outputs: ['missing.txt'],
      output_validation: [{ path: 'invalid.txt', valid: false, error: 'bad format' }],
      rollback: { status: 'incomplete', errors: ['restore blocked'] } } });
  for (const expected of ['commit-1', 'disk locked', 'generate.py: 失败 (退出码 2) / 1.5s', 'attempt.txt: 已变化',
    '缺失输出: missing.txt', 'invalid.txt: bad format', '恢复结果: 未完全恢复', 'restore blocked']) assert(text.includes(expected));
});

test('preview renders structured values and derived file hashes without interpreting HTML', async (t) => {
  const [, { createDiffView }] = await modules;
  const control = dom(t), root = control('preview'), diff = createDiffView(root);
  const malicious = '<script>bad()</script>';
  const pending = diff.confirm({ diff: [
    { path: malicious, id: 'id', field: 'value', before: false, after: { name: malicious } },
    { path: 'derived.yaml', before: 'old-hash', after: 'new-hash' },
  ] });
  const dialog = root.querySelector('dialog'), rows = dialog.querySelector('tbody').children;
  assert.equal(rows[0].children[0].textContent, malicious + ' / id / value');
  assert.equal(rows[0].children[1].textContent, 'false');
  assert.equal(rows[0].children[2].textContent, JSON.stringify({ name: malicious }));
  assert.equal(rows[0].children[2].innerHTML, '');
  assert.equal(rows[1].children[0].textContent, 'derived.yaml / 文件摘要');
  await dialog.querySelector('[data-confirm]').emit('click');
  assert.equal(await pending, true);
});

test('Wonder text and structure preview preserves newlines and differentiates deletion from null', async (t) => {
  const [, { createDiffView }] = await modules;
  const root = dom(t)('preview'), diff = createDiffView(root);
  const pending = diff.confirm({ diff: [
    { wonder_id: 101, wonder_key: 'unique_test', language: 'english', field: 'prompt', value_kind: 'text', before: 'First\nSecond', after: '<text>\nThird' },
    { field: 'ritual', value_kind: 'structure', before: { reward: [1, 2] }, after: { reward: [2] } },
    { field: 'prompt', before_present: true, after_present: false, before: '', after: null },
  ] });
  const dialog = root.querySelector('dialog'), rows = dialog.querySelector('tbody').children;
  assert.equal(rows[0].children[0].textContent, '101 / unique_test / english / prompt');
  assert.equal(rows[0].children[1].textContent, 'First\nSecond');
  assert.equal(rows[0].children[2].textContent, '<text>\nThird');
  assert.equal(rows[0].children[2].className, 'diff-value');
  assert.equal(rows[1].children[1].textContent, JSON.stringify({ reward: [1, 2] }, null, 2));
  assert.equal(rows[2].children[2].textContent, '（不存在）');
  await dialog.querySelector('[data-cancel]').emit('click');
  assert.equal(await pending, false);
});

test('save previews before commit, blocks duplicates, and commits the exact confirmed request', async (t) => {
  const { editor, resource, control, dialog, preview } = await editorFixture(t);
  const calls = [];
  global.fetch = async (url, options) => {
    calls.push({ url, options });
    return Response.json(url.endsWith('/preview') ? preview : { draft: { value: 2 }, operation_id: 'saved-1' });
  };
  const pending = editor.save();
  await until(() => dialog.open);
  assert.equal(calls.length, 1);
  assert.equal(control('field').disabled, true);
  assert.equal(resource.mutate(draft => { draft.value = 99; }), false);
  await editor.save(); assert.equal(calls.length, 1);
  assert.equal(resource.base.source, 'old');
  assert.equal(resource.dirty, true);
  await dialog.querySelector('[data-confirm]').emit('click');
  await pending;
  assert(calls[0].url.endsWith('/preview')); assert(calls[1].url.endsWith('/commit'));
  assert.equal(calls[0].options.body, calls[1].options.body);
  assert.equal(resource.base.source, 'new'); assert.equal(resource.dirty, false);
  assert.equal(control('field').disabled, false);
  assert.match(control('cr-log').textContent, /saved-1/);
});

for (const action of ['return', 'escape']) test(`${action} from preview keeps the draft and never commits`, async (t) => {
  const { editor, resource, control, dialog, preview } = await editorFixture(t);
  let calls = 0;
  global.fetch = async () => { calls++; return Response.json(preview); };
  const pending = editor.save(); await until(() => dialog.open);
  if (action === 'return') await dialog.querySelector('[data-cancel]').emit('click');
  else await dialog.emit('cancel', { preventDefault() {} });
  await pending;
  assert.equal(calls, 1); assert.equal(resource.draft.value, 2);
  assert.equal(resource.base.source, 'old'); assert.equal(resource.dirty, true);
  assert.equal(control('field').disabled, false); assert.equal(dialog.open, false);
});

for (const endpoint of ['preview', 'commit']) test(`${endpoint} failure shows diagnostics and keeps the draft and base`, async (t) => {
  const { editor, resource, control, dialog, preview } = await editorFixture(t);
  global.fetch = async (url) => Response.json(url.endsWith('/' + endpoint)
    ? { detail: 'source changed', code: 'resource_changed', operation_id: 'failed-1', log_text: 'server log',
      generation: { status: 'failed', rollback: { status: 'succeeded', errors: [] } } } : preview,
    { status: url.endsWith('/' + endpoint) ? 409 : 200 });
  const pending = editor.save();
  if (endpoint === 'commit') { await until(() => dialog.open); await dialog.querySelector('[data-confirm]').emit('click'); }
  await pending;
  assert.equal(resource.draft.value, 2); assert.equal(resource.base.source, 'old'); assert.equal(resource.dirty, true);
  assert.equal(control('field').disabled, false);
  assert.match(control('cr-log').textContent, /server log[\s\S]*source changed[\s\S]*failed-1[\s\S]*恢复结果: 已完成/);
});

test('reload requires approval for a dirty draft and discards it only on success', async (t) => {
  const { editor, resource } = await editorFixture(t);
  let calls = 0;
  global.fetch = async () => { calls++; return Response.json({ draft: { value: 7 } }); };
  global.window.confirm = () => false;
  await editor.load({ confirmDirty: true }); assert.equal(calls, 0); assert.equal(resource.draft.value, 2);
  global.window.confirm = () => true;
  await editor.load({ confirmDirty: true }); assert.equal(calls, 1); assert.equal(resource.draft.value, 7);
});

test('both job panels show identical file reports, validation errors and retained-backup diagnostics', async (t) => {
  const [, , { createJobPanel }] = await modules;
  const control = dom(t);
  const job = { operation: { id: 'job-1', status: 'failed', resource_ids: ['editor.wonder'] },
    lines: ['<log>'], line_cursor: 1, lines_reset: true,
    outputs_may_be_partial: true, publication_rollback_failed: true,
    source_snapshots: [{ path: 'optional.png', sha256: 'missing' }], staging_extra_files: ['staging/extra'],
    formal_output_changes: ['external.dds'], declared_outputs: ['changed.dds', 'unchanged.dds', 'deleted.png', 'missing.dds'],
    artifacts: [{ path: 'changed.dds', changed: true }, { path: 'unchanged.dds', changed: false }, { path: 'deleted.png', role: 'deleted' }],
    missing_outputs: ['missing.dds'], metadata: { output_validation: [{ path: 'changed.dds', valid: false, error: 'bad header' }] } };
  for (const prefix of ['media', 'cropper']) {
    const panel = createJobPanel({ root: control(prefix + '-job'), prefix, onChange() {} });
    panel.start(job);
    assert.equal(control(prefix + '-log').textContent, '<log>');
    assert.match(control(prefix + '-identity').textContent, /job-1/);
    assert.equal(control(prefix + '-files').hidden, false);
  }
  const report = control('cropper-file-report').textContent;
  assert.equal(report, control('media-file-report').textContent);
  for (const expected of ['optional.png（可选，缺失）', 'changed.dds（已变化）: bad header', 'unchanged.dds（未变化）',
    'deleted.png（已删除）', 'missing.dds（缺失）', '不参与发布的中间文件', '发布恢复失败', 'external.dds']) assert(report.includes(expected));
});
