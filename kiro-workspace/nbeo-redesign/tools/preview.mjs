/* Render named sheets to preview/ as PNG, for review without opening the PDF.
   Labels are the data-screen-label values; tools/shoot.mjs --all lists them.

   node tools/preview.mjs volume-1.html                     representative set
   node tools/preview.mjs volume-1.html "Cover" "S1-14 key" specific sheets */
import { chromium } from 'playwright';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import { mkdirSync, existsSync } from 'node:fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT = ['Cover', 'Key integrity', 'Exam map', 'Item types',
                 'Emergency gate 1', 'Conditions 2', 'Pharmacology 2',
                 'Competing pairs 1', 'Session 1 divider', 'S1 case index',
                 'S1 score sheet', 'S1-14 case', 'S1-14 key', 'S2-33 case',
                 'S2-33 key', 'Answer key', 'Schedule', 'Colophon'];
const argv = process.argv.slice(2);
const src = argv.length && argv[0].endsWith('.html') ? argv.shift() : 'volume-1.html';
const want = argv.length ? argv : DEFAULT;

mkdirSync(resolve(root, 'preview'), { recursive: true });
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage({ viewportSize: { width: 1100, height: 1400 },
                                     deviceScaleFactor: 2 });
await page.goto(pathToFileURL(resolve(root, src)).href, { waitUntil: 'load' });
await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 30000 })
  .catch(() => console.log('note: font loading timed out'));
await page.waitForTimeout(400);

const numbers = await page.evaluate(() => Object.fromEntries(
  [...document.querySelectorAll('.sheet')].map((s, i) => [s.dataset.screenLabel, i + 1])));

for (const label of want) {
  const el = await page.$(`.sheet[data-screen-label="${label}"]`);
  if (!el) { console.log('missing sheet:', label); continue; }
  const n = String(numbers[label]).padStart(3, '0');
  const slug = label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const vol = src.match(/volume-(\d)/) ? `v${src.match(/volume-(\d)/)[1]}-` : '';
  const file = resolve(root, `preview/${vol}p${n}-${slug}.png`);
  await el.screenshot({ path: file });
  console.log('wrote', file.replace(root + '/', ''));
}
await browser.close();
