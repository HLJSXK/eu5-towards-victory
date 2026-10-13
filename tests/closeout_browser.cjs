// Called by resource_state_browser.cjs: live DOM and previews, simulated source changes and commits.
const assert = require('node:assert/strict');

module.exports = async function closeoutAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate('(' + fn.toString() + ')(...' + JSON.stringify(args) + ')');
  const idle = "document.querySelector('.tool-wonder-localization').dataset.busy === 'false'";

  // Remaining scenarios from the retired Playwright script: draft restoration must retain both option catalogs.
  await page(async () => {
    window.__closeout = { resource: await (await fetch('/api/resources/editor.wonder')).json() };
    const test = __closeout;
    test.wonder = test.resource.draft.wonders.find(w => w.key === 'unique_trinity_lavra');
    test.detail = await (await fetch('/api/wonder-localization/wonders/' + test.wonder.id)).json();
    test.cost = await (await fetch('/api/resources/editor.cost_reward')).json();
    document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click();
    document.querySelectorAll('#wonder-kind-tabs button')[1].click();
    document.querySelector('[data-wonder-key="unique_trinity_lavra"]').click();
  });
  await ready(idle);
  await page(() => [...document.querySelectorAll('#language-tabs button')].find(b => b.textContent.includes('机制')).click());
  const catalogState = () => {
    const shell = type => document.querySelector('[data-field-type="' + type + '"]').closest('.structured-field');
    const ritual = shell('unique_ritual_editor');
    const input = ritual.querySelector('.scalar-grid label.scalar-field input');
    const count = select => {
      select.querySelector('.option-open-button').click();
      const result = select.querySelectorAll('.option-item').length;
      select.querySelector('.option-open-button').click();
      return result;
    };
    return { value: input.value,
      modes: count(ritual.querySelectorAll('.scalar-grid label.scalar-field')[1].querySelector('.option-combobox')),
      costs: count(shell('unique_ceremony_editor').querySelector('[data-row-list="stage-cost"] .option-combobox')),
      calls: __probe.requests.filter(r => r.path === '/api/wonder-localization/catalog').length };
  };
  const original = await page(catalogState);
  assert(original.modes > 1 && original.costs > 1);
  await page(value => {
    const input = document.querySelector('[data-field-type="unique_ritual_editor"]').closest('.structured-field')
      .querySelector('.scalar-grid label.scalar-field input');
    input.value = value + '_closeout'; input.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('#wonder-list button:not(.active)').click();
  }, original.value);
  await ready(idle);
  await page(() => document.querySelector('[data-wonder-key="unique_trinity_lavra"]').click());
  await ready(idle);
  const restored = await page(catalogState);
  assert.deepEqual(restored, { ...original, value: original.value + '_closeout' });
  await page(value => {
    const input = document.querySelector('[data-field-type="unique_ritual_editor"]').closest('.structured-field')
      .querySelector('.scalar-grid label.scalar-field input');
    input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
  }, original.value);
  assert(await page(() => document.querySelector('#dirty-badge').classList.contains('hidden')));

  // Prepare the simulated external source revision; previews still use the real read-only backend.
  await page(() => {
    const test = __closeout;
    test.realBase = Object.fromEntries(test.resource.change_set.base.map(s => [s.path, s.sha256]));
    test.revision = 0; test.active = false; test.failure = false; test.conflict = false; test.previews = [];
    __probe.intercept = async (path, live, options) => {
      if (path === '/api/resources/editor.cost_reward/commit') {
        test.active = true; test.revision++;
        return Response.json({ ...test.cost, written_paths: ['data/cost_reward_units.yaml', 'data/unique_wonders.yaml'] });
      }
      if (!test.active) return null;
      const resource = structuredClone(test.resource);
      resource.change_set.base.find(s => s.path === 'data/unique_wonders.yaml').sha256 = 'external-' + test.revision;
      if (path === '/api/resources/editor.wonder') {
        if (test.failure) return Response.json({ detail: 'refresh probe failed' }, { status: 503 });
        return Response.json(resource);
      }
      if (path === '/api/wonder-localization/wonders/' + test.wonder.id) {
        const detail = structuredClone(test.detail);
        if (test.conflict) {
          const key = 'tv_wonder_' + test.wonder.key;
          for (const section of detail.languages.english.sections) for (const field of section.fields) {
            if (field.key === key) field.original_value = field.value = 'External original name';
          }
          detail.summary.name_en = detail.meta.name_en = 'External original name';
        }
        return Response.json(detail);
      }
      if (path === '/api/resources/editor.wonder/preview') {
        const body = JSON.parse(options.body);
        test.previews.push(body);
        if (body.base['data/unique_wonders.yaml'] !== 'external-' + test.revision)
          return Response.json({ detail: 'stale Wonder base', code: 'resource_changed' }, { status: 409 });
        // The browser fixture does not write real files. Substitute the live base only for the read-only semantic preview.
        return live({ ...options, body: JSON.stringify({ ...body, base: test.realBase }) });
      }
      if (path === '/api/resources/editor.wonder/commit') {
        return Response.json({ ...resource, wonders: resource.draft.wonders, wonder: test.detail,
          operation: { status: 'succeeded' }, operation_id: 'closeout-wonder', log_text: 'closeout saved' });
      }
      return null;
    };
  });

  const editWonder = value => page(value => {
    const input = document.querySelector('#wonder-name-editors [data-language="english"]');
    input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
  const commitCost = async () => {
    await page(() => {
      document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').click();
      const input = document.querySelector('#panels input[type="number"]');
      input.value = String(Number(input.value) + 0.01); input.dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelector('#cr-save-btn').click();
    });
    await ready("document.querySelector('#cr-preview dialog').open");
    await page(() => document.querySelector('#cr-preview [data-confirm]').click());
    await ready("!document.querySelector('#cr-save-btn').disabled");
    await ready(idle);
    await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click());
  };
  for (const conflict of [false, true]) {
    await page(conflict => { __closeout.conflict = conflict; }, conflict);
    await editWonder('Preserved closeout draft');
    await commitCost();
    assert.equal(await page(() => document.querySelector('#wonder-name-editors [data-language="english"]').value), 'Preserved closeout draft');
    assert(await page(() => !document.querySelector('#dirty-badge').classList.contains('hidden')));
    if (conflict) {
      const log = await page(() => document.querySelector('#log-output').textContent);
      assert(log.includes('External original name') && log.includes('tv_wonder_unique_trinity_lavra'));
      assert(log.includes('\u539f\u503c\u5df2\u5728\u5176\u4ed6\u7f16\u8f91\u5668\u4e2d\u6539\u53d8'));
    }
    await page(() => document.querySelector('#save-button').click());
    await ready("document.querySelector('#wonder-preview dialog').open");
    const body = await page(() => __closeout.previews.at(-1));
    assert.equal(body.wonders.length, 1);
    assert.deepEqual(body.wonders[0].mechanics, {});
    assert.deepEqual(body.wonders[0].values, { english: { tv_wonder_unique_trinity_lavra: 'Preserved closeout draft' }, simp_chinese: {} });
    assert.equal(await page(() => document.querySelectorAll('#wonder-preview tbody tr').length), 2); // one field and one file hash
    await page(() => document.querySelector('#wonder-preview [data-confirm]').click());
    await ready(idle);
    assert(await page(() => document.querySelector('#dirty-badge').classList.contains('hidden')));
    assert(await page(() => __probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/preview').body
      === __probe.requests.findLast(r => r.path === '/api/resources/editor.wonder/commit').body));
  }
  // Reverse direction: a Wonder commit rewrites unique_wonders.yaml while cost/reward holds a draft.
  await page(() => {
    const test = __closeout, previous = __probe.intercept;
    test.costRevision = 0; test.costPreviews = [];
    test.realCostBase = Object.fromEntries(test.cost.change_set.base.map(s => [s.path, s.sha256]));
    __probe.intercept = async (path, live, options) => {
      if (path === '/api/resources/editor.cost_reward' && test.costRevision) {
        const resource = structuredClone(test.cost);
        resource.change_set.base.find(s => s.path === 'data/unique_wonders.yaml').sha256 = 'wonder-' + test.costRevision;
        return Response.json(resource);
      }
      if (path === '/api/resources/editor.cost_reward/preview') {
        const body = JSON.parse(options.body);
        test.costPreviews.push(body);
        const expected = test.costRevision ? 'wonder-' + test.costRevision : test.realCostBase['data/unique_wonders.yaml'];
        if (body.base['data/unique_wonders.yaml'] !== expected)
          return Response.json({ detail: 'stale cost/reward base', code: 'resource_changed' }, { status: 409 });
        return live({ ...options, body: JSON.stringify({ ...body, base: test.realCostBase }) });
      }
      if (path === '/api/resources/editor.wonder/commit') {
        test.costRevision++;
        const payload = await (await previous(path, live, options)).json();
        return Response.json({ ...payload, written_paths: ['data/unique_wonders.yaml'] });
      }
      return previous(path, live, options);
    };
    document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').click();
    const input = document.querySelector('#panels input[type="number"]');
    test.costDraft = String(Number(input.value) + 0.5);
    input.value = test.costDraft; input.dispatchEvent(new Event('input', { bubbles: true }));
    document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click();
  });
  await editWonder('Wonder save during cost draft');
  await page(() => document.querySelector('#save-button').click());
  await ready("document.querySelector('#wonder-preview dialog').open");
  await page(() => document.querySelector('#wonder-preview [data-confirm]').click());
  await ready(idle);
  await ready("!document.querySelector('#cr-save-btn').disabled && /已同步/.test(document.querySelector('#cr-status').textContent)");
  assert.equal(await page(() => document.querySelector('#panels input[type="number"]').value), await page(() => __closeout.costDraft));
  await page(() => {
    document.querySelector('.tool-hub-tab-btn[data-tool="cost-reward"]').click();
    document.querySelector('#cr-save-btn').click();
  });
  await ready("document.querySelector('#cr-preview dialog').open");
  const costBody = await page(() => __closeout.costPreviews.at(-1));
  assert.equal(costBody.base['data/unique_wonders.yaml'], 'wonder-1');
  assert.equal(Object.keys(costBody.edits).length, 1);
  await page(() => document.querySelector('#cr-preview [data-cancel]').click());
  await ready("!document.querySelector('#cr-save-btn').disabled");
  await page(() => {
    document.querySelector('#cr-reload-btn').click();
    document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click();
  });
  await ready("!document.querySelector('#cr-save-btn').disabled");

  await editWonder('Draft survives refresh failure');
  await page(() => { __closeout.failure = true; });
  await commitCost();
  assert.equal(await page(() => document.querySelector('#wonder-name-editors [data-language="english"]').value), 'Draft survives refresh failure');
  assert.match(await page(() => document.querySelector('#status-badge').textContent), /refresh probe failed/);
  assert.match(await page(() => document.querySelector('#log-output').textContent), /refresh probe failed/);
  await page(() => { __probe.intercept = null; document.querySelector('#reload-button').click(); });
  await ready(idle);
  console.log('Closeout Chrome acceptance passed: cached options survive draft switching; cost commit refreshes Wonder base, preserves drafts and reports conflicts/failures; preview contains only Wonder drafts; Wonder commits refresh cost/reward base with its draft kept.');
};
