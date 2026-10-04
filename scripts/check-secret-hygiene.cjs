#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const tracked = execFileSync('git', ['ls-files', '-z'], { encoding: 'utf8' })
  .split('\0')
  .filter(Boolean);

const failures = [];
const envTemplateSuffixes = ['.example', '.sample', '.template'];

function isEnvFile(file) {
  const base = path.basename(file);
  if (base === '.env') return true;
  if (!base.startsWith('.env.')) return false;
  return !envTemplateSuffixes.some(suffix => base.endsWith(suffix));
}

for (const file of tracked) {
  if (isEnvFile(file)) {
    failures.push(`${file}: tracked environment file must not be committed`);
  }
}

const binaryExt = new Set([
  '.png','.jpg','.jpeg','.gif','.webp','.ico','.pdf','.exe','.zip','.gz','.woff','.woff2','.ttf','.eot'
]);

const tokenPatterns = [
  ['Stripe secret key', /\bsk_(?:live|test)_[A-Za-z0-9]{16,}\b/],
  ['GitHub token', /\bgh[pousr]_[A-Za-z0-9_]{20,}\b/],
  ['AWS access key', /\bAKIA[0-9A-Z]{16}\b/],
  ['Private key', /-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----/]
];

const assignmentPattern = /^\s*(ADMIN_PASSWORD|SECRET_KEY|POSTGRES_PASSWORD|DATABASE_URL|STRIPE_SECRET_KEY|STRIPE_WEBHOOK_SECRET|LICENSE_SECRET)\s*=\s*(.+?)\s*$/;

function looksPlaceholder(value) {
  const v = value.trim().replace(/^["']|["']$/g, '');
  return !v ||
    /^<[^>]+>$/.test(v) ||
    /^\$\{[^}]+\}$/.test(v) ||
    /^(changeme|change-me|replace[_-]?me|your[_-]|example|dummy|placeholder)/i.test(v);
}

for (const file of tracked) {
  const ext = path.extname(file).toLowerCase();
  if (binaryExt.has(ext)) continue;

  let stat;
  try {
    stat = fs.statSync(file);
  } catch (_) {
    continue;
  }
  if (!stat.isFile() || stat.size > 2_000_000) continue;

  let content;
  try {
    content = fs.readFileSync(file, 'utf8');
  } catch (_) {
    continue;
  }

  for (const [label, pattern] of tokenPatterns) {
    if (pattern.test(content)) failures.push(`${file}: contains a value matching ${label}`);
  }

  const base = path.basename(file);
  const isTemplate = envTemplateSuffixes.some(suffix => base.endsWith(suffix));
  if (isTemplate) continue;

  for (const line of content.split(/\r?\n/)) {
    const match = line.match(assignmentPattern);
    if (match && !looksPlaceholder(match[2])) {
      failures.push(`${file}: contains a non-placeholder assignment for ${match[1]}`);
    }
  }
}

const uniqueFailures = [...new Set(failures)];
if (uniqueFailures.length) {
  console.error('Secret hygiene check failed:');
  uniqueFailures.forEach(item => console.error(' - ' + item));
  process.exit(1);
}

console.log(`Secret hygiene check passed for ${tracked.length} tracked files.`);
