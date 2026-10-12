// WP-02: long wonder keys must wrap inside their meta cards at 1600px and 1000px.
// Mounted from resource_state_browser.cjs; read-only GETs; screenshots go to the OS temp dir, never the repo.
const assert = require('node:assert/strict');
const { mkdtempSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');

module.exports = async function wonderMetaWrapAcceptance({ evaluate, ready, send }) {
  const idle = "document.querySelector('.tool-wonder-localization').dataset.busy === 'false'";
  const longest = await evaluate(`(async () => {
    const { draft } = await (await fetch('/api/resources/editor.wonder')).json();
    return draft.wonders.reduce((best, w) => (w.key.length > best.key.length ? w : best));
  })()`);
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="wonder-localization"]').click();
    { const input = document.querySelector('#search-input'); input.value = ''; input.dispatchEvent(new Event('input', { bubbles: true })); }
    document.querySelectorAll('#wonder-kind-tabs button')[${longest.is_unique ? 1 : 0}].click();`);
  await ready(`!!document.querySelector('#wonder-list button[data-wonder-key=${JSON.stringify(longest.key)}]')`);
  await evaluate(`document.querySelector('#wonder-list button[data-wonder-key=${JSON.stringify(longest.key)}]').click()`);
  await ready(`${idle} && [...document.querySelectorAll('#wonder-meta .meta-card strong')].some(s => s.textContent === ${JSON.stringify(longest.key)})`);

  const measure = `(() => {
    const cards = [...document.querySelectorAll('#wonder-meta .meta-card')];
    const rects = cards.map(card => card.getBoundingClientRect());
    const problems = [];
    cards.forEach((card, i) => {
      const strong = card.querySelector('strong');
      const s = strong.getBoundingClientRect();
      if (strong.scrollWidth > strong.clientWidth + 1) problems.push('strong overflow ' + i + ': ' + strong.scrollWidth + '>' + strong.clientWidth);
      if (card.scrollWidth > card.clientWidth + 1) problems.push('card overflow ' + i + ': ' + card.scrollWidth + '>' + card.clientWidth);
      if (s.right > rects[i].right + 1 || s.left < rects[i].left - 1) problems.push('strong outside card ' + i + ': ' + strong.textContent);
      for (let j = i + 1; j < rects.length; j++) {
        const a = rects[i], b = rects[j];
        if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) problems.push('cards overlap ' + i + '/' + j);
      }
    });
    return { cards: cards.length, problems };
  })()`;

  const shots = mkdtempSync(join(tmpdir(), 'wp02-meta-'));
  const results = {};
  try {
    for (const width of [1600, 1000]) {
      await send('Emulation.setDeviceMetricsOverride', { width, height: 1000, deviceScaleFactor: 1, mobile: false });
      await evaluate('new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
      results[width] = await evaluate(measure);
      await evaluate("document.querySelector('#wonder-meta').scrollIntoView({ block: 'center' })");
      const { data } = await send('Page.captureScreenshot', { format: 'png' });
      writeFileSync(join(shots, `meta_${width}.png`), Buffer.from(data, 'base64'));
    }
  } finally {
    await send('Emulation.clearDeviceMetricsOverride');
  }
  for (const [width, result] of Object.entries(results)) {
    assert(result.cards >= 7, `meta cards rendered at ${width}px`);
    assert.deepEqual(result.problems, [], `meta cards at ${width}px for ${longest.key}`);
  }
  console.log(`Wonder meta wrap acceptance passed: ${longest.key} (${longest.key.length} chars) fits its card at 1600/1000px; screenshots in ${shots}.`);
};
