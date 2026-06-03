#!/usr/bin/env node
// ─────────────────────────────────────────────────────────────────────────────
// FacelessAI static checker (B14). No build system — this is the project's CI gate.
// Runs against the single index.html: validates inline JS syntax, flags duplicate
// top-level function declarations, empty catch blocks, and leftover debug markers.
// Exit code 0 = pass, 1 = fail. Run with: npm test
// ─────────────────────────────────────────────────────────────────────────────
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import vm from 'node:vm';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const file = join(root, 'index.html');
const html = readFileSync(file, 'utf8');

let failures = 0;
const fail = (msg) => { console.error('  ✗ ' + msg); failures++; };
const ok   = (msg) => console.log('  ✓ ' + msg);

// 1) Inline <script> syntax ----------------------------------------------------
console.log('JS syntax (inline <script> blocks):');
const scriptRe = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let m, scriptCount = 0, syntaxBad = 0;
const scripts = [];
while ((m = scriptRe.exec(html))) {
  scriptCount++;
  const code = m[1];
  if (!code.trim()) continue;
  scripts.push(code);
  try { new vm.Script(code); }
  catch (e) { fail(`script #${scriptCount} syntax error: ${e.message}`); syntaxBad++; }
}
if (!syntaxBad) ok(`${scriptCount} blocks parsed, 0 syntax errors`);

const allJs = scripts.join('\n');

// 2) Duplicate top-level function declarations ---------------------------------
console.log('Duplicate function declarations:');
const fnRe = /(^|\n)\s*function\s+([A-Za-z0-9_]+)\s*\(/g;
const counts = {};
while ((m = fnRe.exec(allJs))) counts[m[2]] = (counts[m[2]] || 0) + 1;
const dups = Object.entries(counts).filter(([, v]) => v > 1);
if (dups.length) dups.forEach(([k, v]) => fail(`${k} declared ${v}×`));
else ok('no duplicate named functions');

// 3) Empty catch blocks (must use _diag) ---------------------------------------
console.log('Empty catch blocks:');
// try/catch only: a single identifier param (excludes promise .catch(function(){})), not
// preceded by '.' or a word char (excludes `.catch`). A `{ }` with a comment is non-empty.
const emptyCatch = (allJs.match(/(?<![.\w])catch\s*\(\s*[A-Za-z_$][\w$]*\s*\)\s*\{\s*\}/g) || []).length;
if (emptyCatch) fail(`${emptyCatch} empty catch block(s) — use _diag(e) instead`);
else ok('no empty catch blocks');

// 4) Leftover debug markers ----------------------------------------------------
console.log('Debug markers:');
const debuggers = (allJs.match(/\bdebugger\b/g) || []).length;
if (debuggers) fail(`${debuggers} debugger statement(s) left in code`);
else ok('no debugger statements');

// 5) Single-file invariant -----------------------------------------------------
console.log('Deploy invariant:');
if (/<script\s+[^>]*\bsrc=/i.test(html)) fail('external <script src> found — app must stay a single self-contained file');
else ok('no external script dependencies (single-file deploy intact)');

// ─────────────────────────────────────────────────────────────────────────────
console.log('');
if (failures) { console.error(`FAILED — ${failures} problem(s).`); process.exit(1); }
console.log('All checks passed.');
