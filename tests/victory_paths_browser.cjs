const assert = require('node:assert/strict');

module.exports = async function victoryPathsAcceptance({ evaluate, ready }) {
  const page = (callback, ...args) => evaluate('(' + callback.toString() + ')(...' + JSON.stringify(args) + ')');
  const url = '/api/resources/editor.victory_paths';
  await page((url) => {
    window.__vpPreviousIntercept = __probe.intercept;
    window.__vpProbe = { requests: [], resource: null, mode: 'ready', freshSource: false };
    __probe.intercept = async (path, live, options) => {
      if (!path.startsWith(url)) return window.__vpPreviousIntercept?.(path, live, options);
      const probe = __vpProbe;
      probe.requests.push({ path, body: options.body, method: options.method || 'GET' });
      if (path === url && (!options.method || options.method === 'GET')) {
        const resource = await (await live()).json();
        if (probe.freshSource) {
          resource.sources[0].sha256 = 'a'.repeat(64);
          resource.document.paths[0].milestones[0].threshold += 1;
        }
        if (probe.mode === 'missing') resource.references.rewards[0].resolved = false;
        probe.resource = structuredClone(resource);
        return Response.json(resource);
      }
      if (options.method !== 'POST') throw new Error('Unexpected victory paths request');
      const body = JSON.parse(options.body);
      const resource = probe.resource;
      const common = { references: resource.references, generation: { ...resource.generation, required: true } };
      if (path === url + '/validate') return Response.json({ ...common, valid: true, errors: [], warnings: [] });
      if (path === url + '/preview') {
        if (probe.mode === 'conflict') {
          probe.freshSource = true;
          return Response.json({ code: 'resource_changed', detail: 'WP-11 intercepted conflict' }, { status: 409 });
        }
        return Response.json({ ...common, ready: true, validation: { errors: [], warnings: [] },
          diff: { fields: [{ path: resource.sources[0].path, field: 'paths[0].milestones[0].threshold',
            before: resource.document.paths[0].milestones[0].threshold, after: body.document.paths[0].milestones[0].threshold }],
            sources: resource.sources.map((item, index) => ({ path: item.path, changed: index === 0,
              before_sha256: item.sha256, after_sha256: index === 0 ? 'b'.repeat(64) : item.sha256 })) },
          written_paths: [resource.sources[0].path] });
      }
      if (path === url + '/commit') return Response.json({ code: 'resource_changed', detail: 'WP-11 intercepted commit' }, { status: 409 });
      throw new Error('Unexpected victory paths endpoint: ' + path);
    };
  }, url);
  try {
    assert.equal(await page((url) => __probe.requests.filter((item) => item.path === url).length, url), 0, 'resource loads lazily');
    await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="victory-paths"]').click());
    await ready("!!document.querySelector('#victory-paths-root [data-group=\"milestone-1\"] input[data-field$=\".threshold\"]')");
    const loaded = await page(() => {
      const root = document.querySelector('#victory-paths-root');
      const tabs = [...document.querySelectorAll('.tool-hub-tab-btn')];
      return { pathCount: root.querySelectorAll('[data-paths] button').length,
        expectedPaths: __vpProbe.resource.document.paths.length,
        groups: [...root.querySelectorAll('[data-group]')].map((item) => item.dataset.group),
        slots: root.querySelector('.victory-paths-slots').children.length,
        note: root.querySelector('.victory-paths-slot-note').textContent,
        plan: root.querySelector('[data-plan]').textContent,
        generators: __vpProbe.resource.generation.generators.length,
        outputs: __vpProbe.resource.generation.outputs.length,
        editableReferences: root.querySelectorAll('[data-references] input, [data-references] textarea').length,
        tabCount: tabs.length, usableTabs: tabs.every((tab) => {
          const rect = tab.getBoundingClientRect();
          return rect.width > 0 && rect.height > 0 && rect.left >= 0 && rect.right <= innerWidth;
        }), base: root.querySelector('[data-sources]').textContent,
        liveSources: __vpProbe.resource.sources.map(({ path, sha256 }) => ({ path, sha256 })) };
    });
    assert.equal(loaded.pathCount, loaded.expectedPaths);
    assert(loaded.groups.includes('shared') && loaded.groups.includes('task-settings') && loaded.groups.includes('national-special'));
    assert.equal(loaded.slots, 3);
    assert.match(loaded.note, /不写入 slot 字段/);
    assert.match(loaded.plan, new RegExp(`${loaded.generators} 个生成器；${loaded.outputs} 个只读产物`));
    assert.equal(loaded.editableReferences, 0);
    assert.equal(loaded.tabCount, 9);
    assert.equal(loaded.usableTabs, true, 'all nine tab buttons remain within the viewport');

    const edit = await page(() => {
      const input = document.querySelector('#victory-paths-root [data-group="milestone-1"] input[data-field$=".threshold"]');
      const original = input.value, value = String(Number(original) + 7);
      input.value = value; input.dispatchEvent(new Event('input', { bubbles: true }));
      return { field: input.dataset.field, original, value,
        dot: document.querySelector('.tool-hub-tab-btn[data-tool="victory-paths"] [data-dot]').hidden,
        dirty: document.querySelector('#victory-paths-root [data-dirty]').textContent };
    });
    assert.equal(edit.dot, false);
    assert.match(edit.dirty, /1 个字段/);
    await page(() => document.querySelector('#vp-save-btn').click());
    await ready("document.querySelector('#vp-preview dialog').open");
    const preview = await page(() => ({
      body: document.querySelector('#vp-preview tbody').textContent,
      summary: document.querySelector('#vp-preview .diff-summary').textContent,
      frozen: [...document.querySelectorAll('#victory-paths-root input, #victory-paths-root textarea, #victory-paths-root button')]
        .every((item) => item.disabled),
      commitCount: __vpProbe.requests.filter((item) => item.path.endsWith('/commit')).length,
      requests: __vpProbe.requests.filter((item) => item.body),
    }));
    assert.match(preview.body, /paths\[0\]\.milestones\[0\]\.threshold/);
    assert(preview.body.includes(edit.value));
    assert.match(preview.summary, /1 个字段变更；1 个源文件/);
    assert.match(preview.summary, new RegExp(`${loaded.generators} 个生成步骤`));
    assert.equal(preview.frozen, true);
    assert.equal(preview.commitCount, 0);
    assert.equal(preview.requests[0].body, preview.requests[1].body);
    assert.deepEqual(JSON.parse(preview.requests[0].body).base.sources, loaded.liveSources);
    await page(() => document.querySelector('#vp-preview [data-cancel]').click());
    await ready("!document.querySelector('#vp-save-btn').disabled");
    assert.equal(await page((field) => [...document.querySelectorAll('#victory-paths-root [data-field]')]
      .find((item) => item.dataset.field === field).value, edit.field), edit.value);
    assert.equal(await page(() => document.querySelector('#victory-paths-root [data-sources]').textContent), loaded.base);
    assert.equal(await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="victory-paths"] [data-dot]').hidden), false);

    await page(() => document.querySelector('#vp-save-btn').click());
    await ready("document.querySelector('#vp-preview dialog').open");
    await page(() => document.querySelector('#vp-preview [data-confirm]').click());
    await ready("document.querySelector('#vp-status').textContent.includes('已刷新') && !document.querySelector('#vp-save-btn').disabled");
    const committed = await page(() => ({
      previewBody: __vpProbe.requests.filter((item) => item.path.endsWith('/preview')).at(-1).body,
      commitBody: __vpProbe.requests.filter((item) => item.path.endsWith('/commit')).at(-1).body,
      log: document.querySelector('#vp-log').textContent,
    }));
    assert.equal(committed.previewBody, committed.commitBody);
    assert.match(committed.log, /WP-11 intercepted commit/);

    await page(() => { __vpProbe.mode = 'conflict'; document.querySelector('#vp-save-btn').click(); });
    await ready("document.querySelector('#vp-log').textContent.includes('WP-11 intercepted conflict') && document.querySelector('#vp-status').textContent.includes('已刷新')");
    assert.equal(await page((field) => [...document.querySelectorAll('#victory-paths-root [data-field]')]
      .find((item) => item.dataset.field === field).value, edit.field), edit.value);
    assert.match(await page(() => document.querySelector('#vp-log').textContent), /原值已变化/);
    assert.equal(await page(() => JSON.parse(document.querySelector('#victory-paths-root [data-sources]').textContent)['data/victory_paths.yaml']), 'a'.repeat(64));

    await page(() => { __vpProbe.mode = 'missing'; document.querySelector('#vp-refresh-btn').click(); });
    await ready("!document.querySelector('#vp-refresh-btn').disabled && document.querySelector('#vp-save-btn').disabled");
    assert.match(await page(() => document.querySelector('#victory-paths-root [data-references]').textContent), /引用失效，禁止提交/);
    assert.equal(await page(() => document.querySelector('.tool-hub-tab-btn[data-tool="victory-paths"] [data-dot]').hidden), false);
    await page(() => { __vpProbe.mode = 'ready'; __vpProbe.freshSource = false; document.querySelector('#vp-reload-btn').click(); });
    await ready("!document.querySelector('#vp-reload-btn').disabled && document.querySelector('.tool-hub-tab-btn[data-tool=\"victory-paths\"] [data-dot]').hidden");
    const safe = await page(() => ({
      unknownPosts: __vpProbe.requests.filter((item) => item.method === 'POST' && !/\/(validate|preview|commit)$/.test(item.path)).length,
      stillDirty: window.__toolShell.dirtyTools(),
    }));
    assert.equal(safe.unknownPosts, 0);
    assert.deepEqual(safe.stillDirty, []);
    console.log('Victory paths acceptance passed: lazy live GET, grouped fields and three runtime slots, eight usable tabs, intercepted preview names milestone threshold, cancel keeps draft/base, frozen commit body, 409 draft-preserving refresh, unresolved rewards block saving; no business writes.');
  } finally {
    await page(() => { __probe.intercept = window.__vpPreviousIntercept; delete window.__vpPreviousIntercept; });
  }
};
