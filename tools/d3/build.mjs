// Bundles entry.mjs into <site>/d3.min.js as the global `d3`, writes <site>/d3-LICENSE.txt, and fails if app.js
// calls a d3 function the bundle does not export. Usage: node build.mjs [path/to/website]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.resolve(process.argv[2] || path.join(here, '../../website'));
const version = (m) => JSON.parse(fs.readFileSync(path.join(here, 'node_modules', m, 'package.json'), 'utf8')).version;

const out = await build({
  entryPoints: [path.join(here, 'entry.mjs')], bundle: true, minify: true, format: 'iife', globalName: 'd3',
  target: ['es2018'], legalComments: 'none', write: false, metafile: true,
});
const used = Object.keys(out.metafile.inputs).map((f) => (f.match(/node_modules\/((?:@[^/]+\/)?[^/]+)\//) || [])[1]).filter(Boolean);
const inBundle = [...new Set(used)].sort();
const header = `// d3 for the PACK3D page, built by tools/d3 from: ${inBundle.map((m) => `${m}@${version(m)}`).join(', ')}.\n` +
  '// Copyright 2010-2023 Mike Bostock; d3-ease also Copyright 2001 Robert Penner. ISC and BSD-3-Clause: see d3-LICENSE.txt.\n';
const code = header + out.outputFiles[0].text;

// every d3.<name> in app.js must be in the bundle (one in a comment counts too, to stay on the safe side), and so
// must selection.transition() when app.js animates a selection
const d3 = new Function(`${code}; return d3;`)();
const app = fs.readFileSync(path.join(site, 'app.js'), 'utf8');
const calls = [...new Set([...app.matchAll(/\bd3\.([A-Za-z_$][\w$]*)/g)].map((m) => m[1]))].sort();
const missing = calls.filter((n) => !(n in d3));
if (/\.transition\(/.test(app) && typeof d3.selection.prototype.transition !== 'function') missing.push('selection.transition');
if (missing.length) {
  console.error(`app.js uses d3 functions this bundle lacks: ${missing.join(', ')}. Add their module to entry.mjs.`);
  process.exit(1);
}

fs.writeFileSync(path.join(site, 'd3.min.js'), code);
// the license file: every module's own copyright lines, under each distinct license text (most are ISC;
// d3-ease is BSD-3-Clause, for Robert Penner's easing equations)
const groups = new Map();
for (const m of inBundle) {
  const text = fs.readFileSync(path.join(here, 'node_modules', m, 'LICENSE'), 'utf8').replace(/\r/g, '').trim();
  const cut = text.indexOf('\n\n');
  const head = text.slice(0, cut).trim(), body = text.slice(cut).trim();
  if (!groups.has(body)) groups.set(body, []);
  groups.get(body).push(`${m} ${version(m)}:\n${head}`);
}
fs.writeFileSync(path.join(site, 'd3-LICENSE.txt'),
  'website/d3.min.js bundles these modules of d3 (https://d3js.org). tools/d3 builds it.\n\n' +
  [...groups].map(([body, heads]) => `${heads.join('\n\n')}\n\n${body}\n`).join(`\n${'-'.repeat(78)}\n\n`));
console.log(`wrote ${path.join(site, 'd3.min.js')}: ${code.length} bytes; app.js uses d3.${calls.join(', d3.')}; all present.`);
