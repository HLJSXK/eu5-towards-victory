// WP-07: localization tab. Mounted from resource_state_browser.cjs.
//
// The resource comes from the real read-only GET /api/resources/editor.localization, and saving goes
// through the real `/preview` (read-only, server-side diff). The commit POST is intercepted by the
// harness's commit gate and answered with 409, so nothing is ever written to a business file; that the
// draft and the dirty dot survive the rejection is what the assertions below check. Real writes are
// covered by tests/test_localization_resource_contract.py in a temporary repository copy.
const assert = require('node:assert/strict');

module.exports = async function localizationAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate('(' + fn.toString() + ')(...' + JSON.stringify(args) + ')');
  const dot = `document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot')`;

  // The tab builds its (empty) body at page load but loads the resource only on first activation.
  assert.equal(await page(() => __probe.requests.filter((request) => request.path === '/api/resources/editor.localization').length), 0,
    'the resource is not fetched before the tab is opened');
  assert.equal(await page(() => document.querySelectorAll('#localization-root .localization-group').length), 0,
    'no groups are rendered before the tab is opened');
  await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="localization"]').click());
  await ready("document.querySelector('#localization-root').dataset.busy === 'false' && !!document.querySelector('#localization-root .localization-group')");

  const loaded = await page(() => {
    const root = document.querySelector('#localization-root');
    const groups = [...root.querySelectorAll('.localization-group')];
    return {
      groups: groups.length,
      keys: groups.map((node) => node.querySelector('.localization-group-name').textContent),
      meta: groups.map((node) => node.querySelector('.localization-group-meta').textContent),
      counts: root.querySelector('[data-counts]').textContent,
      note: root.querySelector('[data-note]').hidden,
      active: root.querySelector('.localization-group.active')?.querySelector('.localization-group-name').textContent,
      heading: document.querySelector('.tool-localization .subtitle').textContent,
      panelActive: document.querySelector('.tool-localization').classList.contains('active'),
      panels: document.querySelectorAll('.tool-panel.active').length,
      dotHidden: document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').hidden,
    };
  });
  assert(loaded.groups > 10, `groups rendered: ${loaded.groups}`);
  assert(loaded.keys.every((name) => name.length > 0), 'every group is named');
  assert(loaded.meta.some((text) => text.includes('只读')), 'read-only groups are labeled');
  assert(loaded.meta.some((text) => text.includes('English/简体中文')), 'editable groups name both languages');
  // The counters come from the loaded resource, including the generated groups shown read-only.
  assert.match(loaded.counts, /已加载 \d+ 个分组（可编辑 \d+ 个，生成物 \d+ 个）/);
  assert.match(loaded.counts, /缺译 \d+ 处/);
  assert.equal(loaded.note, true, 'an editable group shows no read-only note');
  assert.match(loaded.heading, /不触发生成/);
  assert.match(loaded.heading, /@icon!/);
  assert.equal(loaded.panelActive, true);
  assert.equal(loaded.panels, 1, 'shared.js keeps exactly one tool panel active');
  assert.equal(loaded.dotHidden, true, 'nothing edited yet, so no tab dot');

  // Select a small editable pair: both columns exist and the two languages are separate inputs.
  const selected = await page(() => {
    const target = [...document.querySelectorAll('#localization-root .localization-group')]
      .find((node) => node.querySelector('.localization-group-name').textContent === 'tv_game_concepts');
    target.click();
    return null;
  });
  assert.equal(selected, null);
  await ready("!!document.querySelector('#localization-root .localization-row')");
  const columns = await page(() => {
    const head = [...document.querySelectorAll('#localization-root thead th')].map((node) => node.textContent);
    const row = document.querySelector('#localization-root .localization-row');
    return {
      head,
      title: document.querySelector('#localization-root [data-title]').textContent,
      editable: [...row.querySelectorAll('td input')].length,
      languages: [...row.querySelectorAll('td[data-language]')].map((node) => node.dataset.language),
      rows: document.querySelectorAll('#localization-root .localization-row').length,
      tableCount: document.querySelector('#localization-root [data-table-count]').textContent,
      noteHidden: document.querySelector('#localization-root [data-note]').hidden,
    };
  });
  assert.deepEqual(columns.head, ['Key', 'English', '简体中文']);
  assert.equal(columns.title, 'tv_game_concepts');
  assert.equal(columns.editable, 2, 'both languages are edited as separate inputs');
  assert.deepEqual(columns.languages, ['english', 'simp_chinese']);
  assert.equal(columns.noteHidden, true);
  // The table is windowed, so the rendered rows never exceed the page size even for a large pair.
  assert(columns.rows <= 200, `windowed rows: ${columns.rows}`);
  assert.match(columns.tableCount, /显示 \d+ \/ \d+ 条/);

  // Filters and search operate on the loaded values.
  const filtered = await page(() => {
    const root = document.querySelector('#localization-root');
    const click = (label) => [...root.querySelectorAll('[data-filters] button')]
      .find((node) => node.textContent === label).click();
    click('仅缺译');
    const missingRows = root.querySelectorAll('.localization-row').length;
    click('仅已改动');
    const editedRows = root.querySelectorAll('.localization-row').length;
    click('全部');
    const allRows = root.querySelectorAll('.localization-row').length;
    const search = root.querySelector('[data-search]');
    search.value = 'zzz-not-a-key';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    const searched = root.querySelectorAll('.localization-row').length;
    search.value = '';
    search.dispatchEvent(new Event('input', { bubbles: true }));
    return { missingRows, editedRows, allRows, searched, restored: root.querySelectorAll('.localization-row').length };
  });
  assert.equal(filtered.editedRows, 0, 'nothing is edited yet');
  assert.equal(filtered.searched, 0, 'an unmatched search shows no row');
  assert.equal(filtered.restored, filtered.allRows, 'clearing the search restores the list');
  assert(filtered.allRows >= filtered.missingRows, 'the missing filter is a subset of all rows');

  // Change one zh value: the row is marked missing/edited, the preview renders, and both the in-page
  // dirty badge and the tab-bar dot appear.
  const edited = await page(() => {
    const input = document.querySelector('#localization-root .localization-row td[data-language="simp_chinese"] input');
    const key = input.closest('.localization-row').dataset.key;
    const original = input.value;
    input.value = '浏览器场景改动';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    input.dispatchEvent(new Event('focus', { bubbles: true }));
    const root = document.querySelector('#localization-root');
    return {
      key,
      original,
      rowEdited: input.closest('.localization-row').dataset.edited,
      badge: root.querySelector('[data-dirty]').textContent,
      badgeHidden: root.querySelector('[data-dirty]').classList.contains('hidden'),
      dotHidden: document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').hidden,
      dotDirty: document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').classList.contains('dirty'),
      tabDirty: document.querySelector('.tool-hub-tab-btn[data-tool="localization"]').dataset.dirty,
      preview: root.querySelector('[data-preview]').textContent,
      rendered: !!root.querySelector('[data-preview] .localization-preview-text'),
    };
  });
  assert.equal(edited.rowEdited, 'true');
  assert.equal(edited.badgeHidden, false, 'the in-page dirty badge appears');
  assert.match(edited.badge, /未保存的更改（1 个键）/);
  assert.equal(edited.dotHidden, false, 'the tab-bar dot appears');
  assert.equal(edited.dotDirty, true);
  assert.equal(edited.tabDirty, 'true', 'the shell records the tool as dirty');
  // The preview renders the value it would show in game, not the raw markup.
  assert.equal(edited.rendered, true);
  assert.match(edited.preview, /浏览器场景改动/);
  assert.match(edited.preview, /不渲染 @icon! 贴图/);

  // Saving previews against the real server (read-only), and the dialog names the edited key.
  const commitsBefore = await page(() => __probe.requests.filter((request) => request.path === '/api/resources/editor.localization/commit').length);
  await page(() => document.querySelector('#loc-save-btn').click());
  await ready("document.querySelector('#loc-preview dialog').open");
  const preview = await page(() => ({
    summary: document.querySelector('#loc-preview .diff-summary').textContent,
    body: document.querySelector('#loc-preview tbody').textContent,
    rows: document.querySelector('#loc-preview tbody').children.length,
    status: document.querySelector('#loc-status').textContent,
  }));
  assert.equal(preview.rows, 1, 'one language value changed, so one diff row');
  assert(preview.body.includes(edited.key), `the dialog names the key; got: ${preview.body}`);
  assert.match(preview.body, /浏览器场景改动/);
  assert.match(preview.body, /simp_chinese/);
  assert.match(preview.summary, /1 个本地化条目变更/);
  assert.match(preview.summary, /不触发生成/);
  assert.equal(await page(() => __probe.requests.filter((request) => request.path === '/api/resources/editor.localization/commit').length), commitsBefore,
    'the dialog is a preview only');

  // Cancelling keeps the draft; the tab dot and the badge are still there.
  await page(() => document.querySelector('#loc-preview [data-cancel]').click());
  await ready("!document.querySelector('#loc-save-btn').disabled");
  assert.equal(await page(() => document.querySelector('#localization-root .localization-row td[data-language="simp_chinese"] input').value),
    '浏览器场景改动', 'the draft survives a cancelled preview');
  assert.equal(await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').hidden), false);

  // The commit is intercepted by the harness and rejected with 409: the draft is kept and reported.
  await page(() => document.querySelector('#loc-save-btn').click());
  await ready("document.querySelector('#loc-preview dialog').open");
  await page(() => { __probe.release = null; document.querySelector('#loc-preview [data-confirm]').click(); });
  await ready('!!__probe.release');
  const bodies = await page(() => ({
    preview: __probe.requests.findLast((request) => request.path === '/api/resources/editor.localization/preview').body,
    commit: __probe.requests.findLast((request) => request.path === '/api/resources/editor.localization/commit').body,
  }));
  assert.equal(bodies.preview, bodies.commit, 'preview and commit share one frozen request body');
  const body = JSON.parse(bodies.commit);
  assert.deepEqual(body.edits, {
    'src/main_menu/localization/english/tv_game_concepts_l_english.yml': { [edited.key]: { simp_chinese: '浏览器场景改动' } },
  }, 'the edit goes through the pair english path with only the changed language');
  assert(Object.keys(body.base).length > 100, `the base covers the whole change set: ${Object.keys(body.base).length}`);
  await page(() => __probe.release());
  await ready("!document.querySelector('#loc-save-btn').disabled");
  assert.match(await page(() => document.querySelector('#loc-log').textContent), /probe source changed/);
  assert.equal(await page(() => document.querySelector('#localization-root .localization-row td[data-language="simp_chinese"] input').value),
    '浏览器场景改动', 'a rejected commit keeps the draft');
  assert.equal(await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').hidden), false);

  // A generated group is read-only and points at its data source instead of offering inputs.
  const generated = await page(() => {
    const target = [...document.querySelectorAll('#localization-root .localization-group')]
      .find((node) => node.querySelector('.localization-group-meta').textContent.includes('只读'));
    const name = target.querySelector('.localization-group-name').textContent;
    target.click();
    const root = document.querySelector('#localization-root');
    return {
      name,
      note: root.querySelector('[data-note]').textContent,
      noteHidden: root.querySelector('[data-note]').hidden,
      inputs: root.querySelectorAll('.localization-row td input').length,
      addDisabled: root.querySelector('[data-add-toggle]').disabled,
    };
  });
  assert.equal(generated.noteHidden, false, 'a read-only group shows the reason');
  assert.match(generated.note, /应改其 data 源/);
  assert.equal(generated.inputs, 0, 'a read-only group renders no editable cell');
  assert.equal(generated.addDisabled, true, 'a read-only group cannot add keys');

  // Reverting the edit clears the draft, the badge and the dot again.
  await page(() => {
    const target = [...document.querySelectorAll('#localization-root .localization-group')]
      .find((node) => node.querySelector('.localization-group-name').textContent === 'tv_game_concepts');
    target.click();
  });
  await ready("!!document.querySelector('#localization-root .localization-row')");
  const reverted = await page((key, original) => {
    const row = [...document.querySelectorAll('#localization-root .localization-row')]
      .find((node) => node.dataset.key === key);
    const input = row.querySelector('td[data-language="simp_chinese"] input');
    input.value = original;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    return { key: row.dataset.key, value: input.value, edited: row.dataset.edited };
  }, edited.key, edited.original);
  assert.equal(reverted.key, edited.key);
  assert.equal(reverted.edited, 'false', 'restoring the loaded value drops the edit');
  await ready("document.querySelector('#localization-root [data-dirty]').classList.contains('hidden')");
  assert.equal(await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="localization"] .tool-hub-tab-dot').hidden), true,
    'reverting the only edit clears the tab dot');
  assert.equal(await page(() => document.querySelector('#loc-save-btn').disabled), true, 'nothing left to save');
  assert.deepEqual(await page(() => window.__toolShell.dirtyTools()), []);
  console.log('Localization acceptance passed: real read-only resource with grouped EN/ZH columns, windowed rows, filters/search, in-page badge and tab dot on edit, real read-only preview naming the edited key with one frozen request body, 409 commit keeps the draft, generated groups read-only with their data source, revert clears the dot.');
};
