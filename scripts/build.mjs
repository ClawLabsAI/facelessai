#!/usr/bin/env node
// ─────────────────────────────────────────────────────────────────────────────
// OPTIONAL minification build (B10). Produces dist/index.html from the canonical
// single-file index.html by minifying the JS inside each <script> block. The source
// index.html stays the editable, deployable file — dist/ is an opt-in smaller artifact.
//
// SAFETY: the app wires behavior through inline on*="globalFn()" handlers in the HTML,
// so terser MUST NOT rename or drop top-level names. We force mangle:false and
// compress.toplevel:false. HTML/CSS are left byte-for-byte intact (only <script> bodies
// change) to avoid touching templates, <pre>, or significant whitespace.
//
// Run: npm run build   (then optionally verify dist with: npm run check:dist)
// ─────────────────────────────────────────────────────────────────────────────
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { minify } from 'terser';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(join(root, 'app.html'), 'utf8');

const scriptRe = /(<script\b[^>]*>)([\s\S]*?)(<\/script>)/gi;
const segs = [];
let m;
while ((m = scriptRe.exec(html))) segs.push({ open: m[1], code: m[2], close: m[3], start: m.index, end: scriptRe.lastIndex });

let out = '', cursor = 0, blocks = 0, kept = 0;
for (const seg of segs) {
  out += html.slice(cursor, seg.start);
  if (!seg.code.trim()) { out += seg.open + seg.code + seg.close; cursor = seg.end; continue; }
  blocks++;
  let code = seg.code;
  try {
    const r = await minify(seg.code, {
      mangle: false,                                   // keep names used by inline on* handlers
      compress: { toplevel: false, passes: 1, drop_console: false }, // never drop top-level decls
      format: { comments: false }
    });
    if (r.code && r.code.length) code = r.code; else kept++;
  } catch (e) {
    console.error('  ! terser failed on a block, keeping original:', e.message);
    kept++;
  }
  out += seg.open + code + seg.close;
  cursor = seg.end;
}
out += html.slice(cursor);

mkdirSync(join(root, 'dist'), { recursive: true });
writeFileSync(join(root, 'dist', 'app.html'), out, 'utf8');

const before = Buffer.byteLength(html, 'utf8');
const after = Buffer.byteLength(out, 'utf8');
console.log(`Minified ${blocks} <script> block(s)${kept ? ` (${kept} kept as-is)` : ''}.`);
console.log(`Size: ${(before / 1024).toFixed(0)} KB -> ${(after / 1024).toFixed(0)} KB  (${(100 * (1 - after / before)).toFixed(1)}% smaller)`);
console.log('Wrote dist/app.html');
