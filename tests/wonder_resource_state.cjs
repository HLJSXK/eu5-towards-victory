// Run with: node --test tests/wonder_resource_state.cjs
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function editor() {
    const control = { dataset: {}, addEventListener() {} };
    const prompts = [];
    const context = vm.createContext({
        document: {
            querySelector: () => control,
            querySelectorAll: () => [],
            getElementById: () => control,
        },
        window: { addEventListener() {}, confirm: (message) => { prompts.push(message); return true; } },
        console: { error() {} },
        // Leave the automatic bootstrap pending; each test supplies its own loaded state.
        fetch: () => new Promise(() => {}),
    });
    vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/wonder_localization.js'), 'utf8'), context);
    vm.runInContext(`
        render = () => {};
        showToast = () => {};
        cacheCurrentWonderDraft = () => {};
        cacheCurrentRitualPromptDraft = () => {};
        hydrateWonderPayload = async (payload) => payload;
        state.busy = false;
        state.currentWonder = { summary: { id: 1 } };
        state.resourceBase = { source: 'old' };
        state.pageDrafts = { 2: { values: { english: { title: 'old draft' } }, mechanics: {} } };
    `, context);
    return {
        context,
        prompts,
        state: vm.runInContext('state', context),
        reload: () => vm.runInContext('reloadCurrentWonder()', context),
        respond: (fetcher) => { context.testFetch = fetcher; vm.runInContext('fetchJson = testFetch', context); },
    };
}

const resource = {
    change_set: { base: [{ path: 'source', sha256: 'new' }] },
    draft: { wonders: [{ id: 1 }, { id: 2 }], log_text: '' },
};

test('reload confirms and discards every page draft before advancing the resource base', async () => {
    const app = editor();
    app.respond(async (url) => url === 'api/resources/editor.wonder'
        ? resource : { summary: { id: 1 }, languages: {}, mechanics: {} });
    await app.reload();
    assert.equal(app.prompts.length, 1, 'a dirty page other than the current one must require confirmation');
    assert.equal(Object.keys(app.state.pageDrafts).length, 0);
    assert.equal(app.state.resourceBase.source, 'new');
});

test('cancelled reload retains the old base and all drafts without making requests', async () => {
    const app = editor();
    app.context.window.confirm = () => false;
    let calls = 0;
    app.respond(async () => { calls += 1; return resource; });
    await app.reload();
    assert.equal(calls, 0);
    assert.equal(app.state.resourceBase.source, 'old');
    assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
});

for (const failure of ['resource', 'detail', 'catalog']) {
    test(`failed ${failure} reload preserves the old base, current detail and every draft`, async () => {
        const app = editor();
        const previousWonder = app.state.currentWonder;
        app.respond(async (url) => {
            if (failure === 'resource' || (failure === 'detail' && url !== 'api/resources/editor.wonder')) {
                throw new Error('load failed');
            }
            return url === 'api/resources/editor.wonder' ? resource : { summary: { id: 1 } };
        });
        if (failure === 'catalog') {
            vm.runInContext('hydrateWonderPayload = async () => { throw new Error("catalog failed"); }', app.context);
        }
        await app.reload();
        assert.equal(app.state.resourceBase.source, 'old');
        assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
        assert.equal(app.state.currentWonder, previousWonder);
        assert.equal(app.state.busy, false);
    });
}

test('a rejected commit refreshes the displayed log and retains drafts and base', async () => {
    const app = editor();
    app.context.fetch = async () => ({
        ok: false, status: 409, statusText: 'Conflict',
        json: async () => ({ detail: 'source changed', log_text: '[error] source changed\n' }),
    });
    await vm.runInContext(`
        renderLog = () => { globalThis.displayedLog = state.logText; };
        saveCurrentWonder();
    `, app.context);
    assert.equal(app.state.resourceBase.source, 'old');
    assert.equal(app.state.pageDrafts[2].values.english.title, 'old draft');
    assert.equal(app.state.logText, '[error] source changed\n');
    assert.equal(app.context.displayedLog, app.state.logText);
});
