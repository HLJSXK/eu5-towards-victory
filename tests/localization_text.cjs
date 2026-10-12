// WP-07: the localization text renderer. Native ES module with no DOM; the real page preview is
// covered by localization_browser.cjs (mounted from resource_state_browser.cjs).
//
// The scope assertions here are the ones the module documents: supported markup renders, unsupported
// markup degrades to a visible literal and is reported, never silently expanded.
const assert = require('node:assert/strict');
const { test } = require('node:test');

const module_ = import('../towards_victory_editor_web/static/localization_text.js');

test('#G content#! renders as a colored span, and #Gfoo#! degrades instead of absorbing its content', async () => {
  const { renderLocalizationText, parseLocalizationText } = await module_;
  assert.equal(renderLocalizationText('#G Text#!'),
    '<span class="loc-tag loc-g" data-tag="G">Text</span>');
  // The engine reads the tag name up to the first non-alphanumeric character, so `#Gfoo#!` names a tag
  // `Gfoo`; the renderer must show that as a literal token rather than color `foo` green and drop `#G`.
  // The trailing `#!` closes the unknown tag, so the visible text is the token itself.
  const broken = renderLocalizationText('#Gfoo#!');
  assert.equal(broken, '<span class="loc-unknown-tag" title="未知文本标记（会被引擎当作标记名的一部分）">#Gfoo</span>');
  assert.deepEqual(parseLocalizationText('#Gfoo#!').warnings,
    [{ type: 'unknown_tag', index: 0, raw: '#Gfoo' }]);
});

test('$X$ renders as a variable placeholder and is never expanded', async () => {
  const { renderLocalizationText } = await module_;
  assert.equal(renderLocalizationText('Cost $X$ gold'),
    'Cost <span class="loc-variable" title="运行时变量，预览不展开">$X$</span> gold');
  // The `|+$` shaped variables used for signed values keep their modifiers inside the placeholder.
  assert.match(renderLocalizationText('$VALUE|+$'),
    /class="loc-variable"[^>]*>\$VALUE\|\+\$<\/span>/);
});

test('[trust|e] renders as a localization function call and its argument is kept', async () => {
  const { renderLocalizationText, localizationTextPlainText } = await module_;
  assert.equal(renderLocalizationText('[trust|e]'),
    '<span class="loc-function" title="本地化函数，预览不展开">[trust|e]</span>');
  // No argument list is evaluated: the raw expression is what is shown and copied.
  assert.equal(localizationTextPlainText('[ShowBuildingTypeName(\'x\')]'), '[ShowBuildingTypeName(\'x\')]');
  const calls = renderLocalizationText('[ShowBuildingTypeName(\'x\')]');
  assert.match(calls, /loc-function/);
  assert.match(calls, /ShowBuildingTypeName/);
});

test('\\n becomes a line break and a physical newline does too', async () => {
  const { renderLocalizationText } = await module_;
  assert.equal(renderLocalizationText('First\\n#R Second#!'),
    'First<br><span class="loc-tag loc-r" data-tag="R">Second</span>');
  assert.equal(renderLocalizationText('a\nb'), 'a<br>b');
});

test('unclosed markup degrades: the marker is reported and nothing crashes', async () => {
  const { renderLocalizationText, localizationTextWarnings, parseLocalizationText } = await module_;
  // An unclosed color tag runs to the end of the value and is still closed in the HTML.
  assert.equal(renderLocalizationText('#R Never closed'),
    '<span class="loc-tag loc-unclosed loc-r" data-tag="R">Never closed</span>');
  assert.deepEqual(parseLocalizationText('#R Never closed').warnings,
    [{ type: 'unclosed_tag', index: 0, raw: '#R' }]);
  // Unclosed `$` and `[` keep their literal text and are reported.
  assert.deepEqual(localizationTextWarnings('$X'), [{ type: 'unclosed_variable', index: 0, raw: '$X' }]);
  assert.deepEqual(localizationTextWarnings('[trust|e'), [{ type: 'unclosed_function', index: 0, raw: '[trust|e' }]);
  assert.equal(renderLocalizationText('$X'), '$X');
  // A stray `#!` is reported at its character offset but produces no markup of its own.
  assert.deepEqual(localizationTextWarnings('ok#!'), [{ type: 'unmatched_close', index: 2, raw: '#!' }]);
  assert.equal(renderLocalizationText('ok#!'), 'ok');
});

test('unsupported markup is labeled, not faked: @icon! and unknown tags', async () => {
  const { renderLocalizationText } = await module_;
  // Icons need the engine's font textures and per-icon sizing, so they render as a labeled chip.
  assert.equal(renderLocalizationText('300 @gold! gold'),
    '300 <span class="loc-icon" title="内联贴图，预览不渲染">@gold!</span> gold');
  assert.match(renderLocalizationText('#Y 5 #weird#!'), /loc-unknown-tag/);
});

test('nested tags keep their order and every text run is escaped', async () => {
  const { renderLocalizationText } = await module_;
  assert.equal(renderLocalizationText('#bold a #Y b#! c#!'),
    '<span class="loc-tag loc-bold" data-tag="bold">a <span class="loc-tag loc-y" data-tag="Y">b</span> c</span>');
  const escaped = renderLocalizationText('<img src=x onerror="window.__xss=true"> & "q"');
  assert.equal(escaped, '&lt;img src=x onerror=&quot;window.__xss=true&quot;&gt; &amp; &quot;q&quot;');
  assert.equal(escaped.includes('<img'), false);
  // A tag parameter only starts after a colon that is followed by a real parameter, so `#Y: 5` keeps
  // the colon as content instead of swallowing it. With no `#!`, the tag stays open to the end.
  assert.equal(renderLocalizationText('#Y: 5'), '<span class="loc-tag loc-unclosed loc-y" data-tag="Y">: 5</span>');
  assert.equal(renderLocalizationText('#indent_newline:2 text#!'),
    '<span class="loc-tag loc-indent" data-tag="indent_newline:2">text</span>');
});

test('plain text drops supported markup and keeps line breaks', async () => {
  const { localizationTextPlainText } = await module_;
  assert.equal(localizationTextPlainText('#G Gain 30#!\\n#R Lose 5#!'), 'Gain 30\nLose 5');
  // An unknown tag keeps its token (`#Gfoo`, with the closing `#!` consumed as the tag's end).
  assert.equal(localizationTextPlainText('#Gfoo#! stays'), '#Gfoo stays');
  assert.equal(localizationTextPlainText('$X$ and [trust|e]'), '$X$ and [trust|e]');
});
