const assert = require('node:assert/strict');
const { readFileSync, readdirSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');

const staticDir = join(__dirname, '..', 'towards_victory_editor_web', 'static');
const styles = readdirSync(staticDir).filter(name => name.endsWith('.css'))
  .map(name => ({ name, text: readFileSync(join(staticDir, name), 'utf8').replace(/\/\*[\s\S]*?\*\//g, '') }));

test('only shared.css owns color tokens and root/body/base button rules', () => {
  const owners = styles.filter(({ text }) => /--[\w-]+\s*:\s*[^;{}]*(?:#[\da-f]{3,8}\b|rgba?\(|hsla?\(|color-mix\()/i.test(text));
  assert.deepEqual(owners.map(({ name }) => name), ['shared.css']);
  for (const { name, text } of styles.filter(style => style.name !== 'shared.css')) {
    assert.doesNotMatch(text, /:root\b|(?:^|[{}])\s*body\s*\{|(?:^|[{}])\s*button\s*\{/, name);
  }
  assert.match(styles.find(style => style.name === 'shared.css').text, /color-scheme:\s*dark\s*;/);
});

test('CSS variables have one vocabulary without color fallbacks', () => {
  const combined = styles.map(({ text }) => text).join('\n');
  const declared = new Set([...combined.matchAll(/(--[\w-]+)\s*:/g)].map(match => match[1]));
  for (const { name, text } of styles) {
    for (const match of text.matchAll(/var\((--[\w-]+)/g)) assert(declared.has(match[1]), `${name}: undefined ${match[1]}`);
    assert.doesNotMatch(text, /var\(--[\w-]+\s*,/, `${name}: duplicated token fallback`);
  }
});
