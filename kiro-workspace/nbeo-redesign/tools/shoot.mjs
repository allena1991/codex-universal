/* Render each sheet of the manual to PNG so the design can be reviewed,
   and report console errors plus any sheet that overflows a letter page.
   Run: bunx node tools/shoot.mjs  (or: node tools/shoot.mjs) */
import { chromium } from 'playwright';
import { mkdirSync, existsSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
mkdirSync(resolve(root, 'preview'), { recursive: true });

/* This image ships Chromium under PLAYWRIGHT_BROWSERS_PATH at a revision the
   installed playwright package does not expect, so point at it explicitly. */
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage({ viewportSize: { width: 1100, height: 1400 }, deviceScaleFactor: 2 });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));

await page.goto(pathToFileURL(resolve(root, 'index.html')).href, { waitUntil: 'load' });
await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 15000 }).catch(() => {});
await page.waitForTimeout(500);

const sheets = await page.$$('.sheet');
const overflow = await page.evaluate(() => {
  const dpi = 96, maxH = 11 * dpi + 2;
  return [...document.querySelectorAll('.sheet')].map((s, i) => {
    const box = Math.round(s.getBoundingClientRect().height);
    // content taller than the sheet box means it is being clipped by overflow:hidden
    const clipped = s.scrollHeight - s.clientHeight;
    const last = s.lastElementChild;
    const gap = last ? Math.round(s.getBoundingClientRect().bottom - last.getBoundingClientRect().bottom) : 0;
    return { i: i + 1, label: s.dataset.screenLabel || '', h: box, clipped,
             gap, over: box > maxH || clipped > 1 };
  });
});

for (let i = 0; i < sheets.length; i++) {
  const n = String(i + 1).padStart(2, '0');
  await sheets[i].screenshot({ path: resolve(root, `preview/sheet-${n}.png`) });
}

console.log('sheets rendered:', sheets.length);
for (const s of overflow) {
  const state = s.clipped > 1 ? `CLIPPED by ${s.clipped}px` : `fits, ${s.gap}px slack`;
  console.log(`  ${String(s.i).padStart(2, '0')}  ${String(s.h).padStart(4)}px  ${state.padEnd(22)}  ${s.label}`);
}
console.log('console errors:', errors.length ? errors : 'none');

await browser.close();
process.exit(overflow.some(s => s.over) || errors.length ? 1 : 0);
