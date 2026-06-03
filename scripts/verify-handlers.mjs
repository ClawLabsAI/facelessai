// One-off: verify every inline event-handler function referenced in the HTML still has a
// definition in the (minified) JS. Guards against a build dropping/renaming a global handler.
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const file = process.argv[2] ? join(root, process.argv[2]) : join(root, 'dist/index.html');
const html = readFileSync(file, 'utf8');

const names = new Set();
const handlerRe = /\son[a-z]+="([A-Za-z_$][\w$]*)\s*\(/g;
let m;
while ((m = handlerRe.exec(html))) names.add(m[1]);

const js = (html.match(/<script\b[^>]*>([\s\S]*?)<\/script>/gi) || []).join('\n');

const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const missing = [];
for (const n of names) {
  const e = esc(n);
  const present =
    new RegExp('function\\s+' + e + '\\b').test(js) ||
    new RegExp('\\b' + e + '\\s*=\\s*(async\\s+)?function').test(js) ||
    new RegExp('\\b' + e + '\\s*=\\s*(async\\s+)?\\(').test(js) ||  // arrow assignment
    new RegExp('\\b' + e + '\\s*=\\s*[A-Za-z_$]').test(js) ||       // aliased
    new RegExp('window\\.' + e + '\\b').test(js);
  if (!present) missing.push(n);
}

console.log('Checking ' + file.replace(root, '.'));
console.log('Unique inline-handler functions referenced: ' + names.size);
if (missing.length) {
  console.error('MISSING definitions (' + missing.length + '): ' + missing.join(', '));
  process.exit(1);
}
console.log('All handler functions have a definition. ✓');
