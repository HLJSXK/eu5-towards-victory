const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');
const context = vm.createContext({});
vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/resource_state.js'), 'utf8').replace(/^export /gm, ''), context);
const { ResourceState } = vm.runInContext('({ ResourceState })', context);

test('requests freeze editing and duplicates, and failure retains draft and base', async () => {
  const state = new ResourceState({ base: { source: 'old' }, saved: { text: 'saved' } });
  state.mutate((draft) => { draft.text = 'draft'; });
  let reject;
  const request = state.run('saving', () => new Promise((_, fail) => { reject = fail; }));
  assert.equal(state.mutate((draft) => { draft.text = 'lost'; }), false);
  await state.run('loading', () => assert.fail('duplicate request'));
  reject(new Error('conflict'));
  await assert.rejects(request, /conflict/);
  assert.equal(state.base.source, 'old');
  assert.equal(state.saved.text, 'saved');
  assert.equal(state.draft.text, 'draft');
  assert.equal(state.dirty, true);
  assert.equal(state.error.message, 'conflict');
  assert.equal(state.busy, false);
  state.setDraft({ text: 'saved' });
  assert.equal(state.dirty, false);
});

test('replacing a resource ignores both stale success and stale failure', async () => {
  for (const fail of [false, true]) {
    const state = new ResourceState();
    let finish;
    const request = state.run('loading', () => new Promise((resolve, reject) => { finish = fail ? reject : resolve; }), { apply: () => assert.fail('stale apply') });
    state.replace({ base: { source: 'new' }, saved: { value: 2 } });
    finish(fail ? new Error('stale') : { value: 1 });
    await request;
    assert.equal(state.draft.value, 2);
    assert.equal(state.error, null);
    assert.equal(state.phase, 'idle');
  }
});

test('applying a replacement keeps the request busy and reports render failures', async () => {
  const state = new ResourceState();
  await assert.rejects(state.run('loading', async () => ({ value: 2 }), { apply: (result) => {
    state.replace({ saved: result });
    assert.equal(state.busy, true);
    throw new Error('render failed');
  } }), /render failed/);
  assert.equal(state.error.message, 'render failed');
  assert.equal(state.busy, false);
  assert.equal(state.draft.value, 2);
});
