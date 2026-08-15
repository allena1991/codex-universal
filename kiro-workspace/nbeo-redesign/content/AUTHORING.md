# Authoring contract for case batches

Read this, read `content/pattern.json`, write your batch, then run the checker
until it prints `clean`.

    python3 tools/check_batch.py content/cases/s1-b.json

## The file

One JSON file per batch, top level is a list of case objects, UTF-8, indent 1.
Write `&deg;` `&nbsp;` `&Delta;` `&micro;` as HTML entities. Never write a raw
`<` or `>`. Never use an em dash. Use plain hyphens.

```json
{
  "id": "S1-07", "session": 1, "n": 7,
  "domain": "Retina, choroid, vitreous",
  "title": "The curtain that came down at the weekend",
  "stem": "...",
  "items": [ ... 5 items ... ],
  "rules": "If ... then ... . If ... then ... .",
  "pair": { ... optional ... }
}
```

`id` is `S<session>-<nn>`, zero padded. `n` is the case number in the session.
`domain` is one of the seventeen blueprint domains, written as English prose,
for example `Cornea and refractive surgery`, `Optic nerve and neuro-ophthalmic`,
`Lids, lacrimal, adnexa, orbit`, `Glaucoma`, `Contact lenses`,
`Accommodation, vergence, oculomotor`, `Lens, cataract, IOL, perioperative`,
`Emergencies and trauma`, `Systemic health`, `Ametropia`,
`Amblyopia and strabismus`, `Ophthalmic optics and spectacles`, `Low vision`,
`Perceptual function and colour vision`, `Episclera, sclera, anterior uvea`,
`Retina, choroid, vitreous`, `Visual and human development`.

`title` is a clinical phrase a candidate would recognise from the chair, not a
diagnosis. The diagnosis must not appear in the title: it gives away item one.

## The item

```json
{
  "type": "diagnosis",
  "q": "What is the most likely diagnosis?",
  "options": [
    {"t": "Preseptal cellulitis with reactive chemosis"},
    {"t": "Orbital cellulitis of ethmoid sinus origin", "correct": true},
    ...five in total...
  ],
  "short": "Orbital cellulitis, ethmoid origin",
  "why": "Why the correct answer is correct, in two sentences.",
  "dis": [
    {"refs": [0], "label": "Preseptal cellulitis",
     "tempting": "Why a competent candidate is drawn to it.",
     "ruled": "The specific finding in this stem that kills it."}
  ]
}
```

- `type` is one of `diagnosis`, `treatment`, `basic`, `legal`. These are the
  four types the blueprint scores separately.
- `"format": "multi"` marks a select-all-that-apply item. It is a response
  format, not a type, so an all-or-none item still has one of the four types.
  Exactly one item per case carries it.
- `options`: exactly 5, with exactly one `"correct": true`. An item with
  `"format": "multi"` takes 5 or 6 options with 2 or 3 correct.
- **Do not choose answer letters.** There are none in this format. Letters are
  generated across the whole session so that A to E each carry 18-22% of the
  single-answer items with no run longer than three. Write the options in the
  order that reads best and flag the correct one in place.
- `short` is the answer in a few words. It prints beside the key letter on the
  teaching key, so it has to stand alone.
- `dis` is required on every item and needs exactly 2 rows. At most one item
  per case may carry a third row, and only if the checker still fits the case
  on two pages. `refs` are zero-based indices into your own `options` array.
  They must point at wrong options. The builder converts them to whatever
  letters the option ends up on. A row may cover two related distractors at
  once, for example `"refs": [0, 3]`.

## Length caps, and why they are hard limits

Each case gets exactly two printed pages: the case, then its teaching key. The
page is a fixed box with overflow hidden, so content that does not fit is lost
in print rather than reflowed. The checker refuses anything that would spill.

| Field | Cap in characters |
| --- | --- |
| `stem` | 440 |
| `q` | 145, and under 95 keeps it to one line |
| each option `t` | 112 |
| `short` | 70 |
| `why` | 205 |
| `tempting` | 88 |
| `ruled` | 88 |
| `label` | 30 |
| `rules` | 200 |

## Rules that make the items teach

1. **Four credible options and at most one clear discard.** An item with one
   plausible answer is a free point, and free points hide the gap the candidate
   needs to find. No throwaways: no "patch the eye and start an antihistamine"
   for proptosis with an RAPD, no "hair colour" as a monitoring parameter.
2. **Match option lengths inside each item.** The longest option must not be
   more than about twice the shortest. If the correct answer needs a qualifier,
   give two distractors qualifiers too. Across a session the correct option may
   be strictly the longest in at most a third of items; the checker fails the
   whole build over this, so keep it near chance.
3. **Distractors are near misses, not nonsense.** The best distractor is the
   competing diagnosis, the right drug at the wrong interval, the right action
   in the wrong order, or the complete plan that ignores the one host factor
   planted in the stem.
4. **Plant the discriminator in the stem.** Every number in a stem should be
   usable: a pulse of 52 before a beta-blocker item, a weight before a
   hydroxychloroquine dose, an interval before a follow-up item. If a number is
   decoration, cut it.
5. **The stem carries findings, not conclusions.** Write "chalky pallid disc
   oedema", not "arteritic-looking disc".
6. **Item mix.** Five items per case. Across your ten cases aim for roughly
   20 to 23 treatment, 14 to 17 diagnosis, 6 to 8 basic science, and 1 or 2 law
   items, which matches the blueprint bands. Exactly one item per case carries
   `"format": "multi"`, spread across the types rather than always landing on
   the same one. Treatment is the largest share because it is the largest share
   of the blueprint and it decides TMOD separately.
7. **`why` explains the reasoning, not the label.** Name the findings that
   force the answer.
8. **`rules` is one or two if-then sentences** a candidate can recite. Not a
   summary of the case.

## The optional competing pair

Add `pair` to roughly one case in three, only where two conditions genuinely
trade places under time pressure. Three or four rows, then the decider.

```json
"pair": {
  "this": "Orbital cellulitis", "vs": "Cavernous sinus thrombosis",
  "rows": [["Laterality", "Unilateral, stays unilateral",
            "Crosses to the other eye within hours"]],
  "decider": "The single finding that separates them, and what it changes."
}
```

Row cells are capped near 100 characters each, the decider near 200.

## Clinical standard

Exam-oriented but correct. Doses are anchors a candidate should recognise, not
prescriptions. Prefer the decision rule over the number where they compete. If
guidance genuinely varies, write the item around the part that does not.

## Voice

Plain, direct, specific. No em dashes. No filler. No second person in stems.
British or American spelling, consistently within your batch. Do not write
"clearly", "simply", or "of course". Do not moralise in a `legal` item: state
the duty and the action.
