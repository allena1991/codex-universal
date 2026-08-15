/* Which characters are not covered by the three embedded families?
   Those are the ones Chromium renders, and embeds, in a fallback face. */
import { chromium } from 'playwright';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { existsSync, readFileSync } from 'node:fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage();
await page.goto(pathToFileURL(resolve(root, 'index.html')).href, { waitUntil: 'networkidle' });
await page.waitForFunction(() => document.fonts.status === 'loaded');

// every non-ASCII character actually present in the rendered document
const chars = await page.evaluate(() => {
  const text = document.body.innerText;
  return [...new Set([...text].filter(c => c.charCodeAt(0) > 126))].sort();
});

const report = await page.evaluate((chars) => {
  const families = ['Spectral', 'Instrument Serif', 'IBM Plex Mono'];
  return chars.map(c => ({
    c,
    code: 'U+' + c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0'),
    covered: families.filter(f => document.fonts.check(`12pt "${f}"`, c))
  }));
}, chars);

console.log('non-ASCII characters in the document:', report.length);
for (const r of report) {
  console.log(`  ${r.c}  ${r.code}  ${r.covered.length ? 'covered by ' + r.covered.join(', ') : 'NOT COVERED -> fallback face'}`);
}
await browser.close();
