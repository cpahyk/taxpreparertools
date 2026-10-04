#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const STRICT = process.argv.includes('--strict') || process.env.SITE_AUDIT_STRICT === '1';
const OUTPUT_JSON = process.env.SITE_AUDIT_JSON || 'site-audit.json';
const OUTPUT_MD = process.env.SITE_AUDIT_MD || 'site-audit.md';

function walk(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    if (['.git','.wrangler','node_modules'].includes(entry.name)) return [];
    const full = path.join(dir, entry.name);
    return entry.isDirectory() ? walk(full) : [full];
  });
}

function attr(tag, name) {
  const match = tag.match(new RegExp('\\b' + name + '\\s*=\\s*["\\\']([^"\\\']*)["\\\']','i'));
  return match ? match[1] : '';
}

function sitemapFiles() {
  if (!fs.existsSync('sitemap.xml')) return new Set();
  const xml = fs.readFileSync('sitemap.xml','utf8');
  const urls = [...xml.matchAll(/<loc>(.*?)<\/loc>/g)].map(m => m[1]);
  const files = new Set();

  for (const value of urls) {
    try {
      const pathname = new URL(value).pathname;
      let file;
      if (pathname === '/') file = 'index.html';
      else if (pathname.endsWith('/')) file = pathname.slice(1) + 'index.html';
      else file = pathname.slice(1) + '.html';
      if (fs.existsSync(file)) files.add(path.normalize(file));
    } catch (_) {}
  }
  return files;
}

