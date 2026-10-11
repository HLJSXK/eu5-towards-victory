// Native ES module import; the final test compares previews with real backend normalizers.
// Run with EU5_PYTHON set if the Windows default does not apply.
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { resolve } = require('node:path');
const { test } = require('node:test');
const values = import('../towards_victory_editor_web/static/wonder_values.js');

const backendScript = `
import json, sys, yaml
from towards_victory_editor_web.services.wonder import values, site_rules, site_templates
from scripts_engineering_department.wonder_mechanics.rituals import ceremony_cost_computed_value

request = json.load(sys.stdin)
if request["task"] == "catalogs":
    result = {
        "triggers": site_templates.TRIGGER_CONDITION_OPTIONS,
        "conditions": site_templates.PREFERENCE_CONDITION_OPTIONS,
        "sources": site_templates.PREFERENCE_SCALE_SOURCE_OPTIONS,
        "costs": [
            {"type": f"{catalog}:{entry}", "value": str(ceremony_cost_computed_value(catalog, entry, index))}
            for index, (catalog, entry) in enumerate([
                ("country_reward", "government_power"), ("country_reward", "scaled_gold")
            ], start=1)
        ],
    }
else:
    result = []
    for case in request["cases"]:
        state, kind = case["state"], case["kind"]
        if kind == "modifier":
            normalized = values.mapping_from_modifier_rows(state, context=kind)
        elif kind == "reward":
            normalized = {"cost_type": state.get("cost_type") or None,
                          "reward": values.reward_list_from_rows(state, context=kind)}
        elif kind == "strings":
            normalized = values.list_from_string_rows(state, context=kind)
        elif kind == "ritual":
            normalized = values.unique_ritual_from_editor_state(state, context=kind)
        elif kind == "ceremony":
            normalized = values.unique_ceremony_from_editor_state(state, context=kind)
            # The inline preview uses the editor's composite catalog:id representation.
            for stage in normalized["stages"]:
                stage["cost"] = [{"type": row["type"], "value": values.parse_editor_scalar(row["value"])}
                                 for row in values.ceremony_cost_rows_from_list(stage["cost"])]
        elif kind == "strip":
            normalized = values.without_editor_options(state)
        elif kind == "trigger":
            normalized = site_rules.render_trigger_script_from_state(state, context=kind)
        elif kind == "preference":
            normalized = site_rules.render_preference_script_from_state(state, context=kind)
        else:
            raise AssertionError(kind)
        result.append({"normalized": normalized,
                       "preview": yaml.safe_load(case["preview"]) if "preview" in case else None})
print(json.dumps(result, ensure_ascii=False))
`;

