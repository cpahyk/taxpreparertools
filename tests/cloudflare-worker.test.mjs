import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const source = await readFile(new URL('../cloudflare-worker.js', import.meta.url), 'utf8');
const { default: worker } = await import('data:text/javascript;base64,' + Buffer.from(source).toString('base64'));
const origin = 'https://www.taxpreparertools.com';
const url = 'https://taxprep-ai.example.workers.dev/';
const validBody = JSON.stringify({ system: 'US tax', messages: [{ role: 'user', content: 'Hello' }] });
const env = (limit = true) => ({ ANTHROPIC_API_KEY: 'test-key', SUPABASE_URL: 'https://example.supabase.co',
  SUPABASE_PUBLISHABLE_KEY: 'test-publishable', AI_RATE_LIMITER: { limit: async () => ({ success: limit }) } });
const request = (body = validBody, headers = {}) => new Request(url, { method: 'POST', headers: {
  Origin: origin, Authorization: 'Bearer valid.token', 'Content-Type': 'application/json', ...headers }, body });

// Local fetch stubs allow verifying that rejected requests never reach the paid API.
test('rejects unapproved origins before making an upstream call', async () => {
  let calls = 0; globalThis.fetch = async () => { calls++; throw Error('unexpected'); };
  const response = await worker.fetch(request(validBody, { Origin: 'https://attacker.test' }), env());
  assert.equal(response.status, 403); assert.equal(calls, 0);
  assert.equal(response.headers.get('Access-Control-Allow-Origin'), null);
});

test('requires a token and bounded input', async () => {
  let calls = 0; globalThis.fetch = async () => { calls++; throw Error('unexpected'); };
  assert.equal((await worker.fetch(request(validBody, { Authorization: '' }), env())).status, 401);
  assert.equal((await worker.fetch(request('x'.repeat(24001)), env())).status, 413);
  assert.equal((await worker.fetch(request(JSON.stringify({ system: '', messages: [{ role: 'user', content: 'x'.repeat(4001) }] })), env())).status, 400);
  assert.equal(calls, 0);
});

test('authenticates and rate limits before calling Anthropic', async () => {
  let calls = 0;
  globalThis.fetch = async () => { calls++; return new Response(JSON.stringify({ id: 'user-1' }), { status: 200 }); };
  assert.equal((await worker.fetch(request(), env(false))).status, 429);
  assert.equal(calls, 1);
});

test('passes validated requests and hides Anthropic errors', async () => {
  let calls = 0;
  globalThis.fetch = async (target) => {
    calls++;
    if (String(target).includes('/auth/v1/user')) return new Response(JSON.stringify({ id: 'user-1' }));
    return new Response(JSON.stringify({ error: { message: 'private detail' } }), { status: 429 });
  };
  const response = await worker.fetch(request(), env());
  assert.equal(response.status, 502); assert.equal(calls, 2);
  assert.doesNotMatch(await response.text(), /private detail/);
});
