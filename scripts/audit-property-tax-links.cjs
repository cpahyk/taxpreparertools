#!/usr/bin/env node
'use strict';

const fs = require('fs');
const vm = require('vm');

const DATA_FILE = process.env.PROPERTY_TAX_DATA_FILE || 'assets/js/property-tax-data.js';
const OUTPUT_JSON = process.env.PROPERTY_TAX_AUDIT_JSON || 'property-tax-link-audit.json';
const OUTPUT_MD = process.env.PROPERTY_TAX_AUDIT_MD || 'property-tax-link-audit.md';
const CONCURRENCY = Math.max(1, Number(process.env.PROPERTY_TAX_AUDIT_CONCURRENCY || 6));
const TIMEOUT_MS = Math.max(2000, Number(process.env.PROPERTY_TAX_AUDIT_TIMEOUT_MS || 10000));
const LIMIT = Math.max(0, Number(process.env.PROPERTY_TAX_AUDIT_LIMIT || 0));
const USER_AGENT = 'TaxPreparerTools-LinkAudit/1.0 (+https://www.taxpreparertools.com/property-tax-search.html)';

function loadDirectory() {
  const source = fs.readFileSync(DATA_FILE, 'utf8');
  const sandbox = { window: {} };
  vm.createContext(sandbox);
  vm.runInContext(source, sandbox, { filename: DATA_FILE, timeout: 2000 });

  const api = sandbox.window.PROPERTY_TAX_DATA;
  if (!api || !Array.isArray(api.states) || typeof api.getCounties !== 'function') {
    throw new Error('PROPERTY_TAX_DATA did not load correctly.');
  }

  const byUrl = new Map();
  for (const state of api.states) {
    for (const item of api.getCounties(state.code)) {
      if (!item || !item.portal || api.isSearchFallback(item)) continue;
      if (!/^https:\/\//i.test(item.portal)) continue;

      const existing = byUrl.get(item.portal) || {
        url: item.portal,
        jurisdictions: []
      };
      existing.jurisdictions.push({
        state: state.code,
        stateName: state.name,
        name: api.getJurisdictionLabel(state.code, item.name)
      });
      byUrl.set(item.portal, existing);
    }
  }

  let entries = [...byUrl.values()];
  if (LIMIT > 0) entries = entries.slice(0, LIMIT);
  return entries;
}

function classify(status, redirected) {
  if (status >= 200 && status < 300) return redirected ? 'redirected-ok' : 'ok';
  if ([401, 403, 429].includes(status)) return 'protected-or-rate-limited';
  if ([404, 410].includes(status)) return 'stale';
  if (status >= 500) return 'server-error';
  if (status >= 300 && status < 400) return 'redirect';
  return 'other-http';
}

async function request(url, method) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  const started = Date.now();

  try {
    const response = await fetch(url, {
      method,
      redirect: 'follow',
      signal: controller.signal,
      headers: {
        'user-agent': USER_AGENT,
        'accept': 'text/html,application/xhtml+xml;q=0.9,*/*;q=0.1'
      }
    });

    try {
      if (response.body) await response.body.cancel();
    } catch (_) {}

    return {
      ok: true,
      method,
      status: response.status,
      finalUrl: response.url || url,
      redirected: response.redirected,
      elapsedMs: Date.now() - started
    };
  } catch (error) {
    return {
      ok: false,
      method,
      status: null,
      finalUrl: url,
      redirected: false,
      elapsedMs: Date.now() - started,
      error: error && error.name === 'AbortError' ? 'timeout' : String(error && error.message || error)
    };
  } finally {
    clearTimeout(timer);
  }
}

