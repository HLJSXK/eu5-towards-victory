// Run with: node --test tests/cropper_resource_state.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function editor() {
  const listeners = {};
  const controls = {};
  function control(id) {
    return controls[id] ||= {
      id, dataset: {}, disabled: false, textContent: '', innerHTML: '',
      addEventListener: (event, handler) => { listeners[`${id}:${event}`] = handler; },
      appendChild() {},
    };
  }
  const canvas = control('cropper-canvas');
  canvas.getContext = () => ({
    clearRect() {}, fillRect() {}, drawImage() {}, save() {}, restore() {},
    beginPath() {}, moveTo() {}, lineTo() {}, stroke() {}, strokeRect() {},
  });
  canvas.getBoundingClientRect = () => ({ left: 0, top: 0, width: 100, height: 100 });
  const context = vm.createContext({
    document: {
      body: { dataset: { activeTool: 'wonder-cropper' } },
      activeElement: null,
      getElementById: (id) => id === 'cropper-canvas' ? canvas : control(id),
      createElement: () => ({ type: '', className: '', textContent: '', addEventListener() {}, }),
      addEventListener: (event, handler) => { listeners[`document:${event}`] = handler; },
    },
    window: { addEventListener() {}, confirm: () => true, devicePixelRatio: 1 },
    Image: class { constructor() { this.complete = true; this.naturalWidth = 100; this.naturalHeight = 100; } },
    fetch: () => new Promise(() => {}),
    console: { error() {} },
  });
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/cropper.js'), 'utf8'), context);
  vm.runInContext(`
    cropState.tasks = [
      { name: 'One', rect: { x: 1, y: 2, width: 27, height: 11 }, saved: true },
      { name: 'Two', rect: { x: 3, y: 4, width: 27, height: 11 }, saved: true },
    ];
    cropState.index = 0;
    cropState.rect = { x: 9, y: 9, width: 27, height: 11 };
    cropState.saved = false;
    cropState.dirty = true;
    cropState.base = { source: 'old' };
  `, context);
  return {
    context,
    listeners,
    state: () => vm.runInContext('cropState', context),
    commit: (rect) => vm.runInContext(`commitCrop(${JSON.stringify(rect)})`, context),
    keydown: (event) => listeners['document:keydown'](event),
  };
}

test('commit cannot switch the selected image and only updates the active draft', async () => {
  const app = editor();
  app.context.fetch = async () => ({ ok: true, json: async () => ({
    change_set: { base: [{ path: 'source', sha256: 'new' }] },
    draft: { tasks: [
      { name: 'One', rect: { x: 10, y: 10, width: 27, height: 11 }, saved: true },
      { name: 'Two', rect: { x: 3, y: 4, width: 27, height: 11 }, saved: true },
    ], logs: ['saved One'] },
  }) });
  const pending = app.commit({ x: 10, y: 10, width: 27, height: 11 });
  vm.runInContext('selectTask(1)', app.context);
  await pending;
  assert.equal(app.state().index, 0);
  assert.equal(JSON.stringify(app.state().rect), JSON.stringify({ x: 10, y: 10, width: 27, height: 11 }));
  assert.equal(app.state().dirty, false);
  assert.equal(app.state().base.source, 'new');
});

test('wheel resize is ignored while a commit is pending', async () => {
  const app = editor();
  let respond;
  app.context.fetch = () => new Promise((resolve) => { respond = resolve; });
  vm.runInContext('cropState.image = new Image()', app.context);
  const pending = app.commit({ x: 10, y: 10, width: 27, height: 11 });
  const before = JSON.stringify(app.state().rect);
  app.listeners['cropper-canvas:wheel']({ deltaY: -1, preventDefault() {} });
  assert.equal(JSON.stringify(app.state().rect), before);
  respond({ ok: true, json: async () => ({
    change_set: { base: [{ path: 'source', sha256: 'new' }] },
    draft: { tasks: app.state().tasks, logs: [] },
  }) });
  await pending;
  assert.equal(app.state().dirty, false);
});

test('arrow navigation only handles the visible cropper when focus is outside form controls', () => {
  const app = editor();
  const event = { key: 'ArrowRight', preventDefault() { this.prevented = true; } };
  app.context.document.body.dataset.activeTool = 'wonder-localization';
  app.keydown(event);
  assert.equal(app.state().index, 0);
  assert.equal(event.prevented, undefined);

  app.context.document.body.dataset.activeTool = 'wonder-cropper';
  app.context.document.activeElement = { tagName: 'INPUT', isContentEditable: false };
  app.keydown(event);
  assert.equal(app.state().index, 0);
  assert.equal(event.prevented, undefined);

  app.context.document.activeElement = null;
  app.keydown(event);
  assert.equal(app.state().index, 1);
  assert.equal(event.prevented, true);
});

test('a commit conflict keeps the draft until an explicit reload advances the base', async () => {
  const app = editor();
  app.context.fetch = async (url) => {
    if (url.includes('/commit')) {
      return { ok: false, status: 409, statusText: 'Conflict', json: async () => ({ detail: 'source changed' }) };
    }
    return { ok: true, json: async () => ({
      change_set: { base: [{ path: 'source', sha256: 'reloaded' }] },
      draft: { tasks: app.state().tasks, logs: ['reloaded'] },
    }) };
  };
  await app.commit({ x: 10, y: 10, width: 27, height: 11 });
  assert.equal(app.state().base.source, 'old');
  assert.equal(app.state().dirty, true);
  assert.match(app.context.document.getElementById('cropper-status').textContent, /Reload crops/);
  await app.listeners['cropper-reload:click']();
  assert.equal(app.state().base.source, 'reloaded');
  assert.equal(app.state().dirty, false);
});
