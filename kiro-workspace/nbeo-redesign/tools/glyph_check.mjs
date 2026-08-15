/* Find which characters force Chromium to embed a fallback face.
   document.fonts.check lies about coverage, so this proves it the only way that
   works: export a copy with a character removed and diff the embedded fonts.

   node tools/glyph_check.mjs            test build/no-*.html against index.html
   Prepare the copies first; tools/build.py leaves them in build/. */
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync, existsSync, readdirSync, unlinkSync } from 'node:fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage();

async function fontsOf(htmlPath) {
  const pdf = htmlPath + '.pdf';
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: 'load' });
  await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 30000 })
    .catch(() => {});
  await page.emulateMedia({ media: 'print' });
  await page.pdf({ path: pdf, preferCSSPageSize: true, printBackground: true });
  const raw = readFileSync(pdf, 'latin1');
  const names = [...raw.matchAll(/\/BaseFont\s*\/([A-Za-z0-9+\-,_]+)/g)]
    .map(m => m[1].split('+').pop());
  unlinkSync(pdf);
  return [...new Set(names)].sort();
}

const base = await fontsOf(resolve(root, 'index.html'));
console.log('index.html          ', base.join(', '));

for (const file of readdirSync(resolve(root, 'build')).filter(f => f.startsWith('no-'))) {
  const fonts = await fontsOf(resolve(root, 'build', file));
  const gone = base.filter(f => !fonts.includes(f));
  console.log(basename(file).padEnd(20), fonts.join(', '));
  console.log('  removing that character drops:', gone.length ? gone.join(', ') : 'nothing');
}

await browser.close();
