// WP-07: localization panel indexing, filtering, missing-translation statistics and the new-key rule.
//
// Native ES modules with a minimal fake DOM, following tests/generators.cjs and tests/global_shell.cjs.
// The group/filter/statistics helpers are exercised directly; the panel is driven through its real
// factory with a stubbed fetch, so the wiring under test is the one the page uses. The page is mounted
// here once and its `tool-activated` entry is asserted, as generators.cjs does. Real browser behaviour
// is covered by localization_browser.cjs (mounted from resource_state_browser.cjs).
const assert = require('node:assert/strict');
const { test } = require('node:test');

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
    textContent: '', dataset: {}, hidden: false, disabled: false, title: '',
    value: '', type: '', checked: false, classes: new Set(), children: [], listeners: new Map(),
    selectors: new Map(), attributes: new Map(),
    appendChild(child) { node.children.push(child); return child; },
    addEventListener(type, fn) { if (!node.listeners.has(type)) node.listeners.set(type, new Set()); node.listeners.get(type).add(fn); },
    removeEventListener(type, fn) { node.listeners.get(type)?.delete(fn); },
    emit(type, event = {}) { return Promise.all([...node.listeners.get(type) || []].map(fn => fn(event))); },
    querySelector(selector) {
      if (!node.selectors.has(selector)) node.selectors.set(selector, element());
      return node.selectors.get(selector);
    },
    querySelectorAll() { return []; },
    closest() { return node; },
    contains() { return true; },
    focus() {},
    setAttribute(name, value) { node.attributes.set(name, value); },
    getAttribute(name) { return node.attributes.get(name) ?? null; },
  };
  // Assigning innerHTML replaces the children, as the real DOM does (renderTable clears then appends).
  let markup = '';
  Object.defineProperty(node, 'innerHTML', {
    get() { return markup; },
    set(value) { markup = value; node.children.length = 0; },
  });
  node.classList = classList(node);
  return Object.assign(node, extra);
}

const EN = 'src/main_menu/localization/english/tv_demo_l_english.yml';
const ZH = 'src/main_menu/localization/simp_chinese/tv_demo_l_simp_chinese.yml';
const GEN_EN = 'src/main_menu/localization/english/tv_managed_l_english.yml';
const GEN_ZH = 'src/main_menu/localization/simp_chinese/tv_managed_l_simp_chinese.yml';
const ED_EN = 'src_engineering_department/main_menu/localization/english/tv_ed_l_english.yml';
const ED_ZH = 'src_engineering_department/main_menu/localization/simp_chinese/tv_ed_l_simp_chinese.yml';

const rows = (pairs) => pairs.map(([key, value]) => ({ key, value }));
const file = (path, languages, extra = {}) => ({ path, read_only: false, languages, ...extra });
const GENERATED = {
  read_only: true,
  read_only_reason: 'Generated localization; edit source data: data/owner.yaml',
  source_data: ['data/owner.yaml'],
};

// One editable pair carrying a missing key in each direction, one generated pair, and one Engineering
// Department pair. A real payload repeats the pair's EN/ZH arrays in every physical file, which the
// two generated rows here reproduce so the indexing is tested against the real shape.
const DRAFT = {
  roots: [
    { root: 'src', files: [
      file(EN, { english: rows([['a', 'A'], ['b', 'B'], ['only_en', 'Only EN']]),
        simp_chinese: rows([['a', '甲'], ['b', '乙'], ['only_zh', '仅中文']]) }),
      file(ZH, { english: rows([['a', 'A'], ['b', 'B'], ['only_en', 'Only EN']]),
        simp_chinese: rows([['a', '甲'], ['b', '乙'], ['only_zh', '仅中文']]) }),
      file(GEN_EN, { english: rows([['g', 'G']]), simp_chinese: rows([['g', '机']]) }, GENERATED),
      file(GEN_ZH, { english: rows([['g', 'G']]), simp_chinese: rows([['g', '机']]) }, GENERATED),
    ] },
    { root: 'src_engineering_department', files: [
      file(ED_EN, { english: rows([['x', 'X']]), simp_chinese: rows([['x', '叉']]) }),
      file(ED_ZH, { english: rows([['x', 'X']]), simp_chinese: rows([['x', '叉']]) }),
    ] },
  ],
  missing_translations: [{ path: ZH, keys: ['only_en'] }, { path: EN, keys: ['only_zh'] }],
};

const payload = () => ({
  resource: { id: 'editor.localization' },
  draft: JSON.parse(JSON.stringify(DRAFT)),
  change_set: { resource_id: 'editor.localization', files: [EN, ZH],
    base: [{ path: EN, sha256: 'e'.repeat(64) }, { path: ZH, sha256: 'z'.repeat(64) }] },
});

