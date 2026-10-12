const assert = require('node:assert/strict');
const { test } = require('node:test');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');

let helpers, indicators;
test.before(async () => {
  helpers = await import('../towards_victory_editor_web/static/victory_paths.js');
  indicators = await import('../towards_victory_editor_web/static/resource_state.js');
});
test.beforeEach(() => indicators.resetToolIndicators());

const sourcePaths = ['data/victory_paths.yaml', 'data/victory_path_tasks.yaml'];
const task = (pathId, id, index) => ({ task_id: id, source: { path_id: pathId, task_index: index },
  fields: { key: `task_${id}`, type: 'fixed', thresholds: [10, 20], custom_tooltip: false, loc: { en: 'Task', zh: '任务' } } });
const path = (id) => ({ id, score_var: `tv_${id}_score`, gui: { order: 0, tab_label: { en: id, zh: '路径' } },
  loc: { title: { en: 'Title', zh: '标题' } }, score_updater_body: 'line one\nline two\n',
  milestones: [{ n: 1, threshold: 200, is_short_term: false, unlock_body: null,
    reward_options: [{ modifier: { discipline: 0.05 } }], loc: { title: { en: 'M1', zh: '里程碑一' } } }],
  tasks: { label: { en: id, zh: '路径' }, color: { r: 0.1, g: 0.2, b: 0.3 },
    items: [task(id, 1001, 0), task(id, 1002, 1)] } });
const plan = () => ({ required: false, registry_complete: true, generators: ['scripts/demo.cpy', 'scripts/downstream.cpy'],
  outputs: ['src/one.txt', 'src/two.txt'], steps: [
    { script: 'scripts/demo.cpy', outputs: ['src/one.txt'] },
    { script: 'scripts/downstream.cpy', outputs: ['src/two.txt'] }], errors: [] });
const payload = () => ({ resource_id: 'editor.victory_paths', schema_version: 1,
  sources: sourcePaths.map((path, index) => ({ path, sha256: String(index + 1).repeat(64), size: 10 })),
  document: { shared: { situation_name: { en: 'Victory', zh: '胜利' } }, paths: [path('conquest'), path('science')],
    on_actions: [], national_special: { tasks: [task('national_special', 9001, 0)] } },
  references: { rewards: [{ key: 'discipline', resolved: true, source_resource: 'editor.cost_reward', editable: false, editable_here: false }], tasks: [] },
  generation: plan(), read_only_outputs: true, constraints: {} });
const allFields = (document, id = 'conquest') => helpers.victoryFieldGroups(document, id).flatMap((group) => group.fields);
const threshold = (document) => allFields(document).find((field) => field.name.endsWith('.threshold'));

async function harness(overrides = {}) {
  const fixture = { latest: payload(), requests: [], statuses: [], diagnostics: [], reports: [], commits: [] };
  const controller = helpers.createVictoryPathsController({
    api: async (url, options) => {
      fixture.requests.push({ url, body: options?.body });
      if (!options) return structuredClone(fixture.latest);
      const body = JSON.parse(options.body);
      const operation = url.split('/').at(-1);
      if (overrides[operation]) return overrides[operation](fixture, body);
      const common = { references: fixture.latest.references, generation: { ...plan(), required: true } };
      if (operation === 'validate') return { ...common, valid: true, errors: [], warnings: [] };
      if (operation === 'preview') return { ...common, ready: true, validation: { errors: [], warnings: [] },
        diff: { fields: [{ path: sourcePaths[0], field: 'paths[0].milestones[0].threshold', before: 200, after: body.document.paths[0].milestones[0].threshold }],
          sources: [{ path: sourcePaths[0], changed: true, before_sha256: '1'.repeat(64), after_sha256: 'a'.repeat(64) }] } };
      assert.equal(operation, 'commit', 'never call generator execution endpoints');
      fixture.latest.document = body.document;
      fixture.latest.sources[0].sha256 = 'a'.repeat(64);
      return { ...structuredClone(fixture.latest), operation_id: 'vp-save', status: 'succeeded', written_paths: [sourcePaths[0]],
        generation: { status: 'succeeded', generators: plan().generators, outputs: plan().outputs,
          artifacts: [{ path: 'src/one.txt', changed: true }] }, rollback: { status: 'not_needed', errors: [] } };
    }, confirmPreview: overrides.confirmPreview || (async () => false),
    status: (text) => fixture.statuses.push(text), diagnostic: (text) => fixture.diagnostics.push(text),
    report: (value) => fixture.reports.push(value), onCommitted: (value) => fixture.commits.push(value),
  });
  fixture.controller = controller;
  await controller.load();
  return fixture;
}

