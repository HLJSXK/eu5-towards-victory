// Run with: node --test tests/api.cjs
// VM loaders strip export keywords; page tests also strip single-line imports with regex.
// Multiline imports or export default require updating these loaders.
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

function client(fetch) {
  const context = vm.createContext({ fetch });
  vm.runInContext(readFileSync(join(__dirname, '../towards_victory_editor_web/static/api.js'), 'utf8')
    .replace(/^export /gm, ''), context);
  return vm.runInContext('({ fetchJson, ApiError })', context);
}

for (const [code, guidance, detail] of [
  ['resource_busy', '资源正在保存或生成中。请稍后重试。', 'Resource busy: editor.wonder_crop'],
  ['resource_changed', '源文件已变化。请核对最新内容后重试。', 'Resource changed since load: data/unique_wonders.yaml'],
]) {
  test(`409 ${code} includes server diagnostics in the shared guidance`, async () => {
    const payload = {
      detail, code, operation_id: 'commit-1',
      operation: { id: 'commit-1', status: 'conflict', events: [{ message: 'conflict' }] },
    };
    const api = client(async () => Response.json(payload, { status: 409 }));
    await assert.rejects(api.fetchJson('/api/resources/editor.wonder/commit'), (error) => {
      assert(error instanceof api.ApiError);
      assert.equal(error.name, 'ApiError');
      assert.equal(error.status, 409);
      assert.equal(error.message, `${guidance}（${detail}）`);
      assert.equal(error.detail, payload.detail);
      assert.equal(error.code, code);
      assert.equal(error.operation_id, payload.operation_id);
      assert.equal(JSON.stringify(error.operation), JSON.stringify(payload.operation));
      return true;
    });
  });
}

for (const [field, value] of [
  ['generation', { operation_id: 'commit-2', steps: [{ id: 'generate', status: 'failed' }], rollback: { status: 'succeeded' } }],
  ['log_text', '[error] generator failed\nrestored outputs\n'],
]) {
  test(`500 retains ${field} on the error`, async () => {
    const api = client(async () => Response.json({ detail: 'generator failed', [field]: value }, { status: 500 }));
    await assert.rejects(api.fetchJson('/commit'), (error) => {
      assert(error instanceof api.ApiError);
      assert.equal(error.status, 500);
      assert.equal(error.detail, 'generator failed');
      assert.equal(error.message, 'generator failed');
      assert.equal(JSON.stringify(error[field]), JSON.stringify(value));
      return true;
    });
  });
}

test('non-JSON error bodies are consumed once and retain the original text', async () => {
  const body = '<html>502 Bad Gateway</html>';
  const response = new Response(body, { status: 502 });
  let reads = 0;
  const readText = response.text.bind(response);
  response.text = () => { reads += 1; return readText(); };
  response.json = () => { assert.fail('an error response must be read as text only'); };
  const api = client(async () => response);
  await assert.rejects(api.fetchJson('/commit'), (error) => {
    assert(error instanceof api.ApiError);
    assert.equal(error.status, 502);
    assert.equal(error.detail, body);
    assert.equal(error.message, body);
    assert.equal(reads, 1);
    assert(response.bodyUsed);
    return true;
  });
});

test('a successful response returns JSON and forwards request options unchanged', async () => {
  const options = { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{"edits":{}}' };
  const payload = { operation_id: 'commit-3', draft: { value: 7 } };
  const api = client(async (url, received) => {
    assert.equal(url, '/commit');
    assert.equal(received, options);
    return Response.json(payload);
  });
  assert.deepEqual(await api.fetchJson('/commit', options), payload);
});

test('an unrecognized 409 keeps its diagnostic instead of reporting a stale resource', async () => {
  const api = client(async () => Response.json({ detail: 'another conflict' }, { status: 409 }));
  await assert.rejects(api.fetchJson('/commit'), { message: 'another conflict', status: 409 });
});

test('structured validation details remain inspectable and produce a readable message', async () => {
  const detail = [{ loc: ['body', 'base'], msg: 'Field required' }];
  const api = client(async () => Response.json({ detail }, { status: 422 }));
  await assert.rejects(api.fetchJson('/commit'), (error) => {
    assert.equal(error.status, 422);
    assert.equal(JSON.stringify(error.detail), JSON.stringify(detail));
    assert.equal(error.message, JSON.stringify(detail));
    return true;
  });
});

test('empty detail falls back to the raw response and custom messages keep diagnostics', async () => {
  const raw = JSON.stringify({ detail: '  ', code: 'resource_busy' });
  const api = client(async () => new Response(raw, { status: 409 }));
  await assert.rejects(api.fetchJson('/commit', undefined, {
    errorMessages: { resource_busy: (detail) => `Busy; draft preserved (${detail})` },
  }), (error) => {
    assert.equal(error.detail, raw);
    assert.equal(error.message, `Busy; draft preserved (${raw})`);
    return true;
  });
});
