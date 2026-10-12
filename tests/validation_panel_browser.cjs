// WP-05: the validation panel after a save. Mounted from resource_state_browser.cjs. The preview is the real
// read-only endpoint; the commit and /api/validate are intercepted, so no file is written and validate.py is not run.
const assert = require('node:assert/strict');

module.exports = async function validationPanelAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate('(' + fn.toString() + ')(...' + JSON.stringify(args) + ')');
  const pass = { pass: true, errors: [], warnings: [], files_checked: 4, command: [], duration_ms: 1500, fixed: [] };
  const failing = { ...pass, pass: false, errors: [
    { rule: 'loc', message: '[LOC] duplicate key tv_wp05_probe', file: 'src/main_menu/localization/english/wp05_l_english.yml', line: 7 },
    { rule: 'loc', message: '[LOC] missing simp_chinese for tv_wp05_probe', file: 'src/main_menu/localization/english/wp05_l_english.yml' },
    { rule: 'syntax', message: 'unbalanced braces <wp05>' },
  ], warnings: [] };

  assert.equal(await page(() => document.querySelector('#validation-panel').dataset.state), 'idle');
  assert(await page(() => document.querySelector('#validation-panel').getClientRects().length > 0), 'panel visible');

  await page((pass) => {
    window.__wp05 = { response: pass, validations: [], commits: 0 };
    __probe.intercept = async (path, live, options) => {
      if (path === '/api/validate') {
        __wp05.validations.push(JSON.parse(options.body));
        return Response.json(__wp05.response);
      }
      if (path === '/api/resources/editor.victory_tree/commit') {
        __wp05.commits++;
        // The live read-only resource GET stands in for the committed state.
        const resource = await (await fetch('/api/resources/editor.victory_tree')).json();
        return Response.json({ ...resource, operation_id: 'wp05-commit', operation: { status: 'succeeded' } });
      }
      return null;
    };
  }, pass);

  const save = async () => {
    await page(() => {
      document.querySelector('.tool-hub-tab-btn[data-tool="victory-tree"]').click();
      const input = document.querySelector('#nodeList input');
      input.value = String(Number(input.value) === 0.25 ? 0.26 : 0.25);
      input.dispatchEvent(new Event('change', { bubbles: true }));
      document.querySelector('#vt-save-btn').click();
    });
    await ready("document.querySelector('#vt-preview dialog').open");
    await page(() => document.querySelector('#vt-preview [data-confirm]').click());
    await ready("!document.querySelector('#vt-save-btn').disabled");
  };

  // Pass state: one save triggers exactly one changed:true validation.
  await save();
  await ready("['pass', 'errors'].includes(document.querySelector('#validation-panel').dataset.state)");
  const passed = await page(() => ({
    state: document.querySelector('#validation-panel').dataset.state,
    status: document.querySelector('#validation-panel .validation-status').textContent,
    hidden: document.querySelector('#validation-panel .validation-results').hidden,
    validations: __wp05.validations, commits: __wp05.commits,
    previews: __probe.requests.filter(r => r.path === '/api/resources/editor.victory_tree/preview').length,
  }));
  assert.equal(passed.commits, 1);
  assert.deepEqual(passed.validations, [{ changed: true }]);
  assert.equal(passed.state, 'pass');
  assert.equal(passed.status, '校验通过（检查 4 个文件，用时 1.5 秒）');
  assert.equal(passed.hidden, true);

  // Errors state from a second save: red panel, rule groups and one item per error.
  await page((failing) => { __wp05.response = failing; }, failing);
  await save();
  await ready("document.querySelector('#validation-panel').dataset.state === 'errors'");
  const failed = await page(() => {
    const root = document.querySelector('#validation-panel');
    return {
      status: root.querySelector('.validation-status').textContent,
      statusColor: getComputedStyle(root.querySelector('.validation-status')).color,
      border: getComputedStyle(root).borderTopColor,
      items: [...root.querySelectorAll('.validation-item[data-severity="error"]')].map(li => li.textContent),
      groups: [...root.querySelectorAll('.validation-group h4')].map(h => h.textContent),
      files: [...root.querySelectorAll('.validation-file')].map(code => code.textContent),
      injected: !!root.querySelector('wp05'),
      visible: root.querySelector('.validation-results').getClientRects().length > 0,
      validations: __wp05.validations.length,
    };
  });
  assert.equal(failed.validations, 2);
  assert.equal(failed.status, '校验失败：3 条错误，0 条警告（检查 4 个文件，用时 1.5 秒）');
  assert.equal(failed.statusColor, 'rgb(255, 123, 102)');
  assert.equal(failed.border, 'rgb(209, 75, 54)');
  assert.equal(failed.items.length, 3);
  assert.deepEqual(failed.groups, ['错误 · loc 2', '错误 · syntax 1']);
  assert.deepEqual(failed.files, ['src/main_menu/localization/english/wp05_l_english.yml:7', 'src/main_menu/localization/english/wp05_l_english.yml']);
  assert(failed.items[2].includes('unbalanced braces <wp05>') && !failed.injected, 'message rendered as text');
  assert(failed.visible);

  // Manual button reruns the same request and returns to pass.
  await page((pass) => { __wp05.response = pass; document.querySelector('#validation-panel [data-validate]').click(); }, pass);
  await ready("document.querySelector('#validation-panel').dataset.state === 'pass'");
  assert.deepEqual(await page(() => __wp05.validations.at(-1)), { changed: true });

  await page(() => { __probe.intercept = null; delete window.__wp05; document.querySelector('#vt-reload-btn').click(); });
  await ready("!document.querySelector('#vt-save-btn').disabled");
  console.log('Validation panel Chrome acceptance passed: a saved commit triggers one changed:true validation; pass and red errors states render grouped items; manual rerun works; no file written.');
};