test('fields group shared, path, milestones, task catalogue and national tasks separately', () => {
  const document = payload().document;
  const groups = helpers.victoryFieldGroups(document, 'conquest');
  assert.deepEqual(groups.map((group) => group.key), ['shared', 'path', 'gui', 'loc', 'milestone-1',
    'task-settings', 'task-1001', 'task-1002', 'on-actions', 'national-special', 'national-9001']);
  assert(groups.find((group) => group.key === 'task-settings').slots);
  const fields = groups.flatMap((group) => group.fields);
  assert(fields.some((field) => field.name === 'shared.situation_name.zh'));
  assert(fields.filter((field) => field.name.endsWith('.task_index')).every((field) => field.readOnly));
  assert(fields.find((field) => field.name.endsWith('.reward_options')).readOnly);
  assert.equal(threshold(document).kind, 'number');
  assert(!fields.some((field) => field.name.includes('science')));
  assert(!fields.some((field) => field.name.endsWith('.slot')));
});

test('draft changes notify the victory-paths dirty indicator and reverting clears it', async () => {
  const { controller } = await harness();
  const field = threshold(controller.state.document);
  const base = structuredClone(controller.state.resource.base);
  controller.edit(field, '250');
  assert.equal(controller.state.resource.dirty, true);
  assert.equal(indicators.toolIndicator('victory-paths').dirty, true);
  assert.equal(Object.keys(controller.state.resource.draft.edits).length, 1);
  assert.equal(field.value, 200, 'loaded values stay separate from local drafts');
  assert.deepEqual(controller.state.resource.base, base);
  controller.edit(field, '200');
  assert.equal(controller.state.resource.dirty, false);
  assert.equal(indicators.toolIndicator('victory-paths').dirty, false);
});

test('request uses only document and the two source hashes without generated slot fields', async () => {
  const { controller } = await harness();
  controller.edit(threshold(controller.state.document), '250');
  const request = helpers.buildVictoryRequest(controller.state.document, controller.state.resource, 'test');
  assert.equal(request.document.paths[0].milestones[0].threshold, 250);
  assert.equal(request.message, 'test');
  assert.deepEqual(request.base.sources.map((item) => item.path), sourcePaths);
  assert.deepEqual(request.document.paths[0].tasks.items[0].source, { path_id: 'conquest', task_index: 0 });
  assert(!JSON.stringify(request).includes('task_pool'));
  assert(!JSON.stringify(request).includes('tree_variant'));
  assert.equal(controller.edit(allFields(controller.state.document).find((field) => field.readOnly), 'invalid'), false);
});

test('invalid numeric and JSON input remains a dirty draft and blocks validate and commit', async () => {
  const { controller, requests } = await harness();
  controller.edit(threshold(controller.state.document), '');
  assert(controller.blocked());
  assert(controller.state.resource.dirty);
  await controller.validate();
  await controller.save();
  assert.equal(requests.length, 1);
  controller.edit(threshold(controller.state.document), '200');
  const field = allFields(controller.state.document).find((item) => item.name.endsWith('.thresholds'));
  controller.edit(field, '[10,');
  assert.equal(Object.values(controller.state.resource.draft.edits)[0].raw, '[10,');
  assert(controller.blocked());
  assert.throws(() => helpers.buildVictoryRequest(controller.state.document, controller.state.resource), /不可提交/);
  controller.edit(field, '[10,20]');
  assert.equal(controller.state.resource.dirty, false);
});

