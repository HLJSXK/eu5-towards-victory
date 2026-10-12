const assert = require('node:assert/strict');
const { test } = require('node:test');

let helpers;
test.before(async () => {
  helpers = await import('../towards_victory_editor_web/static/cost_reward.js');
});

const tokens = [
  { id: 'alpha', loc: { en: 'Treasury funds', zh: '国库资金' } },
  { id: 'beta', loc: { en: 'Local prosperity', zh: '本地繁荣度' } },
  { id: 'gamma', loc: { en: 'Ship build speed', zh: '造船速度' } },
];

test('filters cost/reward rows by id and bilingual loc text', () => {
  assert.deepEqual(helpers.filterTokens(tokens, 'BETA').map(token => token.id), ['beta']);
  assert.deepEqual(helpers.filterTokens(tokens, '繁荣').map(token => token.id), ['beta']);
  assert.deepEqual(helpers.filterTokens(tokens, 'ship').map(token => token.id), ['gamma']);
  assert.deepEqual(helpers.filterTokens(tokens, '').map(token => token.id), ['alpha', 'beta', 'gamma']);
});

test('dirty row collection ignores empty field maps and supports only-dirty filtering', () => {
  const edits = {
    country_modifier: { alpha: { value: '2' }, beta: {} },
    local_reward: { gamma: { value: '3' } },
  };
  assert.deepEqual([...helpers.dirtyRowKeys(edits)], [helpers.rowKey('country_modifier', 'alpha'), helpers.rowKey('local_reward', 'gamma')]);
  assert(helpers.isTokenDirty(edits, 'country_modifier', 'alpha'));
  assert(!helpers.isTokenDirty(edits, 'country_modifier', 'beta'));
  assert.deepEqual(helpers.filterTokens(tokens, '', true, 'country_modifier', edits).map(token => token.id), ['alpha']);
});

test('filter and only-dirty conditions compose without changing token order', () => {
  const edits = { country_modifier: { alpha: { value: '2' }, gamma: { value: '4' } } };
  assert.deepEqual(helpers.filterTokens(tokens, 'speed', true, 'country_modifier', edits).map(token => token.id), ['gamma']);
  assert.deepEqual(helpers.filterTokens(tokens, 'missing', true, 'country_modifier', edits), []);
});

test('value notes stay within the comments-backed category meanings', () => {
  assert.match(helpers.valueNoteFor('country_reward', 'alpha', 1), /One-shot unit/);
  assert.match(helpers.valueNoteFor('country_modifier', 'alpha', 0.1), /per-level increments/);
  assert.match(helpers.valueNoteFor('country_modifier', 'alpha', true), /unscaled unlock units/);
  assert.match(helpers.valueNoteFor('country_reward', 'inflation', 0.05), /Inverted direction/);
  assert.match(helpers.valueNoteFor('country_modifier', 'monthly_towards_axis', 0.05), /monthly_towards/);
});
