module.exports = async function courtPositionsBrowser({ evaluate, ready }) {
  const ROOT = '#court-positions-root';
  await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="court-positions"]').click()`);
  // `[data-fields]` is part of the panel's static template, so it exists before the
  // resource loads. Wait for a rendered field control instead, which only appears
  // after the live read-only GET resolves.
  await ready(`document.querySelector('${ROOT} input[data-field]')`);
  const loaded = await evaluate(`(() => {
    const root = document.querySelector('${ROOT}');
    return {
      positions: root.querySelectorAll('[data-positions] button').length,
      fields: root.querySelectorAll('[data-field]').length,
      dirty: root.querySelector('[data-dirty]').textContent,
    };
  })()`);
  if (!(loaded.positions > 0)) throw new Error(`court positions: no positions rendered (${JSON.stringify(loaded)})`);
  if (!(loaded.fields > 0)) throw new Error(`court positions: no editable fields rendered (${JSON.stringify(loaded)})`);
  if (!loaded.dirty.includes('无未保存草稿')) throw new Error(`court positions: expected a clean draft on load, got ${loaded.dirty}`);

  // Edit one field: the draft counter and the tab dot must both follow.
  await evaluate(`(() => {
    const input = document.querySelector('${ROOT} input[data-field]');
    input.value = '1';
    input.dispatchEvent(new Event('input', { bubbles: true }));
  })()`);
  await ready(`document.querySelector('${ROOT} [data-dirty]').textContent.includes('1 个字段')`);
  const dotHidden = await evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="court-positions"] [data-dot]').hidden`);
  if (dotHidden !== false) throw new Error('court positions: tab dot did not appear after editing a field');

  // Reward references are read-only and rendered as text rows.
  const references = await evaluate(`document.querySelectorAll('${ROOT} [data-references] p').length`);
  if (!(references > 0)) throw new Error('court positions: no modifier reference rows rendered');

  // Reloading keeps the tab alive and clears the draft marker.
  await evaluate(`document.querySelector('#cp-reload-btn').click()`);
  await ready(`document.querySelector('${ROOT} [data-dirty]').textContent.includes('无未保存草稿')`);
  await ready(`document.querySelector('.tool-hub-tab-btn[data-tool="court-positions"] [data-dot]').hidden`);

  console.log(`Court positions acceptance passed: live read-only GET rendered ${loaded.positions} positions and ${loaded.fields} editable fields, ${references} read-only modifier reference rows, draft counter and tab dot follow an edit, reload clears the draft; no business writes.`);
};