function backend(request) {
  const python = process.env.EU5_PYTHON || 'C:/Users/Hades/anaconda3/envs/eu5/python.exe';
  const result = spawnSync(python, ['-c', backendScript], {
    cwd: resolve(__dirname, '..'), encoding: 'utf8', windowsHide: true,
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' }, input: JSON.stringify(request),
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr);
  return JSON.parse(result.stdout);
}

let catalog;
function catalogs() { return catalog ||= backend({ task: 'catalogs' }); }

const modifierState = { rows: [
  { modifier: 'amount', value: ' -2 ' },
  { modifier: 'ratio', value: '.125' },
  { modifier: 'scaled', value: '1e2' },
  { modifier: 'script', value: 'var:tv_wonder_site_preference_bonus' },
  { modifier: '', value: '' },
] };
const rewardState = { cost_type: 'prestige', rows: [
  { type: 'prestige', value: '10' }, { type: 'scaled_gold', value: '-.5' },
  { type: 'government_power', value: 'var:tv_wonder_site_preference_bonus' },
  { type: '', value: '' },
] };
const ritualState = {
  key: ' test_ritual ', mode: 'timed', cost_type: 'prestige',
  listeners: { rows: [{ value: ' monthly ' }, { value: '' }] },
  runtime_variables: { rows: [{ value: ' progress ' }] },
  country_modifier: modifierState, reward: rewardState,
  confirmation_trigger_script: '  always = yes\r\n  ',
  start_effect_script: '', snapshot_effect_script: '', progress_effect_script: '',
  completion_trigger_script: '', completion_effect_script: '',
  timed: { years: ' 3 ', burden_modifier: { rows: [] }, blessing_modifier: modifierState },
  auxiliary_building: {
    local_modifier: { rows: [] }, attributes: { rows: [{ modifier: 'enabled', value: 'yes' }] },
    maintenance: '  2  ', build_time: '', construction_demand: '', price: '  10  ', max_levels: '2',
  },
};

function ceremonyState() {
  return { stage_count: 2, stages: catalogs().costs.map((cost, index) => ({
    title_en: ` Stage ${index + 1} `, title_zh: ` 阶段${index + 1} `,
    desc_en: ' First\r\nSecond ', desc_zh: ' 第一行\r第二行 ',
    icon: ' icon.dds ', icon_rationale: ' reason ',
    cost: { rows: [cost], options: [{ value: cost.type }] },
    option_pay_en: ' Pay ', option_pay_zh: ' 支付 ',
    option_decline_en: ' Decline ', option_decline_zh: ' 拒绝 ',
  })) };
}

function triggerState(any = ['has_river', 'adjacent_lake'], all = ['is_port']) {
  return { template_id: 'current_variant', condition_options: catalogs().triggers,
    any_of: { rows: any.map(value => ({ value })) }, all_of: { rows: all.map(value => ({ value })) } };
}

function preferenceState() {
  return { template_id: 'current_variant', condition_options: catalogs().conditions,
    scale_source_options: catalogs().sources,
    bonus_rules: { rows: [
      { branch: 'if', condition: 'topography_mountains', value: '10' },
      { branch: 'else_if', condition: 'topography_hills', value: '-2' },
      { branch: 'if', condition: '', value: '' },
    ] },
    scaled_rules: { rows: [
      { source: 'development', min: '0', max: '100', multiplier: '.5' },
      { source: 'total_building_levels', min: '1', max: '10', multiplier: '2' },
      { source: '', min: '', max: '', multiplier: '' },
    ] },
  };
}

test('text normalization preserves multiline content and flattens localization lines', async () => {
  const v = await values;
  const text = '  First\r\n第二行\rThird\n\nLast  ';
  assert.equal(v.normalizeLocalizationText(text), 'First 第二行 Third  Last');
  assert.equal(v.normalizeMultilineText(text), 'First\n第二行\nThird\n\nLast');
  assert.equal(v.asOptionalText('\r\n  '), null);
  assert.equal(v.asOptionalText(' First\rSecond '), 'First\nSecond');
});

test('structured field detection, stable serialization and cloning retain source data', async () => {
  const v = await values;
  for (const type of ['modifier_table', 'reward_editor', 'unique_ritual_editor', 'unique_ceremony_editor',
    'site_trigger_template', 'site_preference_template']) assert(v.isStructuredFieldType(type));
  for (const type of ['text', 'yaml', 'script', undefined]) assert.equal(v.isStructuredFieldType(type), false);
  const original = { z: [{ b: 2, a: '奇观' }, null], a: false };
  assert.equal(v.stableStringify(original), '{"a":false,"z":[{"a":"奇观","b":2},null]}');
  const clone = v.deepClone(original);
  clone.z[0].a = 'changed';
  assert.equal(original.z[0].a, '奇观');
  assert.equal(v.deepClone(null), null);
  assert.equal(v.deepClone(undefined), undefined);
});

test('editor catalogs strip recursively and restore without replacing edited source values', async () => {
  const v = await values;
  const server = { title: 'saved', options: ['top'], cost_options: ['cost'],
    stages: [{ title: 'saved stage', cost: { rows: [{ type: 'old', value: '1' }], options: ['nested'] } }],
    server_only: { options: ['unused'] } };
  const draft = { title: 'edited', stages: [
    { title: 'edited stage', cost: { rows: [{ type: 'new', value: '2' }] } },
    { title: 'new stage', cost: { rows: [] } },
  ] };
  const saved = v.deepClone(server);
  assert(v.isEditorOptionKey('options')); assert(v.isEditorOptionKey('cost_options'));
  assert.equal(v.isEditorOptionKey('option_pay_en'), false);
  assert.equal(v.restoreEditorOptions(draft, server), draft);
  assert.deepEqual(draft.options, ['top']);
  assert.deepEqual(draft.stages[0].cost.options, ['nested']);
  assert.deepEqual(v.withoutEditorOptions(draft), { title: 'edited', stages: [
    { title: 'edited stage', cost: { rows: [{ type: 'new', value: '2' }] } },
    { title: 'new stage', cost: { rows: [] } },
  ] });
  assert.equal(Object.hasOwn(draft, 'server_only'), false);
  assert.deepEqual(server, saved);
});

test('numeric and row conversion preserves scripts and ignores unfinished preview rows', async () => {
  const v = await values;
  for (const [input, expected] of [[' -2 ', -2], ['0', 0], ['.125', .125], ['-2.5e+2', -250],
    ['1e2', 100], ['', ''], [null, ''], ['yes', 'yes'], ['var:progress', 'var:progress']]) {
    assert.equal(v.parseNumberMaybe(input), expected);
  }
  assert.deepEqual(v.rowsToModifierMapping([...modifierState.rows, null,
    { modifier: 'unfinished', value: '' }, { modifier: '', value: '3' }]),
  { amount: -2, ratio: .125, scaled: 100, script: 'var:tv_wonder_site_preference_bonus' });
  assert.deepEqual(v.rowsToModifierMapping([{ attribute: 'level', value: '2' }], 'attribute'), { level: 2 });
  assert.deepEqual(v.rowsToRewardList([...rewardState.rows, { type: 'unfinished' }, null]), [
    { type: 'prestige', value: 10 }, { type: 'scaled_gold', value: -.5 },
    { type: 'government_power', value: 'var:tv_wonder_site_preference_bonus' },
  ]);
  assert.deepEqual(v.rowsToStringList([{ value: ' monthly ' }, { value: '' }, null]), ['monthly']);
  assert.deepEqual(v.rowsToModifierMapping(), {});
  assert.deepEqual(v.rowsToRewardList(), []);
  assert.deepEqual(v.rowsToStringList(), []);
});

test('unique ritual payload includes nested values and normalizes empty editing defaults', async () => {
  const v = await values;
  const payload = v.uniqueRitualPayloadFromState(ritualState);
  assert.equal(payload.key, 'test_ritual'); assert.equal(payload.mode, 'timed');
  assert.equal(payload.confirmation_trigger_script, 'always = yes');
  assert.deepEqual(payload.listeners, ['monthly']); assert.deepEqual(payload.runtime_variables, ['progress']);
  assert.equal(payload.timed.years, 3); assert.deepEqual(payload.timed.burden_modifier, {});
  assert.deepEqual(payload.auxiliary_building, { local_modifier: {}, maintenance: '2', build_time: null,
    construction_demand: null, price: '10', attributes: { enabled: 'yes' }, max_levels: 2 });
  const empty = v.uniqueRitualPayloadFromState({ timed: { years: 'bad' }, auxiliary_building: { max_levels: '-2' } });
  assert.equal(empty.key, 'ritual'); assert.equal(empty.mode, 'immediate'); assert.equal(empty.cost_type, null);
  assert.equal(empty.timed.years, 1); assert.equal(empty.auxiliary_building.max_levels, 1);
  assert.deepEqual(empty.reward, []); assert.deepEqual(empty.listeners, []);
});

test('unique ceremony payload retains stage order, multilingual text and composite costs', async () => {
  const v = await values;
  const payload = v.uniqueCeremonyPayloadFromState(ceremonyState());
  assert.equal(payload.stages.length, 2); assert.equal(payload.stages[1].title_en, 'Stage 2');
  assert.equal(payload.stages[0].title_zh, '阶段1'); assert.equal(payload.stages[0].desc_zh, '第一行\n第二行');
  assert.equal(payload.stages[0].desc_en, 'First\nSecond'); assert.equal(payload.stages[0].icon, 'icon.dds');
  assert.equal(payload.stages[0].cost[0].type, 'country_reward:government_power');
  assert.equal(typeof payload.stages[0].cost[0].value, 'number');
  assert.equal(Object.hasOwn(payload.stages[0].cost, 'options'), false);
  assert.deepEqual(v.uniqueCeremonyPayloadFromState({}), { stages: [] });
});

test('option normalization preserves metadata and provides searchable primary and secondary labels', async () => {
  const v = await values;
  assert.deepEqual(v.normalizeOption('Key'), { value: 'Key', label: 'Key', key_label: 'Key',
    localized_label: 'Key', search_text: 'key' });
  const option = v.normalizeOption({ value: 'key', label: 'English', key_label: 'scope:key',
    localized_label: '中文', label_en: 'EN', description_zh: '说明', source: 'Catalog', script: 'kept' });
  assert.equal(option.search_text, 'key english scope:key 中文 en 说明 catalog');
  assert.equal(option.script, 'kept');
  assert.equal(v.normalizeOption({ value: 2, search_text: 'OVERRIDE' }).search_text, 'override');
  assert.equal(v.optionPrimaryText(option, 'key'), 'scope:key');
  assert.equal(v.optionSecondaryText(option, 'key'), '中文');
  assert.equal(v.optionPrimaryText(option, 'localized'), '中文');
  assert.equal(v.optionSecondaryText(option, 'localized'), 'scope:key');
  assert.equal(v.optionPrimaryText(null, 'key'), ''); assert.equal(v.optionSecondaryText(null, 'key'), '');
  const options = v.optionsWithBlank([option], 'None');
  assert.equal(options[0].value, ''); assert.equal(options[0].localized_label, 'None');
  assert.equal(v.optionsWithBlank(options, 'Other').length, 2);
  assert.deepEqual(v.normalizeOptionList(null), []);
  assert.equal(v.optionByValue(options).get('key').label, 'English');
});

test('site trigger rendering preserves custom, empty, single and OR-with-required scripts', async () => {
  const v = await values;
  assert.equal(v.renderSiteTriggerScript({ template_id: 'custom_script', raw_script: ' always = yes\r\n ' }), 'always = yes');
  assert.equal(v.renderSiteTriggerScript(triggerState([], [])), 'always = yes');
  assert.equal(v.renderSiteTriggerScript(triggerState(['is_port'], [])), 'is_port = yes');
  assert.equal(v.renderSiteTriggerScript(triggerState()), 'OR = {\n\thas_river = yes\n\tis_adjacent_to_lake = yes\n}\nis_port = yes');
});

test('site preference renders conditional bonuses, scaling and one final variable cleanup', async () => {
  const v = await values;
  assert.equal(v.renderSitePreferenceScript({ template_id: 'custom_script', raw_script: ' First\rSecond ' }), 'First\nSecond');
  assert.equal(v.renderSitePreferenceScript({}), '');
  const script = v.renderSitePreferenceScript(preferenceState());
  assert.match(script, /^if = \{\n\tlimit = \{ var:tv_wonder_survey_site \?= \{ topography = mountains \} \}/);
  assert.match(script, /else_if = \{[\s\S]*value = -2/);
  assert.match(script, /clamp_variable = \{ name = tv_wonder_site_preference_bonus min = 0 max = 100 \}/);
  assert.match(script, /multiply = \.5/);
  assert.equal(script.split('remove_variable =').length, 2);
  assert(script.endsWith('remove_variable = tv_wonder_site_preference_bonus'));
});

test('YAML rendering keeps nested lists, empty values, Unicode and multiline scalar quoting', async () => {
  const v = await values;
  assert.equal(v.yamlScalar('中文\n"quoted"'), '"中文\\n\\"quoted\\""');
  assert.equal(v.yamlScalar('scope:key'), 'scope:key');
  assert.equal(v.yamlScalar(''), '""'); assert.equal(v.yamlScalar(null), 'null');
  assert.equal(v.yamlScalar(true), 'true'); assert.equal(v.yamlScalar(2.5), '2.5');
  assert.equal(v.inlineYamlValue([]), '[]'); assert.equal(v.inlineYamlValue({}), '{}');
  assert.deepEqual(v.renderYamlLines({ list: [null, {}, { text: '中文\nSecond' }, ['one']], empty: [], map: {} }), [
    'list:', '  - null', '  - {}', '  -', '    text: "中文\\nSecond"', '  -', '    - one',
    'empty:', '  []', 'map: {}',
  ]);
  assert.deepEqual(v.renderYamlLines({}, 1), ['  {}']);
  assert.deepEqual(v.renderYamlLines(null, 1), ['  null']);
  assert(v.isPlainObject({})); assert.equal(v.isPlainObject([]), false); assert.equal(v.isPlainObject(null), false);
});

test('field previews select the correct payload, source path and indentation', async () => {
  const v = await values;
  for (const [parent, key] of [['style_1', 'country_modifier'], ['style_2', 'local_modifier']]) {
    assert.deepEqual(v.previewPayloadForField({ field_type: 'modifier_table', target_kind: 'generic_ritual',
      target_parent_key: parent }, { rows: [{ modifier: 'amount', value: '2' }] }), { [key]: { amount: 2 } });
  }
  assert.equal(v.previewTextForField({ field_type: 'modifier_table', target_path: 'ritual.modifier' },
    { rows: [{ modifier: 'amount', value: '2' }] }), 'ritual.modifier:\n  amount: 2');
  assert.deepEqual(v.previewPayloadForField({ field_type: 'reward_editor' }, { rows: [] }), { cost_type: null, reward: [] });
  for (const type of ['site_trigger_template', 'site_preference_template']) {
    assert.equal(v.previewTextForField({ field_type: type, key: 'fallback', target_path: 'site.script' },
      { template_id: 'custom_script', raw_script: 'First\nSecond' }), 'site.script\n  First\n  Second');
  }
  assert.equal(v.previewTextForField({ field_type: 'site_trigger_template', key: 'fallback' }, triggerState([], [])),
    'fallback\n  always = yes');
  const raw = { text: '中文', empty: '' };
  assert.equal(v.previewPayloadForField({ field_type: 'other' }, raw), raw);
});

test('frontend YAML previews and scripts agree with backend normalization of the same editor states', async () => {
  const v = await values;
  // Numeric-looking optional text has an existing preview quoting discrepancy,
  // tracked in Editor_Web_Refactor_Status.md; this extraction preserves rendering.
  const ritual = v.deepClone(ritualState);
  ritual.auxiliary_building.maintenance = 'var:progress';
  ritual.auxiliary_building.price = 'var:progress';
  const cases = [
    { kind: 'modifier', state: modifierState, field: { field_type: 'modifier_table' } },
    { kind: 'reward', state: rewardState, field: { field_type: 'reward_editor' } },
    { kind: 'reward', state: { rows: [] }, field: { field_type: 'reward_editor' } },
    { kind: 'ritual', state: ritual, field: { field_type: 'unique_ritual_editor' } },
    { kind: 'ceremony', state: ceremonyState(), field: { field_type: 'unique_ceremony_editor' } },
    { kind: 'strings', state: { rows: [{ value: ' monthly ' }, { value: '' }, { value: 'ending_war' }] } },
    { kind: 'strip', state: { options: ['top'], nested: [{ cost_options: ['cost'], rows: [], text: '中文' }] } },
    { kind: 'trigger', state: triggerState() },
    { kind: 'trigger', state: triggerState([], []) },
    { kind: 'trigger', state: triggerState(['is_port'], []) },
    { kind: 'trigger', state: { template_id: 'custom_script', raw_script: ' always = yes\r\n ' } },
    { kind: 'preference', state: preferenceState() },
  ];
  for (const item of cases) {
    if (item.field) item.preview = v.previewTextForField(item.field, item.state);
    else if (item.kind === 'strings') item.preview = v.renderYamlLines(v.rowsToStringList(item.state.rows)).join('\n');
  }
  const results = backend({ task: 'compare', cases });
  cases.forEach((item, index) => {
    const result = results[index];
    if (item.preview !== undefined) assert.deepEqual(result.preview, result.normalized, item.kind);
    else if (item.kind === 'strip') assert.deepEqual(v.withoutEditorOptions(item.state), result.normalized);
    else {
      const render = item.kind === 'trigger' ? v.renderSiteTriggerScript : v.renderSitePreferenceScript;
      assert.equal(render(item.state), result.normalized, item.kind);
    }
  });
});
