/**
 * TaxPreparerTools — Anthropic API Proxy
 * Deploy this as a Cloudflare Worker.
 *
 * SETUP:
 *  1. npx wrangler deploy   (or paste into dash.cloudflare.com → Workers)
 *  2. Set secret:  npx wrangler secret put ANTHROPIC_API_KEY
 *  3. Copy the Worker URL → paste into ai-assistant.html as WORKER_URL
 *
 * CORS: locked to taxpreparertools.com. Add localhost for local testing.
 */

const ALLOWED_ORIGINS = [
  'https://taxpreparertools.com',
  'http://taxpreparertools.com',
  'https://www.taxpreparertools.com',
  // 'http://localhost:3000',  // uncomment for local dev
];

const ANTHROPIC_API = 'https://api.anthropic.com/v1/messages';
const MODEL         = 'claude-sonnet-4-20250514';
const MAX_TOKENS    = 1024;

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';

    // — CORS preflight —
    if (request.method === 'OPTIONS') {
      return corsResponse(null, 204, origin);
    }

    if (request.method !== 'POST') {
      return corsResponse(JSON.stringify({ error: 'POST only' }), 405, origin);
    }

    // — Parse body —
    let body;
    try {
      body = await request.json();
    } catch {
      return corsResponse(JSON.stringify({ error: 'Invalid JSON' }), 400, origin);
    }

    const { system, messages } = body;

    if (!messages || !Array.isArray(messages) || messages.length === 0) {
      return corsResponse(JSON.stringify({ error: 'messages array required' }), 400, origin);
    }

    // — Call Anthropic —
    try {
      const anthropicRes = await fetch(ANTHROPIC_API, {
        method: 'POST',
        headers: {
          'Content-Type':         'application/json',
          'x-api-key':            env.ANTHROPIC_API_KEY,
          'anthropic-version':    '2023-06-01',
        },
        body: JSON.stringify({
          model:      MODEL,
          max_tokens: MAX_TOKENS,
          system:     system || '',
          messages:   messages.slice(-20), // cap context window at 20 turns
        }),
      });

      const data = await anthropicRes.json();

      if (!anthropicRes.ok) {
        console.error('Anthropic error:', JSON.stringify(data));
        return corsResponse(
          JSON.stringify({ error: data.error?.message || 'Anthropic API error' }),
          anthropicRes.status,
          origin
        );
      }

      return corsResponse(JSON.stringify(data), 200, origin);

    } catch (err) {
      console.error('Worker fetch error:', err);
      return corsResponse(JSON.stringify({ error: 'Internal error' }), 500, origin);
    }
  }
};

function corsResponse(body, status, origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  const headers = {
    'Access-Control-Allow-Origin':  allowed,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type':                 'application/json',
  };
  return new Response(body, { status, headers });
}