test('booleans, multiline scripts and null values keep their types in the candidate', async () => {
  const { controller } = await harness();
  const fields = allFields(controller.state.document);
  controller.edit(fields.find((item) => item.name.endsWith('.is_short_term')), true);
  controller.edit(fields.find((item) => item.name.endsWith('.score_updater_body')), 'new\nscript\n');
  controller.edit(fields.find((item) => item.name.endsWith('.unlock_body')), '"effect = yes"');
  const document = helpers.buildVictoryRequest(controller.state.document, controller.state.resource).document;
  assert.equal(document.paths[0].milestones[0].is_short_term, true);
  assert.equal(document.paths[0].score_updater_body, 'new\nscript\n');
  assert.equal(document.paths[0].milestones[0].unlock_body, 'effect = yes');
});

test('cancelled preview preserves base and sparse draft with no commit', async () => {
  let preview;
  const { controller, requests } = await harness({ confirmPreview: async (value) => { preview = value; return false; } });
  controller.edit(threshold(controller.state.document), '250');
  const base = structuredClone(controller.state.resource.base);
  await controller.save();
  assert.deepEqual(requests.map((item) => item.url.split('/').at(-1)), ['editor.victory_paths', 'validate', 'preview']);
  assert.equal(preview.diff[0].field, 'paths[0].milestones[0].threshold');
  assert.equal(preview.diff[0].after, 250);
  assert.equal(preview.file_diff[0].before, '1'.repeat(64));
  assert.deepEqual(controller.state.resource.base, base);
  assert(controller.state.resource.dirty);
});

test('save freezes identical validate, preview and commit bodies and clears drafts only after commit', async () => {
  let controller;
  const fixture = await harness({ confirmPreview: async () => {
    assert(controller.state.resource.busy);
    assert.equal(controller.edit(threshold(controller.state.document), '999'), false);
    return true;
  } });
  controller = fixture.controller;
  controller.edit(threshold(controller.state.document), '250');
  await controller.save('save message');
  const bodies = fixture.requests.filter((item) => item.body).map((item) => item.body);
  assert.equal(bodies.length, 3);
  assert(bodies.every((body) => body === bodies[0]));
  assert.equal(controller.state.document.paths[0].milestones[0].threshold, 250);
  assert.equal(controller.state.resource.base[sourcePaths[0]], 'a'.repeat(64));
  assert.equal(controller.state.resource.dirty, false);
  assert.equal(indicators.toolIndicator('victory-paths').dirty, false);
  assert.equal(fixture.commits.length, 1);
  assert.equal(controller.state.artifacts.length, 1);
  assert.equal(controller.state.plan.steps.length, 2, 'commit result is not a generation plan');
});

test('missing reward reference from GET blocks save until read-only validation resolves it', async () => {
  const fixture = await harness();
  fixture.latest.references.rewards[0].resolved = false;
  await fixture.controller.refreshKeepingDrafts();
  assert(fixture.controller.blocked());
  assert.equal(helpers.missingRewardReferences(fixture.controller.state.references)[0].key, 'discipline');
  const count = fixture.requests.length;
  await fixture.controller.save();
  assert.equal(fixture.requests.length, count);
  fixture.latest.references.rewards[0].resolved = true;
  await fixture.controller.validate();
  assert.equal(fixture.controller.blocked(), false);
});