function resultCategory(result) {
  return result.ok
    ? classify(result.status, result.redirected)
    : (result.error === 'timeout' ? 'timeout' : 'network-error');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function probe(url) {
  let result = await request(url, 'HEAD');

  if (!result.ok || [400, 403, 405, 406, 501].includes(result.status)) {
    const getResult = await request(url, 'GET');
    if (getResult.ok || !result.ok) result = getResult;
  }

  return result;
}

async function inspect(entry) {
  let attempts = 1;
  let result = await probe(entry.url);
  let category = resultCategory(result);

  if (['server-error', 'timeout', 'network-error'].includes(category)) {
    await sleep(750);
    attempts++;
    const retry = await probe(entry.url);
    const retryCategory = resultCategory(retry);

    // Prefer the retry when it recovers or provides a concrete HTTP response.
    if (!['server-error', 'timeout', 'network-error'].includes(retryCategory) || retry.status !== null) {
      result = retry;
      category = retryCategory;
    }
  }

  return {
    ...entry,
    checkedAt: new Date().toISOString(),
    attempts,
    status: result.status,
    category,
    finalUrl: result.finalUrl,
    redirected: result.redirected,
    method: result.method,
    elapsedMs: result.elapsedMs,
    error: result.error || null
  };
}

async function mapConcurrent(items, worker, concurrency) {
  const results = new Array(items.length);
  let cursor = 0;

  async function runWorker() {
    while (true) {
      const index = cursor++;
      if (index >= items.length) return;
      results[index] = await worker(items[index]);
      const r = results[index];
      const retryNote = r.attempts > 1 ? ` retry=${r.attempts}` : '';
      process.stdout.write(`[${index + 1}/${items.length}] ${r.category} ${r.status || '-'}${retryNote} ${items[index].url}\n`);
    }
  }

  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, runWorker));
  return results;
}

function markdown(results) {
  const counts = results.reduce((acc, r) => {
    acc[r.category] = (acc[r.category] || 0) + 1;
    return acc;
  }, {});

  const attention = results.filter(r => !['ok', 'redirected-ok'].includes(r.category));
  const redirected = results.filter(r => r.category === 'redirected-ok' && r.finalUrl !== r.url);

  const lines = [
    '# Property Tax Portal Link Audit',
    '',
    `Generated: ${new Date().toISOString()}`,
    `Unique direct portals checked: ${results.length}`,
    '',
    '## Summary',
    ''
  ];

  for (const key of ['ok','redirected-ok','protected-or-rate-limited','stale','server-error','timeout','network-error','other-http','redirect']) {
    if (counts[key]) lines.push(`- **${key}**: ${counts[key]}`);
  }

  lines.push('', '## Needs review', '');
  if (!attention.length) {
    lines.push('No links require review.');
  } else {
    lines.push('| Category | HTTP | Jurisdiction(s) | URL |', '|---|---:|---|---|');
    for (const r of attention) {
      const names = r.jurisdictions.map(j => `${j.state}: ${j.name}`).join('; ').replace(/\|/g, '\\|');
      const url = r.url.replace(/\|/g, '%7C');
      lines.push(`| ${r.category} | ${r.status || '-'} | ${names} | ${url} |`);
    }
  }

  lines.push('', '## Redirected successfully', '');
  if (!redirected.length) {
    lines.push('No successful redirects detected.');
  } else {
    lines.push('| Jurisdiction(s) | Original | Final |', '|---|---|---|');
    for (const r of redirected) {
      const names = r.jurisdictions.map(j => `${j.state}: ${j.name}`).join('; ').replace(/\|/g, '\\|');
      lines.push(`| ${names} | ${r.url.replace(/\|/g, '%7C')} | ${r.finalUrl.replace(/\|/g, '%7C')} |`);
    }
  }

  lines.push(
    '',
    '> 401/403/429 responses are reported as protected/rate-limited rather than broken because many government portals block automated requests.',
    '> Transient server errors, timeouts, and network failures are retried once before being reported.',
    '> Link failures do not fail the site deployment; this audit is advisory.'
  );

  return lines.join('\n') + '\n';
}

(async () => {
  const entries = loadDirectory();
  if (!entries.length) throw new Error('No direct HTTPS property-tax portals found.');

  console.log(`Checking ${entries.length} unique direct property-tax portals with concurrency ${CONCURRENCY}...`);
  const results = await mapConcurrent(entries, inspect, CONCURRENCY);

  const report = {
    generatedAt: new Date().toISOString(),
    source: DATA_FILE,
    total: results.length,
    counts: results.reduce((acc, r) => {
      acc[r.category] = (acc[r.category] || 0) + 1;
      return acc;
    }, {}),
    results
  };

  fs.writeFileSync(OUTPUT_JSON, JSON.stringify(report, null, 2) + '\n');
  fs.writeFileSync(OUTPUT_MD, markdown(results));
  console.log(`Wrote ${OUTPUT_JSON} and ${OUTPUT_MD}.`);
})().catch(error => {
  console.error(error && error.stack || error);
  process.exit(1);
});
