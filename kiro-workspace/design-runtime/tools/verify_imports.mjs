/* Exercises dc-import and x-import, which the main smoke test does not reach.
   Run with node (not bun): node tools/verify_imports.mjs */
import { readFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { JSDOM, VirtualConsole } from 'jsdom';

const dir = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const target = resolve(dir, 'Imports.dc.html');

let html = readFileSync(target, 'utf8')
  .replace(/https:\/\/unpkg\.com\/react@[\d.]+\/umd\/react\.[a-z.]*js/, 'node_modules/react/umd/react.development.js')
  .replace(/https:\/\/unpkg\.com\/react-dom@[\d.]+\/umd\/react-dom\.[a-z.]*js/, 'node_modules/react-dom/umd/react-dom.development.js');

const logs = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => logs.push('jsdomError: ' + e.message));
for (const level of ['error', 'warn']) vc.on(level, (...a) => logs.push(level + ': ' + a.join(' ')));

const dom = new JSDOM(html, {
  url: pathToFileURL(target).href,
  runScripts: 'dangerously',
  resources: 'usable',
  pretendToBeVisual: true,
  virtualConsole: vc,
  // jsdom has no fetch; the runtime uses it to pull sibling .dc.html files.
  beforeParse(window) {
    window.fetch = async (url) => {
      const path = resolve(dir, String(url).replace(/^\.\//, ''));
      if (!existsSync(path)) return { ok: false, status: 404, text: async () => '' };
      return { ok: true, status: 200, text: async () => readFileSync(path, 'utf8') };
    };
  }
});

await new Promise(r => dom.window.addEventListener('load', r, { once: true }));
await new Promise(r => setTimeout(r, 800));

const root = dom.window.document.getElementById('dc-root');
const markup = root ? root.innerHTML : '';

const checks = [
  ['child DC mounted', markup.includes('Ready to ship')],
  ['child DC read its prop through the template', /<span[^>]*>Ready to ship<\/span>/.test(markup)],
  ['no dc-import placeholder left', !markup.includes('>Chip<')],
  ['web component tag rendered', markup.includes('<demo-badge')],
  ['web component received attributes', /tone="warn"/.test(markup)],
  ['web component children passed through', markup.includes('Needs review')],
  ['custom element upgraded', !!dom.window.customElements.get('demo-badge')],
  ['no console errors', !logs.some(l => l.startsWith('error') || l.startsWith('jsdomError'))]
];

let failed = 0;
for (const [name, ok] of checks) {
  if (!ok) failed++;
  console.log(`${ok ? 'pass' : 'FAIL'}  ${name}`);
}
if (failed) console.log('\nrendered:\n' + markup);
if (logs.length) {
  console.log('\nconsole output:');
  for (const l of logs) console.log('  ' + l);
}
console.log(`\n${failed === 0 ? 'all checks passed' : failed + ' check(s) failed'}`);
process.exit(failed === 0 ? 0 : 1);
