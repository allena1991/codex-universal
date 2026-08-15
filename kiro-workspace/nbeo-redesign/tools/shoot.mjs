/* Measure every sheet in a real Chromium render and fail if any page is clipped.
   Sheets are a fixed 11in box with overflow hidden, so a page that is too full
   loses content silently in print. This is the only check that catches it.

   node tools/shoot.mjs volume-1.html         measure, report clipped and tight
   node tools/shoot.mjs volume-1.html --all   list every sheet, not just problems
   With no file argument it checks both volumes. */
import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const listAll = args.includes('--all');
const files = args.filter(a => !a.startsWith('--'));
if (!files.length) files.push('volume-1.html', 'volume-2.html');

/* This image ships Chromium under PLAYWRIGHT_BROWSERS_PATH at a revision the
   installed playwright package does not expect, so point at it explicitly. */
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage({ viewportSize: { width: 1100, height: 1400 } });
const errors = [];
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('pageerror', e => errors.push(String(e)));

let failed = 0;
for (const file of files) {
await page.goto(pathToFileURL(resolve(root, file)).href, { waitUntil: 'load' });
await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 30000 })
  .catch(() => console.log('note: font loading timed out, measurements may drift'));
await page.waitForTimeout(400);

const sheets = await page.evaluate(() => {
  const maxH = 11 * 96 + 2;
  return [...document.querySelectorAll('.sheet')].map((s, i) => {
    const box = Math.round(s.getBoundingClientRect().height);
    const clipped = s.scrollHeight - s.clientHeight;
    /* The footer is bottom-anchored, so slack is the gap between the last
       content block and the footer, in points, directly comparable with the
       cost model in tools/render.py. */
    const foot = s.querySelector('.rf');
    const kids = [...s.children].filter(k => !k.classList.contains('rf')
      && !k.classList.contains('rh'));
    const lastContent = kids[kids.length - 1];
    let gap = 0;
    if (lastContent) {
      const bottom = lastContent.getBoundingClientRect().bottom;
      const limit = foot ? foot.getBoundingClientRect().top
        : s.getBoundingClientRect().bottom - parseFloat(getComputedStyle(s).paddingBottom);
      gap = Math.round((limit - bottom) * 0.75);
    }
    return { i: i + 1, label: s.dataset.screenLabel || '', h: box, clipped, gap,
             over: box > maxH || clipped > 1 };
  });
});

const bad = sheets.filter(s => s.over);
const tight = sheets.filter(s => !s.over && s.gap < 6);
const show = listAll ? sheets : [...bad, ...tight];

console.log(`${file}: ${sheets.length} sheets, clipped ${bad.length}, tight (<6pt slack) ${tight.length}`);
for (const s of show) {
  const state = s.clipped > 1 ? `CLIPPED by ${s.clipped}px` : `fits, ${s.gap}pt slack`;
  console.log(`  ${String(s.i).padStart(3, '0')}  ${String(s.h).padStart(4)}px  ${state.padEnd(20)}  ${s.label}`);
}

const slack = sheets.filter(s => !s.over).map(s => s.gap).sort((a, b) => a - b);
if (slack.length) {
  const q = p => slack[Math.floor((slack.length - 1) * p)];
  console.log(`slack in points: min ${q(0)}, p10 ${q(0.1)}, median ${q(0.5)}, max ${q(1)}`);
}

failed += bad.length;
}

console.log('console errors:', errors.length ? errors.slice(0, 5) : 'none');
await browser.close();
process.exit(failed || errors.length ? 1 : 0);
