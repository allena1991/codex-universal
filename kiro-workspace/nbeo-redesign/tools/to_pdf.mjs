/* Print the manual to PDF through Chromium's own print engine.
   The document owns its page geometry (@page size: letter, margin: 0, one
   .sheet per page), so preferCSSPageSize is on and no margins are added here.
   Run: node tools/to_pdf.mjs <input.html> <out.pdf> */
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { statSync, existsSync } from 'node:fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const src = resolve(root, process.argv[2] || 'volume-1.html');
const out = resolve(root, process.argv[3] || src.replace(/\.html$/, '.pdf'));

/* This image ships Chromium under PLAYWRIGHT_BROWSERS_PATH at a revision the
   installed playwright package does not expect, so point at it explicitly. */
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(
  existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage();
const problems = [];
page.on('pageerror', e => problems.push(String(e)));
page.on('requestfailed', r => problems.push(`asset failed: ${r.url()}`));

await page.goto(pathToFileURL(src).href, { waitUntil: 'networkidle' });
await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 20000 });

const loadedFonts = await page.evaluate(() =>
  [...new Set([...document.fonts].filter(f => f.status === 'loaded').map(f => f.family))].sort());
const sheets = await page.evaluate(() => document.querySelectorAll('.sheet').length);

await page.emulateMedia({ media: 'print' });
await page.pdf({
  path: out,
  preferCSSPageSize: true,
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 }
});
await browser.close();

console.log('wrote', out);
console.log('size', (statSync(out).size / 1024 / 1024).toFixed(2), 'MB');
console.log('sheets in source:', sheets);
console.log('fonts loaded:', loadedFonts.join(', ') || 'none');
console.log('problems:', problems.length ? problems : 'none');