// The page entry runs at import time and reads `document`/`window`, so the fake DOM is installed for
// the whole file, exactly as tests/generators.cjs does. One import is cached per process, so the page
// instance the tests drive is the one the entry created.
const controls = new Map();
const pageListeners = new Map();
const control = (id) => {
  if (!controls.has(id)) controls.set(id, element());
  return controls.get(id);
};
global.document = {
  body: element({ dataset: {} }),
  getElementById: control,
  createElement: () => element(),
  addEventListener(type, fn) { if (!pageListeners.has(type)) pageListeners.set(type, new Set()); pageListeners.get(type).add(fn); },
  removeEventListener(type, fn) { pageListeners.get(type)?.delete(fn); },
};
global.window = Object.assign(new EventTarget(), { confirm: () => true });
const requests = [];
globalThis.fetch = async (url) => { requests.push(String(url)); return Response.json(payload()); };

const modules = import('../towards_victory_editor_web/static/localization.js');
const activateTool = (tool) => Promise.all([...pageListeners.get('tool-activated') || []].map(fn => fn({ detail: { tool } })));

async function helpers() {
  const mod = await modules;
  return { ...mod, groups: mod.groupLocalizationFiles(DRAFT) };
}

test('the page entry loads only when the localization tab is activated, and only once', async () => {
  await modules;
  assert.equal(requests.length, 0, 'nothing is requested before the tab is opened');
  await activateTool('generators');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(requests.length, 0, 'another tab does not load the resource');
  await activateTool('localization');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.deepEqual(requests, ['api/resources/editor.localization']);
  await activateTool('localization');
  await activateTool('cost-reward');
  await activateTool('localization');
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(requests.length, 1, 'a second activation reuses the loaded resource');
});

test('files are indexed into one group per logical file, with generated pairs read-only', async () => {
  const { groups } = await helpers();
  assert.deepEqual(groups.map((group) => group.name).sort(), ['tv_demo', 'tv_ed', 'tv_managed']);
  const demo = groups.find((group) => group.name === 'tv_demo');
  assert.equal(demo.editable, true);
  assert.deepEqual(demo.order, ['a', 'b', 'only_en', 'only_zh'], 'en order first, the zh-only key appended');
  assert.equal(demo.files.english.path, EN);
  assert.equal(demo.files.simp_chinese.path, ZH, 'the pair shares one group across both paths');
  const managed = groups.find((group) => group.name === 'tv_managed');
  assert.equal(managed.editable, false, 'a generated pair cannot be edited');
  assert.deepEqual(managed.sourceData, ['data/owner.yaml']);
  assert.match(managed.reason, /edit source data/);
});

test('read-only comes from either file of the pair, so the other language cannot bypass it', async () => {
  const { groupLocalizationFiles } = await helpers();
  // Only the zh file is registered as a generated output: the whole pair must still be read-only.
  const draft = { roots: [{ root: 'src', files: [
    file(EN, { english: rows([['a', 'A']]), simp_chinese: rows([['a', '甲']]) }),
    file(ZH, { english: rows([['a', 'A']]), simp_chinese: rows([['a', '甲']]) },
      { read_only: true, read_only_reason: 'Generated', source_data: ['data/x.yaml'] }),
  ] }] };
  const [group] = groupLocalizationFiles(draft);
  assert.equal(group.editable, false);
  assert.deepEqual(group.sourceData, ['data/x.yaml']);
});

test('missing translations are counted in both directions and the summary matches the pairs', async () => {
  const { groups, missingKeysFor, localizationSummary } = await helpers();
  const demo = groups.find((group) => group.name === 'tv_demo');
  assert.deepEqual(missingKeysFor(demo, {}), { english: ['only_zh'], simp_chinese: ['only_en'] });
  const summary = localizationSummary(groups, {});
  assert.equal(summary.groups, 3);
  assert.equal(summary.editable, 2, 'the two editable pairs');
  assert.equal(summary.generated, 1, 'the generated pair is reported separately');
  assert.equal(summary.missing, 2, 'one missing key in each direction');
  assert.equal(summary.keys, 5, 'demo has 4 keys, ED has 1');
});

