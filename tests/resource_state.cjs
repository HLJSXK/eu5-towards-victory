// Native ES module imports.
const assert = require('node:assert/strict');
const { test, before } = require('node:test');
let ResourceState, JobPoller;
before(async () => { ({ ResourceState, JobPoller } = await import('../towards_victory_editor_web/static/resource_state.js')); });

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

test('a render failure during polling is reported and keeps an active job polling', async () => {
  const timers = [];
  const errors = [];
  let renders = 0;
  const responses = [
    { operation: { id: 'job', status: 'running', error: null }, line_cursor: 1, lines: ['a'] },
    { operation: { id: 'job', status: 'succeeded', error: null }, line_cursor: 2, lines: ['b'] },
  ];
  const poller = new JobPoller({
    fetchJob: async () => responses.shift(),
    onUpdate: () => { renders += 1; if (renders === 2) throw new Error('render failed'); },
    onError: (error, retrying) => errors.push([error.message, retrying]),
    schedule: (callback) => { timers.push(callback); return timers.length; },
    cancel: () => {},
  });
  poller.start({ operation: { id: 'job', status: 'queued', error: null }, line_cursor: 0, lines: [] });
  await poller.poll();
  assert.equal(renders, 2);
  assert.deepEqual(errors, [['render failed', true]]);
  assert.equal(poller.active, true);
  assert.notEqual(poller.timer, null);
  assert.deepEqual([...poller.lines], ['a']);
  await poller.poll();
  assert.equal(renders, 3);
  assert.equal(poller.active, false);
  assert.deepEqual([...poller.lines], ['a', 'b']);
});
