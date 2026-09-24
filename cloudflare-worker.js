/** Authenticated Anthropic proxy. Requires SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY,
 * ANTHROPIC_API_KEY and an AI_RATE_LIMITER Cloudflare Rate Limiting binding.
 * Deploy the Worker and bindings together; it fails closed if configuration is absent.
 */
const ORIGINS = new Set(['https://taxpreparertools.com', 'https://www.taxpreparertools.com']);
const MAX_BYTES = 24000;
const MAX_MESSAGE_CHARS = 4000;
const MAX_SYSTEM_CHARS = 6000;

function respond(data, status, origin) {
  const headers = { 'Content-Type': 'application/json', 'Cache-Control': 'no-store', 'Vary': 'Origin' };
  if (ORIGINS.has(origin)) {
    headers['Access-Control-Allow-Origin'] = origin;
    headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS';
    headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type';
  }
  return new Response(data === null ? null : JSON.stringify(data), { status, headers });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    if (!ORIGINS.has(origin)) return respond({ error: 'Forbidden' }, 403, origin);
    if (request.method === 'OPTIONS') return respond(null, 204, origin);
    if (request.method !== 'POST') return respond({ error: 'POST only' }, 405, origin);
    if (!env.ANTHROPIC_API_KEY || !env.SUPABASE_URL || !env.SUPABASE_PUBLISHABLE_KEY || !env.AI_RATE_LIMITER)
      return respond({ error: 'Service unavailable' }, 503, origin);
    const bearer = request.headers.get('Authorization') || '';
    if (!/^Bearer [A-Za-z0-9._-]+$/.test(bearer)) return respond({ error: 'Sign in required' }, 401, origin);
    const length = Number(request.headers.get('Content-Length'));
    if (length > MAX_BYTES) return respond({ error: 'Request too large' }, 413, origin);
    let raw;
    try { raw = await request.text(); } catch { return respond({ error: 'Invalid body' }, 400, origin); }
    if (raw.length > MAX_BYTES) return respond({ error: 'Request too large' }, 413, origin);
    let body;
    try { body = JSON.parse(raw); } catch { return respond({ error: 'Invalid JSON' }, 400, origin); }
    if (!Array.isArray(body.messages) || !body.messages.length || body.messages.length > 20 ||
        typeof body.system !== 'string' || body.system.length > MAX_SYSTEM_CHARS ||
        body.messages.some(m => !m || !['user', 'assistant'].includes(m.role) ||
          typeof m.content !== 'string' || !m.content.length || m.content.length > MAX_MESSAGE_CHARS))
      return respond({ error: 'Invalid conversation' }, 400, origin);

    // Supabase Auth validates the token remotely, including expiry and revocation.
    let userResponse;
    try {
      const authUrl = new URL('/auth/v1/user', env.SUPABASE_URL);
      userResponse = await fetch(authUrl, {
        headers: { apikey: env.SUPABASE_PUBLISHABLE_KEY, Authorization: bearer },
      });
    } catch { return respond({ error: 'Authentication unavailable' }, 503, origin); }
    if (!userResponse.ok) return respond({ error: 'Sign in required' }, 401, origin);
    const user = await userResponse.json();
    if (!user.id) return respond({ error: 'Sign in required' }, 401, origin);
    try {
      const limit = await env.AI_RATE_LIMITER.limit({ key: user.id });
      if (!limit.success) return respond({ error: 'AI usage limit reached. Try again later.' }, 429, origin);
    } catch { return respond({ error: 'Service unavailable' }, 503, origin); }

    try {
      const upstream = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': env.ANTHROPIC_API_KEY,
          'anthropic-version': '2023-06-01' },
        body: JSON.stringify({ model: 'claude-sonnet-4-20250514', max_tokens: 1024,
          system: body.system, messages: body.messages }),
      });
      if (!upstream.ok) return respond({ error: 'AI service unavailable' }, 502, origin);
      return respond(await upstream.json(), 200, origin);
    } catch { return respond({ error: 'AI service unavailable' }, 502, origin); }
  },
};
