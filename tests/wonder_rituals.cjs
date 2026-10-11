const assert = require('node:assert/strict');
const { test } = require('node:test');

const rituals = import('../towards_victory_editor_web/static/wonder_rituals.js');

test('ritual prompt builder keeps display order, nested values and translated title', async () => {
  const { buildRitualImplementationPrompt, ritualDesignEntriesForDisplay } = await rituals;
  const design = {
    id: 7,
    key: 'unique_test',
    display_name: 'Test Wonder',
    base_key: 'generic_test',
    location: 'test_location',
    source_ritual_key: 'ritual.test',
    field_labels: { title: '标题', mode: '模式', stages: '阶段', reward: '奖励' },
    ritual_design: { title: 'English title', mode: 'timed', stages: { reward: 'prestige' } },
    ritual_design_zh: { title: '中文标题', mode: 'timed', stages: { reward: 'prestige' } },
  };

  assert.deepEqual(ritualDesignEntriesForDisplay(design.ritual_design_zh), ['title', 'mode', 'stages']);
  const prompt = buildRitualImplementationPrompt(design);
  assert.match(prompt, /请实现独特奇观仪式：Test Wonder/);
  assert.match(prompt, /标题: 中文标题/);
  assert.match(prompt, /阶段:\n  奖励: prestige/);
  assert.match(prompt, /英文原文标题：\nEnglish title/);
});