test('missing rewards discovered during validation never open preview or commit', async () => {
  const fixture = await harness({ validate: (fixture) => ({ valid: false,
    errors: [{ path: 'rewards.discipline', message: 'Missing reference' }], warnings: [], generation: plan(),
    references: { rewards: [{ ...fixture.latest.references.rewards[0], resolved: false }], tasks: [] } }) });
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  await fixture.controller.save();
  assert.deepEqual(fixture.requests.map((item) => item.url.split('/').at(-1)), ['editor.victory_paths', 'validate']);
  assert(fixture.controller.blocked());
  assert(fixture.controller.state.resource.dirty);
  assert.match(fixture.statuses.at(-1), /奖励引用失效/);
});

test('not-ready previews cannot be confirmed or committed', async () => {
  const fixture = await harness({ preview: () => ({ ready: false, generation: plan(), references: payload().references,
    validation: { errors: [{ path: 'milestones', message: 'Rejected' }], warnings: [] } }),
    confirmPreview: () => { throw new Error('must not confirm'); } });
  await fixture.controller.save();
  assert.equal(fixture.requests.length, 3);
  assert.match(fixture.statuses.at(-1), /预览未就绪/);
});

test('409 refreshes base and preserves user draft without retrying commit', async () => {
  const fixture = await harness({ preview: (fixture) => {
    fixture.latest.sources[0].sha256 = 'b'.repeat(64);
    fixture.latest.document.paths[0].milestones[0].threshold = 210;
    throw Object.assign(new Error('source conflict'), { status: 409, code: 'resource_changed' });
  } });
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  await fixture.controller.save();
  assert.equal(fixture.controller.state.resource.base[sourcePaths[0]], 'b'.repeat(64));
  assert.equal(helpers.buildVictoryRequest(fixture.controller.state.document, fixture.controller.state.resource)
    .document.paths[0].milestones[0].threshold, 250);
  assert(fixture.controller.state.resource.dirty);
  assert(fixture.diagnostics.some((text) => text.includes('source conflict')));
  assert(fixture.diagnostics.some((text) => text.includes('原值已变化')));
  assert.equal(fixture.requests.at(-1).url, 'api/resources/editor.victory_paths');
  assert(!fixture.requests.some((item) => item.url.endsWith('/commit')));
});

test('resource_busy does not rebase or auto-retry a commit', async () => {
  const fixture = await harness({ commit: () => { throw Object.assign(new Error('busy'), { status: 409, code: 'resource_busy' }); },
    confirmPreview: async () => true });
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  const base = structuredClone(fixture.controller.state.resource.base);
  await fixture.controller.save();
  assert.equal(fixture.requests.length, 4);
  assert.deepEqual(fixture.controller.state.resource.base, base);
  assert(fixture.controller.state.resource.dirty);
});

test('generation failure retains operation diagnostics, base and unsaved draft', async () => {
  const failure = Object.assign(new Error('generator failed'), { status: 500, operation_id: 'failed-vp',
    generation: { status: 'failed' }, operation: { details: { rollback: { status: 'completed', errors: [] } } } });
  const fixture = await harness({ commit: () => { throw failure; }, confirmPreview: async () => true });
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  const base = structuredClone(fixture.controller.state.resource.base);
  await fixture.controller.save();
  assert.deepEqual(fixture.controller.state.resource.base, base);
  assert(fixture.controller.state.resource.dirty);
  assert.equal(fixture.reports.at(-1), failure);
  assert.equal(fixture.commits.length, 0);
});

test('refresh failure leaves loaded document, base and draft unchanged', async () => {
  const fixture = await harness();
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  const snapshot = JSON.stringify(fixture.controller.state);
  fixture.controller.state.resource.run = async () => { throw new Error('GET unavailable'); };
  await fixture.controller.refreshKeepingDrafts();
  assert.equal(JSON.stringify(fixture.controller.state), snapshot);
  assert.match(fixture.statuses.at(-1), /旧 base 与草稿已保留/);
});

