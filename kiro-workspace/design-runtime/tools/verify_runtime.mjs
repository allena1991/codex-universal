/* Smoke test for the Design Component runtime.
   Run with: bun tools/verify_runtime.mjs Roadmap.dc.html   (from the design/ directory) */
import { readFileSync } from 'node:fs';
import { resolve, dirname, basename } from 'node:path';
import { pathToFileURL } from 'node:url';
import { JSDOM, VirtualConsole } from 'jsdom';

const target = resolve(process.argv[2] || 'Roadmap.dc.html');
const dir = dirname(target);

let html = readFileSync(target, 'utf8')
  .replace(/https:\/\/unpkg\.com\/react@[\d.]+\/umd\/react\.[a-z.]*js/, 'node_modules/react/umd/react.development.js')
  .replace(/https:\/\/unpkg\.com\/react-dom@[\d.]+\/umd\/react-dom\.[a-z.]*js/, 'node_modules/react-dom/umd/react-dom.development.js');

const logs = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => logs.push('jsdomError: ' + e.message));
for (const level of ['error', 'warn']) vc.on(level, (...a) => logs.push(level + ': ' + a.join(' ')));

const dom = new JSDOM(html, {
  url: pathToFileURL(resolve(dir, basename(target))).href,
  runScripts: 'dangerously',
  resources: 'usable',
  pretendToBeVisual: true,
  virtualConsole: vc
});

await new Promise(r => dom.window.addEventListener('load', r, { once: true }));
await new Promise(r => setTimeout(r, 400));

const { document } = dom.window;
const root = document.getElementById('dc-root');
const markup = root ? root.innerHTML : '';
const headCss = [...document.querySelectorAll('head style')].map(s => s.textContent).join('\n');

const checks = [
  ['mounted something', markup.length > 200],
  ['static markup rendered', markup.includes('Release readiness')],
  ['renderVals hole resolved', markup.includes('2/4 ready')],
  ['sc-for expanded every row', /Streaming template compiler/.test(markup) && /Props and tweak metadata/.test(markup)],
  ['sc-for scope value used', markup.includes('>01<') && markup.includes('>04<')],
  ['sc-if true branch shown', markup.includes('Priya')],
  ['sc-if false branch hidden', !markup.includes('>Review</span>') === false],
  ['per-row conditional chips', markup.includes('Shipped') && markup.includes('Blocked')],
  ['inline style compiled to style attr', /style="[^"]*display: ?grid/.test(markup)],
  ['pseudo-state class applied', /class="dc-s\d+"/.test(markup)],
  ['pseudo-state rule injected', /\.dc-s\d+:hover\{/.test(headCss.replace(/\s/g, ''))],
  ['helmet keyframes hoisted', headCss.includes('@keyframes dc-rise')],
  ['helmet link colors hoisted', headCss.includes('a:hover')],
  ['handler attached (button present)', /<button[^>]*>Hide owners<\/button>/.test(markup)],
  ['runtime flagged ready', document.documentElement.hasAttribute('data-dc-ready')],
  ['no console errors', !logs.some(l => l.startsWith('error') || l.startsWith('jsdomError'))]
];

let failed = 0;
for (const [name, ok] of checks) {
  if (!ok) failed++;
  console.log(`${ok ? 'pass' : 'FAIL'}  ${name}`);
}

// interaction: click the footer button and confirm state flips
const button = root && root.querySelector('button');
if (button) {
  button.dispatchEvent(new dom.window.MouseEvent('click', { bubbles: true }));
  await new Promise(r => setTimeout(r, 120));
  const after = root.innerHTML;
  const ok = after.includes('Show owners') && !after.includes('Priya');
  if (!ok) failed++;
  console.log(`${ok ? 'pass' : 'FAIL'}  setState re-render hides owners`);
}

if (logs.length) {
  console.log('\nconsole output:');
  for (const l of logs) console.log('  ' + l);
}

console.log(`\n${failed === 0 ? 'all checks passed' : failed + ' check(s) failed'}`);
process.exit(failed === 0 ? 0 : 1);