const sitemap = sitemapFiles();
const excludedTheme = new Set(['fo-verify.html']);
const htmlFiles = walk('.').filter(file => file.endsWith('.html')).map(file => file.replace(/^\.\//,'')).sort();
const issues = [];
const pages = [];

function add(file, severity, code, message) {
  issues.push({ file, severity, code, message });
}

for (const file of htmlFiles) {
  const html = fs.readFileSync(file,'utf8');
  const noindex = /<meta[^>]+name=["']robots["'][^>]+content=["'][^"']*noindex/i.test(html);
  const inSitemap = sitemap.has(path.normalize(file));
  const title = html.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.trim() || '';
  const description = html.match(/<meta[^>]+name=["']description["'][^>]+content=["']([^"']+)["']/i)?.[1]?.trim() || '';
  const canonical = html.match(/<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']+)["']/i)?.[1]?.trim()
    || html.match(/<link[^>]+href=["']([^"']+)["'][^>]+rel=["']canonical["']/i)?.[1]?.trim()
    || '';
  const h1Count = (html.match(/<h1\b/gi) || []).length;
  const hasMain = /<main\b|role=["']main["']/i.test(html);
  const usesTheme = /professional-light\.css/.test(html);
  const hasViewport = /<meta[^>]+name=["']viewport["']/i.test(html);
  const hasLang = /<html[^>]+lang=["'][^"']+["']/i.test(html);
  const hasCharset = /<meta[^>]+charset=/i.test(html);

  if (!title) add(file,'error','missing-title','Missing <title>.');
  if (!hasViewport) add(file,'error','missing-viewport','Missing viewport meta tag.');
  if (!hasLang) add(file,'error','missing-lang','Missing language on <html>.');
  if (!hasCharset) add(file,'warning','missing-charset','Missing charset declaration.');
  if (!excludedTheme.has(file) && !usesTheme) add(file,'error','missing-theme','Missing professional-light.css.');

  if (inSitemap && !noindex) {
    if (!description) add(file,'error','missing-description','Indexable sitemap page has no meta description.');
    if (!canonical) add(file,'error','missing-canonical','Indexable sitemap page has no canonical URL.');
    if (h1Count !== 1) add(file,'error','h1-count',`Expected one H1 on indexable page; found ${h1Count}.`);
    if (!hasMain) add(file,'warning','missing-main','Indexable page has no <main> or role="main" landmark.');
  }

  const htmlForDomChecks = html
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '');

  const ids = [...htmlForDomChecks.matchAll(/\bid=["']([^"']+)["']/gi)].map(m => m[1]);
  const seen = new Set();
  for (const id of ids) {
    if (seen.has(id)) add(file,'error','duplicate-id',`Duplicate id="${id}".`);
    seen.add(id);
  }

  const anchors = [...htmlForDomChecks.matchAll(/<a\b[^>]*>/gi)].map(m => m[0]);
  for (const tag of anchors) {
    if (attr(tag,'target').toLowerCase() !== '_blank') continue;
    const rel = attr(tag,'rel').toLowerCase().split(/\s+/).filter(Boolean);
    if (!rel.includes('noopener')) {
      add(file,'error','unsafe-blank','target="_blank" link is missing rel="noopener".');
    }
  }

  for (const tag of anchors) {
    const href = attr(tag,'href').trim().toLowerCase();
    if (href !== '#' && href !== 'javascript:void(0)' && href !== 'javascript:void(0);') continue;
    const hasHandler = /\bonclick\s*=/.test(tag) || !!attr(tag,'id').trim();
    if (!hasHandler) {
      add(file,'warning','dead-placeholder-link','Placeholder link has no id or inline handler and may be non-functional.');
    }
  }

  if (/\balert\s*\(/.test(html) || /\bprompt\s*\(/.test(html)) {
    add(file,'error','native-dialog','Uses browser alert()/prompt() instead of inline UI.');
  }

  const images = [...htmlForDomChecks.matchAll(/<img\b[^>]*>/gi)].map(m => m[0]);
  for (const tag of images) {
    if (!/\balt\s*=/.test(tag)) add(file,'warning','missing-img-alt','Image tag is missing alt attribute.');
  }

  const labelTargets = new Set(
    [...htmlForDomChecks.matchAll(/<label\b[^>]*\bfor=["']([^"']+)["'][^>]*>/gi)].map(m => m[1])
  );
  const controls = [...htmlForDomChecks.matchAll(/<(input|select|textarea)\b[^>]*>/gi)];
  for (const match of controls) {
    const tag = match[0];
    const tagName = match[1].toLowerCase();
    const type = tagName === 'input' ? attr(tag,'type').toLowerCase() : '';
    if (tagName === 'input' && ['hidden','submit','button','reset','image'].includes(type)) continue;

    const id = attr(tag,'id');
    const hasExplicitName =
      !!attr(tag,'aria-label').trim() ||
      !!attr(tag,'aria-labelledby').trim() ||
      !!attr(tag,'title').trim() ||
      (!!id && labelTargets.has(id));

    const before = htmlForDomChecks.slice(0, match.index);
    const nestedInLabel = before.lastIndexOf('<label') > before.lastIndexOf('</label>');

    if (!hasExplicitName && !nestedInLabel) {
      add(file,'warning','unnamed-form-control',`${tagName} control is missing an associated label or accessible name.`);
    }
  }

  const buttons = [...htmlForDomChecks.matchAll(/<button\b([^>]*)>([\s\S]*?)<\/button>/gi)];
  for (const match of buttons) {
    const tag = '<button' + match[1] + '>';
    const text = match[2].replace(/<[^>]+>/g,' ').replace(/&nbsp;/gi,' ').replace(/\s+/g,' ').trim();
    const hasName = text || attr(tag,'aria-label').trim() || attr(tag,'aria-labelledby').trim() || attr(tag,'title').trim();
    if (!hasName) add(file,'warning','unnamed-button','Button is missing visible text or an accessible name.');
  }

  const iframes = [...htmlForDomChecks.matchAll(/<iframe\b[^>]*>/gi)].map(m => m[0]);
  for (const tag of iframes) {
    if (!attr(tag,'title').trim()) add(file,'warning','missing-iframe-title','Iframe is missing a descriptive title attribute.');
  }

  const forms = [...htmlForDomChecks.matchAll(/<form\b[^>]*>[\s\S]*?<\/form>/gi)].map(m => m[0]);
  for (const form of forms) {
    const formButtons = [...form.matchAll(/<button\b[^>]*>/gi)].map(m => m[0]);
    for (const tag of formButtons) {
      if (!attr(tag,'type').trim()) {
        add(file,'warning','implicit-form-button','Button inside a form is missing an explicit type attribute.');
      }
    }
  }
  const inlineHandlerNames = new Set();
  const handlerAttrs = [...htmlForDomChecks.matchAll(/\bon(?:click|change|input|submit|keydown|keyup|blur|focus)\s*=\s*["']([^"']+)["']/gi)];
  const ignoredHandlerCalls = new Set([
    'if','for','while','switch','return','typeof','Number','String','Boolean','Date','Array','Object','JSON',
    'parseInt','parseFloat','encodeURIComponent','decodeURIComponent','setTimeout','setInterval',
    'requestAnimationFrame','cancelAnimationFrame','confirm','fetch'
  ]);
  for (const match of handlerAttrs) {
    for (const call of match[1].matchAll(/(?<![.\w$])([A-Za-z_$][\w$]*)\s*\(/g)) {
      if (!ignoredHandlerCalls.has(call[1])) inlineHandlerNames.add(call[1]);
    }
  }
  for (const name of inlineHandlerNames) {
    const escaped = name.replace(/[.*+?^$(){}|[\]\\]/g, '\\$&');
    const definitions = [
      new RegExp('\\bfunction\\s+' + escaped + '\\s*\\('),
      new RegExp('\\b(?:const|let|var)\\s+' + escaped + '\\s*='),
      new RegExp('\\bwindow\\.' + escaped + '\\s*='),
      new RegExp('\\b' + escaped + '\\s*=\\s*(?:async\\s+)?function\\b')
    ];
    if (!definitions.some(pattern => pattern.test(html))) {
      add(file,'warning','missing-inline-handler','Inline event handler references "' + name + '()" but no local definition was found.');
    }
  }

  pages.push({
    file,
    inSitemap,
    noindex,
    title: !!title,
    description: !!description,
    canonical: !!canonical,
    theme: usesTheme,
    viewport: hasViewport,
    lang: hasLang,
    h1Count,
    main: hasMain
  });
}

const counts = issues.reduce((acc, issue) => {
  acc[issue.severity] = (acc[issue.severity] || 0) + 1;
  acc.byCode[issue.code] = (acc.byCode[issue.code] || 0) + 1;
  return acc;
},{ error:0, warning:0, byCode:{} });

const report = {
  generatedAt: new Date().toISOString(),
  htmlFiles: htmlFiles.length,
  sitemapPages: sitemap.size,
  strict: STRICT,
  counts,
  issues,
  pages
};

fs.writeFileSync(OUTPUT_JSON, JSON.stringify(report,null,2)+'\n');

const md = [
  '# Site-wide HTML Audit',
  '',
  `Generated: ${report.generatedAt}`,
  `HTML files scanned: ${htmlFiles.length}`,
  `Sitemap-backed pages: ${sitemap.size}`,
  `Errors: ${counts.error}`,
  `Warnings: ${counts.warning}`,
  '',
  '## Issue counts',
  '',
  ...Object.entries(counts.byCode).sort((a,b)=>b[1]-a[1]).map(([code,count])=>`- **${code}**: ${count}`),
  '',
  '## Issues',
  ''
];

if (!issues.length) {
  md.push('No issues found.');
} else {
  md.push('| Severity | File | Code | Message |','|---|---|---|---|');
  for (const issue of issues) {
    md.push(`| ${issue.severity} | ${issue.file.replace(/\|/g,'\\|')} | ${issue.code} | ${issue.message.replace(/\|/g,'\\|')} |`);
  }
}

fs.writeFileSync(OUTPUT_MD, md.join('\n')+'\n');

console.log(`Site audit scanned ${htmlFiles.length} HTML files: ${counts.error} errors, ${counts.warning} warnings.`);
for (const [code,count] of Object.entries(counts.byCode).sort((a,b)=>b[1]-a[1])) {
  console.log(` - ${code}: ${count}`);
}

const actionable = issues.filter(issue => issue.severity === 'error' || !['missing-main'].includes(issue.code));
if (actionable.length) {
  console.log('Actionable site-audit findings:');
  for (const issue of actionable) {
    console.log(` [${issue.severity}] ${issue.file} :: ${issue.code} :: ${issue.message}`);
  }
}

const missingMain = issues.filter(issue => issue.code === 'missing-main').map(issue => issue.file);
if (missingMain.length) {
  console.log('Pages missing a main landmark:');
  for (const file of missingMain) console.log(' [main] ' + file);
}

console.log(`Wrote ${OUTPUT_JSON} and ${OUTPUT_MD}.`);

if (STRICT && counts.error) {
  console.error('Strict site audit failed.');
  process.exit(1);
}
