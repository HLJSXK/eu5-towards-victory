// Import the production ES module without a DOM or page state.
const assert = require('node:assert/strict');
const { test } = require('node:test');
const panels = import('../towards_victory_editor_web/static/wonder_panels.js');

test('wonder search includes IDs, keys, bilingual names, concepts, kinds and sizes', async () => {
  const { wonderSearchHaystack } = await panels;
  const wonder = {
    id: 123, key: 'KEY', concept: 'Concept', name_zh: '中文名', name_en: 'English Name',
    display_name: 'Display Name', kind_label: 'Kind', size: 'SIZE', size_label: 'Size Label',
  };
  const before = structuredClone(wonder);
  const haystack = wonderSearchHaystack(wonder);
  for (const term of ['123', 'key', 'concept', '中文名', 'english name', 'display name', 'kind', 'size', 'size label']) {
    assert(haystack.includes(term), term);
  }
  assert.equal(wonderSearchHaystack({}).trim(), '');
  assert.deepEqual(wonder, before);
});

test('wonder mode filtering preserves order and references without changing the input list', async () => {
  const { wondersForMode } = await panels;
  const wonders = [{ key: 'generic', is_unique: false }, { key: 'unique', is_unique: true }, { key: 'other' }];
  const before = structuredClone(wonders);
  assert.deepEqual(wondersForMode(wonders, 'generic'), [wonders[0], wonders[2]]);
  assert.deepEqual(wondersForMode(wonders, 'unique'), [wonders[1]]);
  assert.equal(wondersForMode(wonders, 'unique')[0], wonders[1]);
  assert.deepEqual(wondersForMode([], 'unique'), []);
  assert.deepEqual(wonders, before);
});

test('key lookup distinguishes a generic prototype from a unique wonder with the same key', async () => {
  const { findWonderByKey } = await panels;
  const wonders = [{ key: 'shared', is_unique: true }, { key: 'shared', is_unique: false }];
  assert.equal(findWonderByKey(wonders, 'shared'), wonders[0]);
  assert.equal(findWonderByKey(wonders, 'shared', true), wonders[0]);
  assert.equal(findWonderByKey(wonders, 'shared', false), wonders[1]);
  assert.equal(findWonderByKey(wonders, 'missing'), undefined);
  assert.equal(findWonderByKey([], 'shared'), undefined);
});

test('image alt text accepts summaries and details with bilingual and key fallbacks', async () => {
  const { wonderImageAlt } = await panels;
  assert.equal(wonderImageAlt({ name_zh: '中文', name_en: 'English', key: 'key' }), '中文 image');
  assert.equal(wonderImageAlt({ summary: { name_en: 'English', key: 'key' } }), 'English image');
  assert.equal(wonderImageAlt({ key: 'key' }), 'key image');
  assert.equal(wonderImageAlt(null), 'wonder image');
});

test('initial-level labels distinguish absent, existing and invalid draft values', async () => {
  const { uniqueInitialLevelStartStateLabel } = await panels;
  assert.equal(uniqueInitialLevelStartStateLabel({ valid: true, level: 0, value: '0' }), 'Not present');
  assert.equal(uniqueInitialLevelStartStateLabel({ valid: true, level: 6, value: '6' }), 'Level 6');
  assert.equal(uniqueInitialLevelStartStateLabel({ valid: false, value: '7' }), 'Invalid level: 7');
  assert.equal(uniqueInitialLevelStartStateLabel({ valid: false, value: '' }), 'Invalid level');
});
