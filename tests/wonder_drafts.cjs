const test = require('node:test');
const assert = require('node:assert/strict');

test('field drafts add, restore, and remove empty pages without replacing other draft content', async () => {
  const { emptyDraft, draftValueForField, setFieldDraft, setPromptDraft, draftHasChanges, dirtyPageCount } =
    await import('../towards_victory_editor_web/static/wonder_drafts.js');
  const drafts = { '1': emptyDraft() };

  setPromptDraft(drafts, 1, 'ritual prompt');
  setFieldDraft(drafts, 1, { scope: 'localization', language: 'english', key: 'title' }, 'New title', 'Title');
  setFieldDraft(drafts, 2, { scope: 'mechanics', key: 'mechanic' }, 'new', 'old');
  assert.deepEqual(drafts['1'].values.english, { title: 'New title' });
  assert.equal(draftValueForField(drafts['1'], { scope: 'localization', language: 'english', key: 'title' }), 'New title');
  assert.equal(drafts['1'].ritual_prompt, 'ritual prompt');
  assert.equal(dirtyPageCount(drafts), 2);

  setFieldDraft(drafts, 1, { scope: 'localization', language: 'english', key: 'title' }, 'Title\n', 'Title');
  assert.equal(drafts['1'].values.english.title, undefined);
  assert.equal(drafts['1'].ritual_prompt, 'ritual prompt');
  setPromptDraft(drafts, 1, undefined);
  assert.equal(draftHasChanges(drafts['1']), false);
  assert.equal(drafts['1'], undefined);
  assert.equal(dirtyPageCount(drafts), 1);
});

test('structured field drafts restore editor options and update name and initial-level previews', async () => {
  const { emptyDraft, setFieldDraft, applyDraftToWonderPayload } =
    await import('../towards_victory_editor_web/static/wonder_drafts.js');
  const payload = {
    summary: { id: 7, key: 'sample_wonder', name_en: 'Old', name_zh: '旧', display_name: '旧 / Old', is_unique: true, initial_level: 1 },
    meta: { key: 'sample_wonder', name_en: 'Old', name_zh: '旧', initial_level: 1 },
    languages: { english: { sections: [{ fields: [{ key: 'tv_wonder_sample_wonder', value: 'Old' }] }] } },
    mechanics: { sections: [{ fields: [{ key: 'mechanics.unique_initial_level.sample_wonder', field_type: 'number', value: '1' }, {
      key: 'mechanics.unique_ritual_editor.sample_wonder', field_type: 'unique_ritual_editor', value: '{}',
      structured_value: { stages: [{ title: 'Base' }], options: [{ value: 'ritual_option' }] },
    }] }] },
  };
  const draft = emptyDraft();
  const drafts = { '7': draft };
  const ref = (key, fieldType = 'text') => ({ scope: 'mechanics', key, fieldType });
  setFieldDraft(drafts, 7, { scope: 'localization', language: 'english', key: 'tv_wonder_sample_wonder' }, 'New', 'Old');
  setFieldDraft(drafts, 7, ref('mechanics.unique_initial_level.sample_wonder', 'number'), '3', '1');
  setFieldDraft(drafts, 7, ref('mechanics.unique_ritual_editor.sample_wonder', 'unique_ritual_editor'),
    '{"stages":[{"title":"Draft"}]}', '{}');

  const preview = applyDraftToWonderPayload(payload, draft);
  assert.equal(payload.languages.english.sections[0].fields[0].value, 'New');
  assert.equal(payload.summary.display_name, '旧 / New');
  assert.equal(payload.meta.name_en, 'New');
  assert.equal(payload.summary.initial_level, 3);
  assert.equal(payload.meta.initial_level, 3);
  assert.equal(payload.mechanics.sections[0].fields[1].structured_value.stages[0].title, 'Draft');
  assert.deepEqual(payload.mechanics.sections[0].fields[1].structured_value.options, [{ value: 'ritual_option' }]);
  assert.equal(preview.initial_level, 3);
});

test('name and initial-level keys share one definition with the page', async () => {
  const { wonderNameKeyForKey, uniqueInitialLevelFieldKey, parseUniqueInitialLevelValue } =
    await import('../towards_victory_editor_web/static/wonder_drafts.js');
  assert.equal(wonderNameKeyForKey('sample'), 'tv_wonder_sample');
  assert.equal(uniqueInitialLevelFieldKey({ meta: { key: 'sample' } }), 'mechanics.unique_initial_level.sample');
  assert.equal(uniqueInitialLevelFieldKey(null), '');
  assert.deepEqual(parseUniqueInitialLevelValue(' 4 '), { valid: true, level: 4, value: '4' });
  assert.equal(parseUniqueInitialLevelValue('7').valid, false);
});