test('identity-based refresh survives reordered paths and tasks without changing task source identity', async () => {
  const fixture = await harness();
  const field = allFields(fixture.controller.state.document).find((item) => item.name.endsWith('items[1001].fields.loc.zh'));
  fixture.controller.edit(field, '任务草稿');
  fixture.latest.document.paths.reverse();
  const conquest = fixture.latest.document.paths.find((item) => item.id === 'conquest');
  conquest.tasks.items.reverse();
  conquest.tasks.items.forEach((item, index) => { item.source.task_index = index; });
  await fixture.controller.refreshKeepingDrafts();
  const candidate = helpers.buildVictoryRequest(fixture.controller.state.document, fixture.controller.state.resource).document;
  const updated = candidate.paths.find((item) => item.id === 'conquest').tasks.items[1];
  assert.equal(updated.fields.loc.zh, '任务草稿');
  assert.equal(updated.source.task_index, 1);
  assert.equal(candidate.paths[0].tasks.items[0].fields.loc.zh, '任务');
});

test('deleted targets retain orphan drafts and block submit rather than silently applying elsewhere', async () => {
  const fixture = await harness();
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  fixture.latest.document.paths.shift();
  await fixture.controller.refreshKeepingDrafts();
  assert(fixture.controller.state.resource.dirty);
  assert(fixture.controller.blocked());
  assert.equal(fixture.controller.localErrors()[0].orphan, true);
  assert.match(fixture.diagnostics.at(-1), /草稿仍保留/);
  assert.throws(() => helpers.buildVictoryRequest(fixture.controller.state.document, fixture.controller.state.resource), /不可提交/);
});

test('cost/reward refresh is deferred through confirmation and never expands the two-source base', async () => {
  let fixture;
  fixture = await harness({ confirmPreview: async () => {
    fixture.latest.references.rewards[0].resolved = false;
    fixture.controller.handleCommitted({ resourceId: 'editor.cost_reward', writtenPaths: ['data/cost_reward_units.yaml'] });
    assert.equal(fixture.requests.length, 3, 'GET waits until preview/confirmation is idle');
    return false;
  } });
  fixture.controller.edit(threshold(fixture.controller.state.document), '250');
  const base = structuredClone(fixture.controller.state.resource.base);
  await fixture.controller.save();
  assert.equal(fixture.requests.length, 4);
  assert.deepEqual(fixture.controller.state.resource.base, base);
  assert(fixture.controller.state.resource.dirty);
  assert(fixture.controller.blocked());
  fixture.controller.handleCommitted({ resourceId: 'editor.victory_paths', writtenPaths: sourcePaths });
  fixture.controller.handleCommitted({ resourceId: 'unrelated', writtenPaths: ['data/task_pool.yaml'] });
  assert.equal(fixture.requests.length, 4);
});

test('generation plan is entirely registry-derived and includes read-only output and artifact reports', () => {
  const text = helpers.generationPlanText(plan(), [{ path: 'src/one.txt', changed: true }]);
  assert.match(text, /2 个生成器；2 个只读产物/);
  assert.match(text, /1\. scripts\/demo.cpy/);
  assert.match(text, /2\. scripts\/downstream.cpy/);
  assert.match(text, /只读产物（去重）/);
  assert.match(text, /src\/one.txt: 已变化/);
  assert.match(helpers.generationPlanText({ ...plan(), registry_complete: false }), /不完整，禁止提交/);
});

function element(tag = 'div') {
  const selectors = new Map(), listeners = new Map();
  const node = { tagName: tag.toUpperCase(), children: [], dataset: {}, attributes: {}, disabled: false, value: '',
    appendChild(child) { this.children.push(child); return child; },
    replaceChildren(...children) { this.children = children; },
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener(name, callback) { listeners.set(name, callback); },
    dispatch(name) { listeners.get(name)?.({ target: this }); },
    querySelector(selector) {
      if (!selectors.has(selector)) selectors.set(selector, element(selector.endsWith('-btn') ? 'button' : 'div'));
      return selectors.get(selector);
    },
    querySelectorAll() { return [...selectors.values(), ...descendants(this)].filter((child) => ['BUTTON', 'INPUT', 'TEXTAREA', 'SELECT'].includes(child.tagName)); },
  };
  Object.defineProperty(node, 'textContent', { get() { return (this.text || '') + this.children.map((child) => child.textContent).join(''); },
    set(value) { this.text = value; this.children = []; } });
  return node;
}
function descendants(node) {
  return node.children.flatMap((child) => [child, ...descendants(child)]);
}

