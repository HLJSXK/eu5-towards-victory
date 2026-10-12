// WP-09: generator tab. Mounted from resource_state_browser.cjs. The catalogue comes from the real
// read-only GET /api/generators; every POST /api/generators/run is intercepted, so this scenario
// never executes a generator or writes a business file (real runs are covered by
// tests/test_generator_runs.py in a temporary repository copy). The absence of a new persisted
// `generator_run` operation proves nothing reached the server.
const assert = require('node:assert/strict');

const escape = (value) => value.replace(/[.\\/+]/g, '\\$&');

module.exports = async function generatorsAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate('(' + fn.toString() + ')(...' + JSON.stringify(args) + ')');
  const generatorRuns = () => page(() => fetch('/api/operations?kind=generator_run&limit=100')
    .then((response) => response.json()).then((payload) => payload.operations.length));
  const before = await generatorRuns();

  await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="generators"]').click());
  await ready("!!document.querySelector('#generators-root .generator-group')");

  // The real catalogue: grouped by root/domain, with the order note and the disabled run button.
  const loaded = await page(() => ({
    groups: [...document.querySelectorAll('#generators-root .generator-group-title')].map((node) => node.textContent),
    scripts: document.querySelectorAll('#generators-root .generator-script').length,
    counts: [...document.querySelectorAll('#generators-root .generator-group-counts')].map((node) => node.textContent),
    note: document.querySelector('#generators-root .generators-note').textContent,
    plan: document.querySelector('#generators-root [data-plan]').textContent,
    runDisabled: document.querySelector('#generators-root [data-run]').disabled,
    heading: document.querySelector('.tool-generators .subtitle').textContent,
    status: document.querySelector('#gen-status').textContent,
    active: document.querySelector('.tool-generators').classList.contains('active'),
    others: [...document.querySelectorAll('.tool-panel.active')].length,
  }));
  assert(loaded.groups.length > 10, `groups rendered: ${loaded.groups.length}`);
  assert(loaded.groups.every((title) => title.includes(' / ')), 'root / domain titles');
  assert.equal(new Set(loaded.groups).size, loaded.groups.length, 'one section per root/domain');
  assert(loaded.scripts > loaded.groups.length, `more scripts (${loaded.scripts}) than groups (${loaded.groups.length})`);
  assert(loaded.counts.every((text) => /^\d+ 个脚本$/.test(text)), 'group counts');
  assert.match(loaded.note, /顺序执行，无依赖图/);
  assert.match(loaded.note, /中途失败即停止/);
  assert.match(loaded.plan, /尚未选择脚本/);
  assert.match(loaded.heading, /顺序执行，没有依赖图/);
  assert.match(loaded.heading, /文件级检查/);
  assert.equal(loaded.runDisabled, true);
  assert.match(loaded.status, /已加载 \d+ 个已登记生成器/);
  // The tab is a separate tool panel; shared.js keeps exactly one panel active.
  assert(loaded.active);
  assert.equal(loaded.others, 1);

  // Selection state: one script per group, execution order follows the click order.
  const picked = await page(() => {
    const rows = [...document.querySelectorAll('#generators-root .generator-row')];
    window.__gen = { runs: [], mode: 'gate', release: null, payload: null, status: 200, groupAdded: 0 };
    const pick = (index) => {
      const box = rows[index].querySelector('input[type="checkbox"]');
      box.checked = true;
      box.dispatchEvent(new Event('change', { bubbles: true }));
      return rows[index].querySelector('.generator-script').textContent;
    };
    // The first row belongs to the first root/domain group, the last row to the last one.
    const chosen = [pick(rows.length - 1), pick(0)];
    const groupToggles = [...document.querySelectorAll('#generators-root .generator-group-head input')];
    groupToggles[1].checked = true;
    groupToggles[1].dispatchEvent(new Event('change', { bubbles: true }));
    window.__gen.groupAdded = [...document.querySelectorAll('#generators-root .generator-row input')]
      .filter((box) => box.checked).length;
    groupToggles[1].checked = false;
    groupToggles[1].dispatchEvent(new Event('change', { bubbles: true }));
    return chosen;
  });
  const plan = await page(() => document.querySelector('#generators-root [data-plan]').textContent);
  assert.equal(plan, `执行顺序：1. ${picked[0]} → 2. ${picked[1]}`);
  assert.equal(await page(() => document.querySelector('#generators-root [data-run]').disabled), false, 'run enabled after selection');
  assert(await page(() => window.__gen.groupAdded > 2), 'the group toggle selected a whole group at once');
  assert.equal(await page(() => [...document.querySelectorAll('#generators-root .generator-row input')].filter((box) => box.checked).length), 2,
    'clearing the group toggle left exactly the two explicit picks');

  await page(() => {
    __probe.intercept = async (path, live, options) => {
      if (path !== '/api/generators/run') return null;
      __gen.runs.push({ method: options.method, body: JSON.parse(options.body) });
      if (__gen.mode === 'gate') await new Promise((resolve) => { __gen.release = resolve; });
      return Response.json(__gen.payload, { status: __gen.status });
    };
  });

  // In-flight state: one request in the user's order, every control locked, no second submission.
  await page(() => document.querySelector('#generators-root [data-run]').click());
  await ready("window.__gen.release !== null");
  const running = await page(() => ({
    running: document.querySelector('#generators-root').dataset.running,
    plan: document.querySelector('#generators-root [data-plan]').textContent,
    status: document.querySelector('#gen-status').textContent,
    run: document.querySelector('#generators-root [data-run]').disabled,
    reload: document.querySelector('#generators-root [data-reload]').disabled,
    dryRun: document.querySelector('#generators-root [data-dry-run]').disabled,
    boxes: [...document.querySelectorAll('#generators-root .generator-row input')].every((box) => box.disabled),
    groupBoxes: [...document.querySelectorAll('#generators-root .generator-group-head input')].every((box) => box.disabled),
    runs: __gen.runs.length,
  }));
  assert.equal(running.running, 'true');
  assert.match(running.plan, /正在按顺序执行 2 个脚本/);
  assert.match(running.status, /正在按顺序执行 2 个脚本/);
  assert(running.run && running.reload && running.dryRun, 'actions disabled while running');
  assert(running.boxes && running.groupBoxes, 'checkboxes disabled while running');
  assert.equal(running.runs, 1);
  assert.deepEqual(await page(() => __gen.runs[0]), { method: 'POST', body: { scripts: picked, dry_run: false } });
  // Clicking again while the run is in flight must not queue a second request.
  await page(() => document.querySelector('#generators-root [data-run]').click());
  assert.equal(await page(() => __gen.runs.length), 1);

  // Precheck rejection: 400 with `detail` only. The panel releases and reports the conflict verbatim.
  await page(() => {
    __gen.status = 400;
    __gen.payload = { detail: 'Intersecting outputs: src/a.txt (scripts/gen_x.py, scripts/gen_y.py; src/a.txt)' };
    __gen.release();
  });
  await ready("document.querySelector('#generators-root').dataset.running === 'false'");
  const rejected = await page(() => ({
    kind: document.querySelector('#gen-status').dataset.kind,
    status: document.querySelector('#gen-status').textContent,
    color: getComputedStyle(document.querySelector('#gen-status')).color,
    log: document.querySelector('#gen-log').textContent,
    run: document.querySelector('#generators-root [data-run]').disabled,
    boxes: [...document.querySelectorAll('#generators-root .generator-row input')].some((box) => box.disabled),
  }));
  assert.equal(rejected.kind, 'error');
  assert.match(rejected.status, /Intersecting outputs: src\/a\.txt/);
  assert.match(rejected.log, /\[error\] Intersecting outputs: src\/a\.txt/);
  assert.equal(rejected.color, 'rgb(209, 75, 54)', 'shared .job-status error color');
  assert.equal(rejected.run, false, 'the same selection can be retried');
  assert.equal(rejected.boxes, false);

  // Execution failure: 500 with `detail` plus the full report fields. api.js keeps only its documented
  // ApiError fields, so the panel reports the detail; the error response's step report is not reachable.
  await page((first) => {
    __gen.mode = 'direct';
    __gen.status = 500;
    __gen.payload = { detail: `${first} exited with 1`, operation_id: 'gen-chrome-fail',
      operation: { id: 'gen-chrome-fail', status: 'failed', kind: 'generator_run', resource_ids: [], events: [], error: `${first} exited with 1` },
      results: [{ script: first, status: 'failed', exit_code: 1, duration_ms: 40, output_tail: 'boom\n' }],
      artifacts: [], rollback: { status: 'not_needed', errors: [] } };
    document.querySelector('#generators-root [data-run]').click();
  }, picked[0]);
  await ready("document.querySelector('#gen-status').dataset.kind === 'error'");
  const failed = await page(() => ({
    status: document.querySelector('#gen-status').textContent,
    log: document.querySelector('#gen-log').textContent,
    running: document.querySelector('#generators-root').dataset.running,
    runDisabled: document.querySelector('#generators-root [data-run]').disabled,
    reloadDisabled: document.querySelector('#generators-root [data-reload]').disabled,
  }));
  assert.match(failed.status, new RegExp(`${escape(picked[0])} exited with 1`));
  assert.match(failed.log, /\[error\]/);
  assert.equal(failed.running, 'false', 'the panel is not stuck');
  assert.equal(failed.runDisabled, false);
  assert.equal(failed.reloadDisabled, false);

  // dry_run success: skipped steps, no artifacts, and the explicit "nothing written" statement.
  await page(() => {
    __gen.status = 200;
    __gen.payload = { operation_id: 'gen-chrome-dry',
      operation: { id: 'gen-chrome-dry', operation_id: 'gen-chrome-dry', kind: 'generator_run', status: 'succeeded',
        resource_ids: ['editor.localization'], events: [], error: null },
      results: __gen.runs[0].body.scripts.map((script) => ({ script, status: 'skipped', exit_code: null, duration_ms: 0, output_tail: '' })),
      artifacts: [], rollback: { status: 'not_needed', errors: [] } };
    const dry = document.querySelector('#generators-root [data-dry-run]');
    dry.checked = true;
    dry.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#generators-root [data-run]').click();
  });
  await ready("document.querySelector('#gen-log').textContent.includes('已跳过')");
  const dryRun = await page(() => ({
    runs: __gen.runs.length,
    body: __gen.runs.at(-1).body,
    status: document.querySelector('#gen-status').textContent,
    log: document.querySelector('#gen-log').textContent,
    filesHidden: document.querySelector('#gen-files').hidden,
    fileReport: document.querySelector('#gen-file-report').textContent,
  }));
  assert.equal(dryRun.runs, 3);
  assert.deepEqual(dryRun.body, { scripts: picked, dry_run: true });
  assert.match(dryRun.log, /操作 ID: gen-chrome-dry/);
  assert.match(dryRun.log, new RegExp(`${escape(picked[0])}: 已跳过[\\s\\S]*恢复结果: 无需恢复`));
  assert.match(dryRun.status, /dry_run：未执行脚本、未写入文件/);
  assert.equal(dryRun.filesHidden, false, 'the shared file report is shown');
  assert.equal(dryRun.fileReport, '资源: editor.localization');

  // A successful run reports steps and artifacts through the same shared renderer, including a
  // registered output the run deleted.
  await page(() => {
    const [first, second] = __gen.runs[0].body.scripts;
    __gen.payload = { operation_id: 'gen-chrome-run',
      operation: { id: 'gen-chrome-run', operation_id: 'gen-chrome-run', kind: 'generator_run', status: 'succeeded',
        resource_ids: ['editor.localization'], events: [], error: null },
      results: [{ script: first, status: 'succeeded', exit_code: 0, duration_ms: 8123, output_tail: 'wrote 7 files\n' },
        { script: second, status: 'succeeded', exit_code: 0, duration_ms: 40, output_tail: '' }],
      artifacts: [{ path: 'data/index/icons.txt', size: 120, sha256: 'ab'.repeat(32), changed: true },
        { path: 'data/index/old.txt', size: 0, sha256: 'missing', changed: true }],
      rollback: { status: 'not_needed', errors: [] } };
    const dry = document.querySelector('#generators-root [data-dry-run]');
    dry.checked = false;
    dry.dispatchEvent(new Event('change', { bubbles: true }));
    document.querySelector('#generators-root [data-run]').click();
  });
  await ready("document.querySelector('#gen-log').textContent.includes('data/index/old.txt')");
  const reported = await page(() => ({
    log: document.querySelector('#gen-log').textContent,
    status: document.querySelector('#gen-status').textContent,
    fileReport: document.querySelector('#gen-file-report').textContent,
    injected: !!document.querySelector('#gen-log img'),
  }));
  assert.match(reported.log, new RegExp(`${escape(picked[0])}: 已完成 \\(退出码 0\\) \\/ 8\\.123s`));
  assert.match(reported.log, new RegExp(`${escape(picked[1])}: 已完成 \\(退出码 0\\) \\/ 0\\.04s`));
  assert.match(reported.log, /data\/index\/icons\.txt: 已变化/);
  assert.match(reported.log, /data\/index\/old\.txt: 已删除/);
  assert.match(reported.log, new RegExp(`\\[${escape(picked[0])}\\]\\nwrote 7 files`));
  assert.match(reported.log, /恢复结果: 无需恢复/);
  assert.match(reported.status, /2 个脚本；已完成；2\/2 个产物有变化/);
  assert.equal(reported.injected, false, 'the report renders as text');
  // The probe's artifact paths are not the picked scripts' registered outputs, so the shared file
  // report lists the resource lock and marks every declared output as not generated.
  assert.match(reported.fileReport, /资源: editor\.localization[\s\S]*输出:/);

  // Nothing reached the server: every run was intercepted here, so no generator executed.
  assert.equal(await page(() => __probe.requests.filter((request) => request.path === '/api/generators/run').length), 4,
    'the page issued four runs');
  assert.equal(await page(() => __gen.runs.length), 4);
  assert.equal(await generatorRuns(), before, 'no generator_run operation was persisted');

  // Reload goes through the real read-only catalogue and keeps the panel usable.
  await page(() => {
    __probe.intercept = null;
    delete window.__gen;
    document.querySelector('#generators-root [data-reload]').click();
  });
  await ready("document.querySelector('#gen-status').textContent.includes('已加载')");
  assert.equal(await page(() => document.querySelector('#generators-root [data-reload]').disabled), false);
  assert.match(await page(() => document.querySelector('#gen-status').textContent), /已加载 \d+ 个已登记生成器/);
  assert.match(await page(() => document.querySelector('#generators-root [data-plan]').textContent), /执行顺序/);
  console.log('Generators Chrome acceptance passed: real read-only catalogue grouped by root/domain with the sequential/no-DAG note, click-order selection and group toggle, locked in-flight state with a single request, 400 precheck and 500 execution error states, dry_run skipped-step report and a succeeded run reporting changed/deleted artifacts through the shared renderers; no generator_run operation was persisted.');
};