test('filters split by missing and edited, and search matches key or either language', async () => {
  const { groups, entriesFor, filterEntries, writeEdit } = await helpers();
  const demo = groups.find((group) => group.name === 'tv_demo');
  const all = entriesFor(demo, {});
  assert.equal(all.length, 4);
  assert.deepEqual(filterEntries(all, 'missing', '').map((entry) => entry.key), ['only_en', 'only_zh']);
  assert.equal(filterEntries(all, 'edited', '').length, 0, 'nothing is edited yet');
  // Search is case-insensitive and spans the key, the English value and the Chinese value.
  assert.deepEqual(filterEntries(all, 'all', 'B').map((entry) => entry.key), ['b']);
  assert.deepEqual(filterEntries(all, 'all', 'b').map((entry) => entry.key), ['b'], 'case-insensitive');
  assert.deepEqual(filterEntries(all, 'all', '仅中文').map((entry) => entry.key), ['only_zh']);
  // An edit moves its row into the "edited" filter and keeps the missing statistics unchanged.
  const edits = writeEdit({}, demo, 'a', 'simp_chinese', '甲改');
  const after = entriesFor(demo, edits);
  assert.deepEqual(filterEntries(after, 'edited', '').map((entry) => entry.key), ['a']);
  assert.deepEqual(filterEntries(after, 'missing', '').map((entry) => entry.key), ['only_en', 'only_zh']);
  assert.equal(missingKeysForUnchanged(after), true);
});

// Presence, not value, decides "missing": changing a translated value must not create or clear one.
function missingKeysForUnchanged(entries) {
  return entries.filter((entry) => entry.missing).map((entry) => entry.key).join() === 'only_en,only_zh';
}

test('a new key must carry both languages, and only real changes reach the request', async () => {
  const { groups, draftErrors, buildEdits, writeEdit, editCount } = await helpers();
  const demo = groups.find((group) => group.name === 'tv_demo');
  // Adding a key with one language is exactly what contract 6.2 rejects with a 400.
  let edits = writeEdit({}, demo, 'new_key', 'english', 'New');
  assert.deepEqual(draftErrors(groups, edits), ['新增键 new_key 必须同时提供 English 与简体中文值']);
  edits = writeEdit(edits, demo, 'new_key', 'simp_chinese', '新的');
  assert.deepEqual(draftErrors(groups, edits), [], 'both languages satisfied');
  const request = buildEdits(groups, edits, { [EN]: 'e'.repeat(64) });
  assert.deepEqual(request, { edits: { [EN]: { new_key: { english: 'New', simp_chinese: '新的' } } },
    base: { [EN]: 'e'.repeat(64) } }, 'new keys go through the english path only');
  // An existing key sends only the changed language, and reverting the value drops the edit.
  edits = writeEdit({}, demo, 'b', 'simp_chinese', '乙改');
  assert.deepEqual(buildEdits(groups, edits, {}).edits, { [EN]: { b: { simp_chinese: '乙改' } } });
  assert.equal(editCount(edits), 1);
  edits = writeEdit(edits, demo, 'b', 'simp_chinese', '乙');
  assert.deepEqual(edits, {}, 'reverting to the loaded value is not a change');
  assert.equal(editCount(edits), 0);
  // An invalid key is rejected before the server sees it.
  assert.match(draftErrors(groups, { [demo.key]: { 'bad key': { english: 'a', simp_chinese: 'b' } } })[0],
    /非法 key/);
});

test('the panel loads the resource, renders both columns and reports the missing counts', async () => {
  const { createLocalizationPanel } = await helpers();
  const root = element();
  const panel = createLocalizationPanel(root);
  const before = requests.length;
  await panel.load();
  assert.deepEqual(requests.slice(before), ['api/resources/editor.localization']);
  assert.equal(panel.state.loaded, true);
  const counts = root.querySelector('[data-counts]').textContent;
  assert.match(counts, /已加载 3 个分组/);
  assert.match(counts, /可编辑 2 个/);
  assert.match(counts, /生成物 1 个/);
  assert.match(counts, /缺译 2 处/);
  assert.equal(root.querySelector('[data-title]').textContent, 'tv_demo', 'the first editable group is selected');
  // Both columns are present: the table is appended to the scroll host, so its markup is on the child.
  const table = root.querySelector('[data-table]').children[0];
  assert.equal(table.className, 'localization-table');
  assert.match(table.innerHTML, /<th>Key<\/th><th>English<\/th><th>简体中文<\/th>/);
  const demo = panel.state.groups.find((group) => group.name === 'tv_demo');
  assert.deepEqual(panel.entriesOf(demo).filter((entry) => entry.missing).map((entry) => entry.key),
    ['only_en', 'only_zh']);
  assert.equal(root.querySelector('[data-note]').hidden, true, 'an editable group shows no read-only note');
  // Selecting the generated group shows the "edit the data source" hint instead of editable cells.
  const groupsNode = root.querySelector('[data-groups]');
  const managedButton = groupsNode.children.find((button) => button.dataset.group?.includes('tv_managed'));
  assert(managedButton, 'the generated group has its own button');
  await managedButton.emit('click');
  const note = root.querySelector('[data-note]');
  assert.equal(note.hidden, false);
  assert.match(note.textContent, /应改其 data 源：data\/owner\.yaml/);
  assert.equal(root.querySelector('[data-add-toggle]').disabled, true, 'a read-only group cannot add keys');
});
