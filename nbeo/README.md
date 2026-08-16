# NBEO study guides

Three print-ready study guides, one per part of the NBEO examination sequence, generated
from HTML fragments and rendered with WeasyPrint.

| Guide | File | Pages |
| --- | --- | --- |
| Part I, Applied Basic Science | `dist/NBEO_Part_I_ABS_Study_Guide.pdf` | 188 |
| Part II, Patient Assessment and Management / TMOD | `dist/NBEO_Part_II_PAM_TMOD_Study_Guide.pdf` | 171 |
| Part III, Patient Encounters and Performance Skills | `dist/NBEO_Part_III_PEPS_Study_Guide.pdf` | 85 |

## Building

```
pip install weasyprint pypdf pypdfium2
# body Noto Serif, headings Noto Sans, values Noto Sans Mono
dnf install -y google-noto-serif-fonts google-noto-sans-fonts google-noto-sans-mono-fonts

python3 build.py            # all three
python3 build.py part3      # one guide
```

`build.py` reads the sorted `*.html` fragments in `content/<guide>/`, injects stable ids on
every chapter and section heading, builds the table of contents with real page numbers via
`target-counter()`, tags over-tall callouts so they can break across pages, wraps the result
in a paged-media shell with `assets/print.css`, and writes the PDF plus a `.debug.html`
snapshot to `dist/`.

## Authoring conventions

Chapter heading. The `.t` span feeds the running header, so keep it under about 55
characters:

```html
<h1 class="chapter"><span class="num">Chapter 4 &#183; Gross anatomy</span><span class="t">Retina, RPE, and retinal circulation</span></h1>
```

Front matter uses `<section class="fm"><h1>Title</h1>`; add `class="notoc"` to keep a
heading out of the table of contents.

Component classes in `print.css`: `.opener` with `.obj` and `.wt` for the chapter opener and
blueprint weight, `.box` with the `.hy` `.trap` `.pearl` `.mnem` `.script` variants,
`.numbers`, `.algo`, `.checklist` with `li.crit`, `.drill` with `.answers`, `.recap`,
`.tags`/`.tag`, `.cols2`/`.cols3`, `pre.dia`, and the table modifiers `.compact` `.sub`
`.rx` `.trapt`. Add `.newpage` to force a page break.

Two rules the renderer will not catch for you: never use an em dash character, and keep
`pre.dia` lines at 108 characters or fewer, because that is what fits the text column at the
declared mono size.

## Verification

The build is checked against the rendered PDFs, not just the exit code:

- no glyph crosses the text column on any page,
- no page is left near-empty by an unbreakable block,
- every table of contents entry resolves to the page its leader dots promise,
- no em dash survives anywhere in the extracted text.

## Sources

Content is authored against the public NBEO documents for the August 2026 to May 2027
administration: the Part I content matrix, the Part II PAM content outline, and the Part III
PEPS candidate guide, blueprint and content outline, and the anterior and posterior segment
skills evaluation forms. Those PDFs are not redistributed here. Download the current
versions from the NBEO website and re-verify before an exam date, because item numbering on
the skills forms changes between administrations.

These guides are a study aid, not an official NBEO publication.
