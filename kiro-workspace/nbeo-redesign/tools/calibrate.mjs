/* Measure real block heights so the cost model in tools/render.py can be fitted
   to them instead of guessed. Prints, in points: the usable column of a sheet,
   and the height of every block on a named sheet.
   node tools/calibrate.mjs "S1-01 case" "S1-01 key" */
import { chromium } from 'playwright';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import { existsSync } from 'node:fs';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const wanted = process.argv.slice(2);
const shipped = '/opt/playwright/chromium-1232/chrome-linux64/chrome';
const browser = await chromium.launch(existsSync(shipped) ? { executablePath: shipped } : {});
const page = await browser.newPage({ viewportSize: { width: 1100, height: 1400 } });
await page.goto(pathToFileURL(resolve(root, 'index.html')).href, { waitUntil: 'load' });
await page.waitForFunction(() => document.fonts.status === 'loaded', null, { timeout: 30000 }).catch(() => {});
await page.waitForTimeout(300);

const out = await page.evaluate((wanted) => {
  const pt = px => Math.round(px * 0.75 * 10) / 10;
  const report = [];
  const first = document.querySelector('.sheet:not(.cover):not(.divider)');
  const cs = getComputedStyle(first);
  const usable = first.clientHeight
    - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
  report.push({ what: 'usable column (pt)', v: pt(usable) });

  const rh = first.querySelector('.rh'), rf = first.querySelector('.rf');
  if (rh) report.push({ what: 'running head incl margin (pt)', v: pt(rh.getBoundingClientRect().height + parseFloat(getComputedStyle(rh).marginBottom)) });
  if (rf) report.push({ what: 'footer incl padding (pt)', v: pt(rf.getBoundingClientRect().height + parseFloat(getComputedStyle(rf).paddingTop)) });

  for (const label of wanted) {
    const sheet = [...document.querySelectorAll('.sheet')]
      .find(s => (s.dataset.screenLabel || '') === label);
    if (!sheet) { report.push({ what: 'MISSING ' + label, v: 0 }); continue; }
    report.push({ what: '--- ' + label, v: pt(sheet.scrollHeight - sheet.clientHeight) + 'pt over' });
    for (const kid of sheet.children) {
      const k = getComputedStyle(kid);
      const h = kid.getBoundingClientRect().height
        + parseFloat(k.marginTop) + parseFloat(k.marginBottom);
      report.push({ what: '  ' + kid.className.slice(0, 28) + ' ' + (kid.tagName),
                    v: pt(h), chars: (kid.textContent || '').trim().length });
      if (/^(div|section)$/i.test(kid.tagName) && kid.children.length && kid.className.match(/^(?!rh|rf)/)) {
        for (const g of kid.children) {
          const gs = getComputedStyle(g);
          const gh = g.getBoundingClientRect().height
            + parseFloat(gs.marginTop) + parseFloat(gs.marginBottom);
          report.push({ what: '      ' + g.className.slice(0, 26) + ' ' + g.tagName,
                        v: pt(gh), chars: (g.textContent || '').trim().length });
        }
      }
    }
  }
  return report;
}, wanted);

for (const r of out) {
  console.log(String(r.v).padStart(8), ' ', r.what, r.chars !== undefined ? `(${r.chars} chars)` : '');
}
await browser.close();
