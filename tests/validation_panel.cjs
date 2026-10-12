// WP-05: validation panel rendering and save-triggered validation. Native ES modules with a minimal fake DOM;
// the real page is covered by validation_panel_browser.cjs.
const assert = require('node:assert/strict');
const { test } = require('node:test');

class Element {
  constructor() {
    this.textContent = ''; this.innerHTML = ''; this.dataset = {}; this.hidden = false; this.disabled = false;
    this.children = []; this.listeners = new Map(); this.selectors = new Map();
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

const controls = new Map();
const control = (id) => {
  if (!controls.has(id)) controls.set(id, new Element());
  return controls.get(id);
};
global.document = { getElementById: control, createElement: () => new Element() };
global.window = Object.assign(new EventTarget(), { confirm: () => true });
const modules = Promise.all([
  import('../towards_victory_editor_web/static/validation_panel.js'),
  import('../towards_victory_editor_web/static/editor_panel.js'),
  import('../towards_victory_editor_web/static/resource_state.js'),
]);

const PASS = { pass: true, errors: [], warnings: [], files_checked: 6, command: [], duration_ms: 2400, fixed: [] };
const WARNINGS = { ...PASS, warnings: [
  { rule: 'style', message: 'long line', file: 'src/a.txt', line: 3 },
  { rule: 'style', message: 'trailing space' },
] };
const ERRORS = { ...PASS, pass: false, files_checked: 3, errors: [
  { rule: 'loc', message: '[LOC] duplicate key tv_probe', file: 'src/main_menu/localization/english/x_l_english.yml', line: 12 },
  { rule: 'loc', message: '[LOC] missing simp_chinese <b>tv_probe</b>', file: 'src/y.yml' },
  { rule: 'syntax', message: 'unbalanced braces', file: 'src/z.txt', line: 40 },
], warnings: [{ rule: 'style', message: 'long line' }] };

function count(html, pattern) { return (html.match(pattern) || []).length; }
const items = (html, severity) => count(html, new RegExp(`class="validation-item" data-severity="${severity}"`, 'g'));

function panelFixture(responses) {
  const calls = [], copied = [];
  return import('../towards_victory_editor_web/static/validation_panel.js').then(({ createValidationPanel }) => {
    const root = new Element();
    const panel = createValidationPanel(root, {
      fetch: async (url, options) => {
        calls.push({ url, ...options });
        const next = responses.shift();
        return next instanceof Response ? next : Response.json(next);
      },
      writeText: async (text) => { copied.push(text); },
    });
    const part = (selector) => root.querySelector(selector);
    return { root, panel, calls, copied, part };
  });
}

test('pass, warnings and errors responses render their summary, state and grouped item counts', async () => {
  const { root, panel, calls, copied, part } = await panelFixture([PASS, WARNINGS, ERRORS]);
  assert.equal(root.dataset.state, 'idle');
  assert.match(part('.validation-status').textContent, /尚未校验/);

  await panel.run('manual');
  assert.equal(calls[0].url, 'api/validate');
  assert.equal(calls[0].method, 'POST');
  assert.deepEqual(JSON.parse(calls[0].body), { changed: true });
  assert.equal(root.dataset.state, 'pass');
  assert.equal(part('.validation-status').textContent, '校验通过（检查 6 个文件，用时 2.4 秒）');
  assert.equal(part('.validation-results').hidden, true);
  assert.equal(part('.validation-results').innerHTML, '');

  await panel.run('manual');
  assert.equal(root.dataset.state, 'warnings');
  assert.equal(part('.validation-status').textContent, '校验通过，有 2 条警告（检查 6 个文件，用时 2.4 秒）');
  let html = part('.validation-results').innerHTML;
  assert.equal(items(html, 'warning'), 2);
  assert.equal(items(html, 'error'), 0);
  assert.match(html, /<code class="validation-file"[^>]*>src\/a\.txt:3<\/code>/);

  await panel.run('saved');
  assert.equal(root.dataset.state, 'errors');
  assert.equal(part('.validation-status').textContent, '校验失败：3 条错误，1 条警告（检查 3 个文件，用时 2.4 秒）');
  html = part('.validation-results').innerHTML;
  assert.equal(part('.validation-results').hidden, false);
  assert.equal(items(html, 'error'), 3);
  assert.equal(items(html, 'warning'), 1);
  // Grouped by rule: loc (2) and syntax (1) error groups plus one warning group.
  assert.equal(count(html, /<section class="validation-group" data-severity="error">/g), 2);
  assert.match(html, /错误 · loc <span class="validation-count">2<\/span>/);
  assert.match(html, /错误 · syntax <span class="validation-count">1<\/span>/);
  assert.match(html, /src\/main_menu\/localization\/english\/x_l_english\.yml:12/);
  assert.match(html, /\[LOC\] missing simp_chinese &lt;b&gt;tv_probe&lt;\/b&gt;/, 'messages are escaped');
  assert(!html.includes('<b>tv_probe'));

  assert.equal(part('[data-copy]').disabled, false);
  await part('[data-copy]').emit('click');
  assert.equal(copied.length, 1);
  assert.equal(copied[0].split('\n')[0], '校验失败：3 条错误，1 条警告（检查 3 个文件，用时 2.4 秒）');
  assert.match(copied[0], /\[错误\] loc \(2\)\n  src\/main_menu\/localization\/english\/x_l_english\.yml:12 \[LOC\] duplicate key tv_probe/);
  assert.match(copied[0], /\[警告\] style \(1\)\n  long line/);
  assert.equal(part('[data-copy]').textContent, '已复制');
});

test('400/504/500 responses show an incomplete validation, not a pass or a rule failure', async () => {
  const { root, panel, copied, part } = await panelFixture([
    Response.json({ detail: 'Validation timed out after 180 seconds', output_tail: 'tail <line>' }, { status: 504 }),
    Response.json({ detail: 'Expected a repository-relative path' }, { status: 400 }),
    new Response('plain failure', { status: 500 }),
  ]);
  await panel.run();
  assert.equal(root.dataset.state, 'failed');
  assert.equal(part('.validation-status').textContent, '校验未完成：HTTP 504：Validation timed out after 180 seconds');
  assert.equal(part('.validation-results').innerHTML, '<pre class="validation-output">tail &lt;line&gt;</pre>');
  await part('[data-copy]').emit('click');
  assert.equal(copied[0], '校验未完成：HTTP 504：Validation timed out after 180 seconds\ntail <line>');
  await panel.run();
  assert.equal(part('.validation-status').textContent, '校验未完成：HTTP 400：Expected a repository-relative path');
  assert.equal(part('.validation-results').hidden, true);
  await panel.run();
  assert.equal(part('.validation-status').textContent, '校验未完成：HTTP 500：plain failure');
  assert.equal(part('[data-validate]').disabled, false);
});

test('a save during a running validation queues exactly one follow-up run', async () => {
  let release;
  const responses = [new Promise(resolve => { release = resolve; }), Promise.resolve(Response.json(PASS))];
  const { createValidationPanel } = (await modules)[0];
  const root = new Element();
  let calls = 0;
  const panel = createValidationPanel(root, { fetch: () => { calls++; return responses.shift(); } });
  const first = panel.run('saved');
  assert.equal(root.dataset.state, 'running');
  assert.equal(root.querySelector('[data-validate]').disabled, true);
  panel.run('saved'); panel.run('saved');
  release(Response.json(ERRORS));
  await first;
  assert.equal(calls, 2);
  assert.equal(root.dataset.state, 'pass');
});

test('the page instance validates on resource-saved and editor_panel emits it only after a successful commit', async (t) => {
  const [, { createEditorPanel }, { ResourceState }] = await modules;
  const calls = [];
  const originalFetch = global.fetch;
  t.after(() => { global.fetch = originalFetch; });
  global.fetch = async (url, options = {}) => {
    calls.push({ url, body: options.body });
    if (url === 'api/validate') return Response.json(ERRORS);
    if (url.endsWith('/preview')) return Response.json({ valid: true, diff: [] });
    if (url.endsWith('/commit') && calls.filter(c => c.url.endsWith('/commit')).length === 1) {
      return Response.json({ code: 'resource_changed', detail: 'probe changed' }, { status: 409 });
    }
    return Response.json({ draft: { value: 2 } });
  };
  const saved = [];
  window.addEventListener('resource-saved', ({ detail }) => saved.push(detail.resourceId));
  const resource = new ResourceState({ base: { source: 'old' }, saved: { value: 1 }, draft: { value: 2 } });
  const editor = createEditorPanel({
    prefix: 'vp', resourceId: 'editor.cost_reward', resource,
    request: () => ({ edits: resource.draft, base: resource.base }),
    apply: (payload) => resource.replace({ base: { source: 'new' }, saved: payload.draft }),
  });
  const dialog = control('vp-preview').querySelector('dialog');
  const save = async (accept) => {
    const pending = editor.save();
    for (let i = 0; i < 20 && !dialog.open; i++) await new Promise(setImmediate);
    await dialog.querySelector(accept ? '[data-confirm]' : '[data-cancel]').emit('click');
    await pending;
  };
  await save(false); // returned to edit: no commit
  await save(true); // 409 conflict
  assert.deepEqual(saved, []);
  assert.equal(calls.filter(c => c.url === 'api/validate').length, 0);
  await save(true); // committed
  assert.deepEqual(saved, ['editor.cost_reward']);
  const panel = control('validation-panel');
  for (let i = 0; i < 20 && panel.dataset.state !== 'errors'; i++) await new Promise(setImmediate);
  const validations = calls.filter(c => c.url === 'api/validate');
  assert.equal(validations.length, 1);
  assert.deepEqual(JSON.parse(validations[0].body), { changed: true });
  assert.equal(panel.dataset.state, 'errors');
  assert.equal(items(panel.querySelector('.validation-results').innerHTML, 'error'), 3);
});
