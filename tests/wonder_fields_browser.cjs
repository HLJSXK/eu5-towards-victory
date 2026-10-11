// Called by resource_state_browser.cjs with its live Chrome page and read-only server.
const assert = require('node:assert/strict');

module.exports = async function wonderFieldsAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate('(' + fn.toString() + ')(...' + JSON.stringify(args) + ')');
  await page(async () => {
    const path = __probe.requests.findLast(r => /\/wonders\/\d+$/.test(r.path)).path;
    const detail = await (await fetch(path)).json();
    const catalog = await (await fetch('/api/wonder-localization/catalog')).json();
    window.__fields = {
      detail, catalog,
      field(type) {
        const fields = this.detail.mechanics.sections.flatMap(s => s.fields).filter(f => f.field_type === type);
        return fields.find(f => f.structured_value?.rows?.length) || fields[0];
      },
      binding(field) { return [...document.querySelectorAll('#language-panels [data-editor-field]')].find(e => e.dataset.key === field.key); },
      shell(type) { return this.binding(this.field(type)).closest('.structured-field'); },
      input(element, value) { element.value = value; element.dispatchEvent(new Event('input', { bubbles: true })); },
      choose(combo, value, keyboard = true) {
        const input = combo.querySelector('input');
        input.focus(); this.input(input, value);
        const item = [...combo.querySelectorAll('.option-item')].find(e => e.textContent.includes(value));
        if (!item) throw new Error('Missing searchable option: ' + value);
        if (keyboard) input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true }));
        else item.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true }));
        if (combo.value !== value) throw new Error('Wrong selected value: ' + combo.value);
      },
    };
  });

  for (const type of ['site_trigger_template', 'site_preference_template', 'modifier_table', 'reward_editor']) {
    const result = await page(type => {
      const field = __fields.field(type), binding = __fields.binding(field), shell = __fields.shell(type);
      return { actual: JSON.parse(binding.value), original: JSON.parse(field.original_value),
        controls: shell.querySelectorAll('.structured-editor input, .structured-editor textarea').length,
        visible: shell.getClientRects().length > 0, code: !!shell.querySelector('.code-state-output').textContent };
    }, type);
    assert.deepEqual(result.actual, result.original, type + ' initial value');
    assert(result.controls > 0 && result.visible && result.code, type + ' rendered: ' + JSON.stringify(result));
  }

  const selection = await page(() => {
    const field = __fields.field('modifier_table'), binding = __fields.binding(field);
    const original = binding.value, rows = JSON.parse(original).rows;
    const combo = __fields.shell('modifier_table').querySelector('.structured-row .option-combobox');
    const ref = field.structured_value.options.catalog_ref;
    const choice = __fields.catalog.catalogs[ref].find(o => o.value && o.value !== rows[0].modifier);
    combo.querySelector('.option-mode-button').click();
    __fields.choose(combo, choice.value, false);
    const selected = JSON.parse(binding.value).rows[0].modifier;
    const stripped = !binding.value.includes('catalog_ref') && !binding.value.includes('"options"');
    const mode = combo.dataset.displayMode;
    __fields.choose(combo, rows[0].modifier);
    return { selected, expected: choice.value, stripped, mode, restored: binding.value === original };
  });
  assert.equal(selection.selected, selection.expected);
  assert(selection.stripped && selection.restored);
  assert.equal(selection.mode, 'key');

  for (const type of ['site_trigger_template', 'site_preference_template']) {
    const result = await page(type => {
      const field = __fields.field(type), preset = field.structured_value.presets.find(p => p.id !== field.structured_value.template_id);
      if (!preset) throw new Error('No alternative preset for ' + type);
      __fields.choose(__fields.shell(type).querySelector('.option-combobox'), preset.id);
      const value = JSON.parse(__fields.binding(field).value);
      const expected = type === 'site_trigger_template'
        ? { any_of: preset.any_of.map(value => ({ value })), all_of: preset.all_of.map(value => ({ value })) }
        : { bonus_rules: preset.bonus_rules, scaled_rules: preset.scaled_rules };
      const actual = Object.fromEntries(Object.keys(expected).map(key => [key, value[key].rows]));
      return { actual, expected, selected: value.template_id, id: preset.id,
        code: !!__fields.shell(type).querySelector('.code-state-output').textContent };
    }, type);
    assert.deepEqual(result.actual, result.expected, type + ' preset rows');
    assert.equal(result.selected, result.id);
    assert(result.code);
  }

  const reward = await page(() => {
    const shell = __fields.shell('reward_editor');
    const input = shell.querySelector('input[placeholder="Value"]');
    __fields.input(input, '0.375');
    return { value: JSON.parse(__fields.binding(__fields.field('reward_editor')).value).rows[0].value,
      code: shell.querySelector('.code-state-output').textContent };
  });
  assert.equal(reward.value, '0.375');
  assert.match(reward.code, /0\.375/);
  assert(await page(() => !document.querySelector('#dirty-badge').classList.contains('hidden')));
  await page(() => document.querySelector('#save-button').click());
  await ready("document.querySelector('#wonder-preview dialog').open");
  assert.match(await page(() => document.querySelector('#wonder-preview tbody').textContent), /0\.375/);
  await page(() => document.querySelector('#wonder-preview [data-cancel]').click());
  await ready("!document.querySelector('#save-button').disabled");
  await page(() => document.querySelector('#reload-button').click());
  await ready("!document.querySelector('#reload-button').disabled");

  const unique = await page(async () => {
    const resource = await (await fetch('/api/resources/editor.wonder')).json();
    const wonder = resource.draft.wonders.find(w => w.is_unique && w.key.includes('dome_of_the_rock'));
    __fields.detail = await (await fetch('/api/wonder-localization/wonders/' + wonder.id)).json();
    document.querySelectorAll('#wonder-kind-tabs button')[1].click();
    document.querySelector('[data-wonder-key="' + wonder.key + '"]').click();
    return wonder.key;
  });
  await ready("document.querySelector('.tool-wonder-localization').dataset.busy === 'false'");
  assert.equal(await page(() => document.querySelector('#wonder-list .active').dataset.wonderKey), unique);
  for (const type of ['unique_ritual_editor', 'unique_ceremony_editor']) {
    const result = await page(type => {
      const field = __fields.field(type), shell = __fields.shell(type);
      return { actual: JSON.parse(__fields.binding(field).value), original: JSON.parse(field.original_value),
        controls: shell.querySelectorAll('input, textarea').length, visible: shell.getClientRects().length > 0 };
    }, type);
    assert.deepEqual(result.actual, result.original, type + ' initial value');
    assert(result.controls > 0 && result.visible, type + ' rendered');
  }

  const edits = await page(() => {
    const initial = document.querySelector('[data-key^="mechanics.unique_initial_level."]');
    __fields.input(initial, '3');
    const constraints = [initial.type, initial.min, initial.max, initial.step];
    const name = document.querySelector('#wonder-name-editors [data-language="english"]');
    __fields.input(name, 'Field module acceptance');
    const ritual = __fields.shell('unique_ritual_editor');
    const years = [...ritual.querySelectorAll('.scalar-field')].find(e => e.firstElementChild.textContent === 'Timed years').querySelector('input');
    __fields.input(years, '2');
    const ceremony = __fields.shell('unique_ceremony_editor');
    const title = [...ceremony.querySelectorAll('.scalar-field')].find(e => e.firstElementChild.textContent === 'Title (English)').querySelector('input');
    __fields.input(title, 'Field ceremony acceptance');
    return { constraints, meta: document.querySelector('#wonder-meta').textContent,
      list: document.querySelector('#wonder-list .active').textContent,
      years: JSON.parse(__fields.binding(__fields.field('unique_ritual_editor')).value).timed.years,
      title: JSON.parse(__fields.binding(__fields.field('unique_ceremony_editor')).value).stages[0].title_en,
      code: ceremony.querySelector('.code-state-output').textContent };
  });
  assert.deepEqual(edits.constraints, ['number', '0', '6', '1']);
  assert.match(edits.meta, /Level 3/);
  assert.match(edits.meta, /Field module acceptance/);
  assert.match(edits.list, /Field module acceptance/);
  assert.equal(edits.years, '2');
  assert.equal(edits.title, 'Field ceremony acceptance');
  assert.match(edits.code, /Field ceremony acceptance/);
  await page(() => document.querySelector('#save-button').click());
  await ready("document.querySelector('#wonder-preview dialog').open");
  const diff = await page(() => document.querySelector('#wonder-preview tbody').textContent);
  assert.match(diff, /Field module acceptance/);
  assert.match(diff, /Field ceremony acceptance/);
  assert.match(diff, /initial_level/);
  await page(() => document.querySelector('#wonder-preview [data-cancel]').click());
  await ready("!document.querySelector('#save-button').disabled");

  const readonly = await page(() => {
    const field = __fields.field('site_trigger_template'), shell = __fields.shell('site_trigger_template');
    const controls = [...shell.querySelectorAll('.structured-editor input, .structured-editor button, .structured-editor textarea')]
      .filter(e => !e.closest('.readonly-actions'));
    const button = shell.querySelector('.readonly-actions button');
    const result = { prototype: field.prototype_key, disabled: controls.every(e => e.disabled),
      note: shell.querySelector('.readonly-note').textContent, actionEnabled: !button.disabled };
    button.click(); return result;
  });
  assert(readonly.disabled && readonly.actionEnabled);
  assert.match(readonly.note, /Inherited from prototype/);
  await ready("document.querySelector('.tool-wonder-localization').dataset.busy === 'false'");
  assert.equal(await page(() => document.querySelector('#wonder-list .active').dataset.wonderKey), readonly.prototype);
  assert(await page(() => !document.querySelector('[data-field-type="site_trigger_template"]').closest('.structured-field').querySelector('.readonly-note')));
  await page(() => document.querySelector('#reload-button').click());
  await ready("!document.querySelector('#reload-button').disabled");
  assert(await page(() => document.querySelector('#dirty-badge').classList.contains('hidden')));
  assert.equal(await page(() => __probe.requests.filter(r => r.path === '/api/resources/editor.wonder/commit').length), 0);

  // Two instances must retain their own callbacks; also exercise the ordinary boolean binding.
  const isolated = await page(async () => {
    const { createWonderFields } = await import('/static/wonder_fields.js');
    const calls = [], hooks = id => ({ onChange: () => calls.push(id), onOpenPrototype() {}, onInitialLevelChange() {} });
    const first = createWonderFields(hooks('first')), second = createWonderFields(hooks('second'));
    const field = { field_type: 'boolean', key: 'probe', value: 'yes', original_value: 'yes' };
    const a = first.buildEditorInput(field, 'mechanics'), b = second.buildEditorInput(field, 'mechanics');
    a.checked = false; a.dispatchEvent(new Event('change'));
    b.checked = false; b.dispatchEvent(new Event('change'));
    a.checked = true; a.dispatchEvent(new Event('change'));
    return { calls, values: [a.value, b.value] };
  });
  assert.deepEqual(isolated, { calls: ['first', 'second', 'first'], values: ['yes', 'no'] });
  await page(() => { delete window.__fields; });
  console.log('Wonder fields acceptance passed: six field types, catalog search, presets, live previews, readonly prototype navigation, name/level callbacks and isolated instances.');
};