test('panel renders typed grouped fields, three read-only slots, dirty drafts and path switching', async () => {
  const root = element();
  global.document = { createElement: element, getElementById: () => element() };
  global.window = Object.assign(new EventTarget(), { confirm: () => true });
  try {
    const controller = helpers.createVictoryPathsPanel(root, { api: async () => payload() });
    await controller.load();
    const sections = root.querySelector('[data-fields]').children;
    assert(sections.some((section) => section.dataset.group === 'shared'));
    assert(sections.some((section) => section.dataset.group === 'milestone-1'));
    assert.equal(descendants(root.querySelector('[data-fields]')).filter((node) => node.textContent === '槽 1 · 运行时选择（只读）').length, 1);
    const controls = descendants(root.querySelector('[data-fields]'));
    const input = controls.find((node) => node.dataset.field === 'paths[conquest].milestones[1].threshold');
    assert(input);
    input.value = '250'; input.dispatch('input');
    assert.match(root.querySelector('[data-dirty]').textContent, /1 个字段/);
    assert(indicators.toolIndicator('victory-paths').dirty);
    root.querySelector('[data-paths]').children[1].dispatch('click');
    root.querySelector('[data-paths]').children[0].dispatch('click');
    assert.equal(descendants(root.querySelector('[data-fields]')).find((node) => node.dataset.field === input.dataset.field).value, '250');
    assert.equal(root.querySelector('#vp-save-btn').disabled, false);
  } finally { delete global.document; delete global.window; }
});

test('panel renders unresolved reward warning and prevents save with read-only reference and output controls', async () => {
  const root = element(), missing = payload();
  missing.references.rewards[0].resolved = false;
  global.document = { createElement: element, getElementById: () => element() };
  global.window = new EventTarget();
  try {
    const controller = helpers.createVictoryPathsPanel(root, { api: async () => missing });
    await controller.load();
    assert.match(root.querySelector('[data-references]').textContent, /discipline · 引用失效，禁止提交/);
    assert.equal(root.querySelector('#vp-save-btn').disabled, true);
    assert.match(root.querySelector('[data-plan]').textContent, /只读产物/);
    assert.equal(root.querySelector('[data-references]').querySelectorAll().length, 0);
    assert.equal(root.querySelector('[data-plan]').querySelectorAll().length, 0);
  } finally { delete global.document; delete global.window; }
});

test('eight-tab shell registers a dirty dot, external modal and wrapping without generator execution', () => {
  const staticRoot = join(__dirname, '../towards_victory_editor_web/static');
  const html = readFileSync(join(staticRoot, 'index.html'), 'utf8');
  assert.equal((html.match(/<button class="tool-hub-tab-btn"/g) || []).length, 8);
  assert.match(html, /data-tool="victory-paths">胜利路径<span class="tool-hub-tab-dot" data-dot hidden>/);
  assert(html.indexOf('id="vp-preview"') > html.lastIndexOf('</main>'));
  assert.match(readFileSync(join(staticRoot, 'shared.css'), 'utf8'), /\.tool-hub-tab-bar\s*\{\s*flex-wrap: wrap;/);
  const code = readFileSync(join(staticRoot, 'victory_paths.js'), 'utf8');
  assert(!code.includes('api/generators/run'));
  assert(!code.includes('task_pool.yaml'));
  assert(!code.includes('victory_path_tree_variant.yaml'));
});
