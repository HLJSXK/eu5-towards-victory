// Called by resource_state_browser.cjs with its live Chrome page and read-only server.
const assert = require('node:assert/strict');
const { setTimeout: delay } = require('node:timers/promises');

module.exports = async function wonderRitualsAcceptance({ evaluate, ready, send }) {
  const panel = "document.querySelector('[data-editor-tab=\"ritual-design\"]')";
  const idle = "document.querySelector('.tool-wonder-localization').dataset.busy === 'false'";
  const clickTab = (text) => evaluate(`[...document.querySelectorAll('#language-tabs button')].find(b => b.textContent.includes('${text}')).click()`);

  // Catalog call 1 fails, 2 waits for a gate, 3 is a stale response released after a newer reload.
  await evaluate(`(() => {
    const rituals = window.__rituals = { catalog: 0, detail: 0, gates: {} };
    const gate = (name) => new Promise((resolve) => { rituals.gates[name] = resolve; });
    __probe.intercept = async (path, live) => {
      if (path === '/api/wonder-localization/ritual-designs') {
        const call = ++rituals.catalog;
        if (call === 1) return Response.json({ detail: 'ritual catalog probe failure' }, { status: 503 });
        if (call === 2) { await gate('retry'); return live(); }
        if (call === 3) { const payload = await (await live()).json(); await gate('stale'); return Response.json({ ...payload, count: 999 }); }
        return live();
      }
      if (path.startsWith('/api/wonder-localization/ritual-designs/') && rituals.detail++ === 0) {
        return Response.json({ detail: 'ritual detail probe failure' }, { status: 500 });
      }
      return null;
    };
  })()`);
  await clickTab('English');
  await evaluate("document.querySelector('#reload-button').click()");
  await ready(idle);
  assert.equal(await evaluate('__rituals.catalog'), 0, 'catalog waits for the ritual tab');

  await clickTab('仪式设计');
  await ready(`${panel}.textContent.includes('ritual catalog probe failure')`);
  await evaluate(`[...${panel}.querySelectorAll('button')].find(b => b.textContent.includes('生成 Prompt 草稿')).click()`);
  assert.match(await evaluate(`${panel}.querySelector('[data-ritual-prompt-input]').value`), /请实现独特奇观仪式/);
  assert(await evaluate("!document.querySelector('#dirty-badge').classList.contains('hidden')"), 'generated prompt is a draft');

  await evaluate(`{ const input = ${panel}.querySelector('[data-ritual-prompt-input]');
    input.value = 'draft while catalog loads'; input.dispatchEvent(new Event('input', { bubbles: true })); }`);
  await evaluate(`[...${panel}.querySelectorAll('button')].find(b => b.textContent === '重试').click()`);
  await ready(`${panel}.querySelector('.ritual-design-catalog-content').textContent.includes('正在加载')`);
  await evaluate(`{ window.__ritualPrompt = ${panel}.querySelector('[data-ritual-prompt-input]'); __ritualPrompt.focus(); __ritualPrompt.setSelectionRange(6, 6); }`);
  await evaluate('__rituals.gates.retry()');
  await ready(`!!${panel}.querySelector('.ritual-design-all')`);
  assert.deepEqual(await evaluate(`({ value: __ritualPrompt.value, same: __ritualPrompt === ${panel}.querySelector('[data-ritual-prompt-input]'),
    focused: document.activeElement === __ritualPrompt, caret: __ritualPrompt.selectionStart })`),
  { value: 'draft while catalog loads', same: true, focused: true, caret: 6 }, 'catalog render keeps the prompt editor');

  await evaluate(`{ window.__ritualItem = ${panel}.querySelector('.ritual-design-all details.ritual-design-card:not([open])'); __ritualItem.open = true; }`);
  await ready("__ritualItem.textContent.includes('ritual detail probe failure')");
  await evaluate('__ritualItem.open = false');
  await delay(100);
  await evaluate('__ritualItem.open = true');
  await ready("!!__ritualItem.querySelector(':scope > .ritual-design-body')");
  assert.equal(await evaluate('__rituals.detail'), 2, 'detail retries after a failed expansion');

  // The reload invalidates the catalog; the first reload's late response must not replace the second's.
  await evaluate("document.querySelector('#reload-button').click()");
  await ready('__rituals.catalog === 3 && !!__rituals.gates.stale');
  await ready(idle);
  await evaluate("document.querySelector('#reload-button').click()");
  await ready(idle);
  await ready(`!!${panel}?.querySelector('.ritual-design-all')`);
  await evaluate('__rituals.gates.stale()');
  await delay(300);
  assert(!(await evaluate(`${panel}.querySelector('.ritual-design-count').textContent`)).includes('999'), 'stale catalog discarded');
  assert(await evaluate("document.querySelector('#dirty-badge').classList.contains('hidden')"));

  await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: false });
  try {
    assert(await evaluate(`${panel}.querySelector('[data-ritual-prompt-input]').getClientRects().length > 0`), 'narrow prompt visible');
    assert(await evaluate(`(e => e.scrollWidth <= e.clientWidth + 1)(${panel}.querySelector('.origin-pill'))`), 'narrow source path fits');
  } finally {
    await send('Emulation.clearDeviceMetricsOverride');
  }
  await evaluate('__probe.intercept = null; delete window.__rituals; delete window.__ritualPrompt; delete window.__ritualItem');
  await clickTab('English');
  console.log('Wonder rituals acceptance passed: tab-gated catalog, failure retry, generated prompt draft, prompt editor kept across catalog render, detail retry, stale catalog isolation and narrow layout.');
};
