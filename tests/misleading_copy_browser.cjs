// WP-03: misleading labels are corrected. Mounted from resource_state_browser.cjs; read-only GETs, no writes.
const assert = require('node:assert/strict');
const { mkdtempSync, writeFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join } = require('node:path');

module.exports = async function misleadingCopyAcceptance({ evaluate, ready, send }) {
  const shots = mkdtempSync(join(tmpdir(), 'wp03-copy-'));
  const shot = async (name) => writeFileSync(join(shots, `${name}.png`), Buffer.from((await send('Page.captureScreenshot', { format: 'png' })).data, 'base64'));
  const tab = (tool) => evaluate(`document.querySelector('.tool-hub-tab-btn[data-tool="${tool}"]').click()`);

  // Victory tree: design-record notice, coordinate-only save button, no regenerate wording on save.
  await tab('victory-tree');
  const tree = await evaluate(`(() => {
    const panel = document.querySelector('.tool-victory-tree');
    return { text: panel.innerText, save: document.querySelector('#vt-save-btn').innerText,
      buttons: [...panel.querySelectorAll('button')].map((b) => b.innerText) };
  })()`);
  assert(tree.text.includes('设计稿（未实现），仅用于摆放坐标；不参与游戏当前系统'), 'victory tree design notice');
  assert.equal(tree.save, '保存坐标');
  assert.deepEqual(tree.buttons.filter((text) => text.includes('重新生成')), [], 'no victory tree button mentions 重新生成');
  await shot('victory_tree');

  // cost/reward: both task_pool categories say no mechanic consumes the catalog; reward categories do not.
  await tab('cost-reward');
  const notice = '当前无机制消费此目录（见 docs/design/Cost_Reward_Unit_Concepts.md 第 6 节）';
  const groups = await evaluate("[...document.querySelectorAll('#cr-tabs button')].map((b) => b.innerText)");
  const seen = {};
  for (let index = 0; index < groups.length; index++) {
    await evaluate(`document.querySelectorAll('#cr-tabs button')[${index}].click()`);
    await ready(`document.querySelectorAll('#cr-tabs button')[${index}].classList.contains('active')`);
    seen[groups[index]] = await evaluate(`document.querySelector('#panels').innerText.includes(${JSON.stringify(notice)})`);
  }
  const taskTabs = Object.keys(seen).filter((label) => /任务/.test(label));
  assert.equal(taskTabs.length, 2, `two task_pool tabs: ${JSON.stringify(groups)}`);
  for (const label of Object.keys(seen)) assert.equal(seen[label], taskTabs.includes(label), `task_pool notice on ${label}`);
  await evaluate("document.querySelector('.task-pool-notice').scrollIntoView({ block: 'center' })");
  await shot('task_pool');
  await evaluate("document.querySelectorAll('#cr-tabs button')[0].click()");

  // Media tools: badges come from ToolSpec.cost_hint served by /api/media/bootstrap.
  await tab('media-studio');
  await ready("document.querySelectorAll('#media-tool-list button').length > 0");
  await shot('media_tools');
  const { tools } = await evaluate("fetch('/api/media/bootstrap').then((r) => r.json())");
  const cards = await evaluate(`[...document.querySelectorAll('#media-tool-list button')].map((b) => b.innerText)`);
  assert.equal(cards.length, tools.length);
  const expected = { paid_api: '付费', local: '本地' };
  assert.equal(tools.filter((tool) => tool.cost_hint === 'paid_api').length, 3);
  assert.equal(tools.filter((tool) => tool.cost_hint === 'local').length, 2);
  tools.forEach((tool, index) => {
    assert(cards[index].includes(expected[tool.cost_hint]), `${tool.id} badge ${expected[tool.cost_hint]}: ${cards[index]}`);
    const other = tool.cost_hint === 'paid_api' ? '本地' : '付费';
    assert(!cards[index].split('\n').includes(other), `${tool.id} has no ${other} badge`);
  });
  console.log(`Misleading copy acceptance passed: victory tree design notice and 保存坐标, task_pool notices on 2 tabs, 3 付费 / 2 本地 media badges; screenshots in ${shots}.`);
};
