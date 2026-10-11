// Called by resource_state_browser.cjs with its live Chrome page and read-only server.
const assert = require('node:assert/strict');

module.exports = async function wonderPanelsAcceptance({ evaluate, ready }) {
  const page = (fn, ...args) => evaluate(`(${fn.toString()})(${args.map(arg => JSON.stringify(arg)).join(',')})`);
  const idle = "document.querySelector('.tool-wonder-localization').dataset.busy === 'false'";
  const search = value => page(value => {
    const input = document.querySelector('#search-input');
    input.value = value;
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }, value);
  const mode = index => page(index => document.querySelectorAll('#wonder-kind-tabs button')[index].click(), index);
  const listKeys = () => page(() => [...document.querySelectorAll('#wonder-list button')].map(b => b.dataset.wonderKey));

  const counts = await page(async () => {
    const { draft } = await (await fetch('/api/resources/editor.wonder')).json();
    return { generic: draft.wonders.filter(w => !w.is_unique).length, unique: draft.wonders.filter(w => w.is_unique).length };
  });
  await search('');
  await mode(0);
  assert.equal((await listKeys()).length, counts.generic);
  assert.deepEqual(await page(() => [...document.querySelectorAll('#wonder-kind-tabs button')].map(b => b.textContent)),
    [`通用奇观 (${counts.generic})`, `独特奇观 (${counts.unique})`]);
  await mode(1);
  assert.equal((await listKeys()).length, counts.unique);
  assert.equal(await page(() => document.querySelector('#wonder-count').textContent), `显示 ${counts.unique} / ${counts.unique} 个独特奇观`);

  // Modify only a read response to exercise the page's actual thumbnail HTML and search wiring.
  const probe = {
    name: '<img src=x onerror="window.__panelXss=true"> & "中文"',
    english: 'WonderPanelSearchProbe',
    url: '/static/wonder-panel-probe.png?value=" onerror="window.__panelXss=true" & <text>',
  };
  await page(probe => {
    __probe.intercept = async (path, live) => {
      if (path !== '/api/resources/editor.wonder') return null;
      const payload = await (await live()).json();
      const wonder = payload.draft.wonders.find(w => !w.is_unique);
      window.__panelProbeKey = wonder.key;
      Object.assign(wonder, { name_zh: probe.name, name_en: probe.english, image: { url: probe.url } });
      return Response.json(payload);
    };
    document.querySelector('#reload-button').click();
  }, probe);
  try {
    await ready(idle);
    await mode(0);
    await search('  WONDERPANELSEARCHPROBE  ');
    assert.deepEqual(await listKeys(), [await page(() => __panelProbeKey)]);
    assert.equal(await page(() => document.querySelector('#wonder-count').textContent), `显示 1 / ${counts.generic} 个通用奇观`);
    assert.deepEqual(await page(() => {
      const button = document.querySelector('#wonder-list button'), image = button.querySelector('img');
      return { name: button.querySelector('strong').textContent, alt: image.alt, src: image.getAttribute('src'),
        images: button.querySelectorAll('img').length, injected: !!button.querySelector('[onerror]'), xss: !!window.__panelXss };
    }), { name: probe.name, alt: probe.name + ' image', src: probe.url, images: 1, injected: false, xss: false });
    await mode(1);
    assert.equal((await listKeys()).length, 0);
    assert.equal(await page(() => document.querySelector('#wonder-list .empty-state').textContent), '没有匹配的奇观。');
    await mode(0);
    assert.equal((await listKeys()).length, 1, 'type switching keeps the search');
  } finally {
    await page(() => { __probe.intercept = null; delete window.__panelProbeKey; delete window.__panelXss; });
    await search('');
    await page(() => document.querySelector('#reload-button').click());
    await ready(idle);
  }

  // Follow the real selection callback and verify page drafts drive the meta label.
  await mode(1);
  const selectedKey = await page(() => {
    const button = document.querySelector('#wonder-list button');
    const key = button.dataset.wonderKey;
    button.click();
    return key;
  });
  await ready(idle);
  assert.equal(await page(() => document.querySelector('#wonder-list .active').dataset.wonderKey), selectedKey);
  await page(() => [...document.querySelectorAll('#language-tabs button')].find(b => b.textContent === 'Mechanics').click());
  const setLevel = value => page(value => {
    const field = document.querySelector('[data-key^="mechanics.unique_initial_level."]');
    field.value = value;
    field.dispatchEvent(new Event('input', { bubbles: true }));
    return [...document.querySelectorAll('#wonder-meta .meta-card')].find(c => c.firstElementChild.textContent === 'Start state').lastElementChild.textContent;
  }, value);
  assert.equal(await setLevel('0'), 'Not present');
  assert.equal(await setLevel('4'), 'Level 4');
  assert.equal(await setLevel('7'), 'Invalid level: 7');
  assert.equal(await setLevel(''), 'Invalid level');
  await page(() => document.querySelector('#reload-button').click());
  await ready(idle);
  assert(await page(() => document.querySelector('#dirty-badge').classList.contains('hidden')));

  // A separate factory instance uses current getter values and safely renders image captions.
  const images = await page(async () => {
    const { createWonderPanels } = await import('/static/wonder_panels.js');
    const elements = { wonderImageFrame: document.createElement('figure') };
    let current = null;
    const panels = createWonderPanels({ elements, getCurrentWonder: () => current });
    panels.renderImage();
    const empty = elements.wonderImageFrame.classList.contains('is-missing') && !elements.wonderImageFrame.childElementCount;
    current = { summary: { key: 'image_probe' }, meta: { image: { filename: 'probe.dds', path: '<img src=x onerror="window.__panelXss=true">' } } };
    panels.renderImage();
    const missing = elements.wonderImageFrame.querySelector('.wonder-image-placeholder').textContent;
    const caption = elements.wonderImageFrame.querySelector('figcaption').textContent;
    const injected = !!elements.wonderImageFrame.querySelector('figcaption img');
    current.meta.image.url = '/static/wonder-panel-probe.png';
    panels.renderImage();
    return { empty, missing, caption, injected, alt: elements.wonderImageFrame.querySelector('img').alt,
      loaded: elements.wonderImageFrame.classList.contains('has-image'),
      missingClass: elements.wonderImageFrame.classList.contains('is-missing') };
  });
  assert.deepEqual(images, { empty: true, missing: 'No generated image', caption: '<img src=x onerror="window.__panelXss=true">',
    injected: false, alt: 'image_probe image', loaded: true, missingClass: false });
  console.log('Wonder panels acceptance passed: kind counts, search, escaped thumbnails, selection, initial-level draft labels and image states.');
};
