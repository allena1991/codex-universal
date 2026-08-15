# Audit: NBEO Part II PAM/TMOD 2026 Master Study Guide (120 pp.)

Three classes of defect, in the order that matters. The first one wrecks the product; the second one limits how much a student learns per hour; the third is the part that looks like a redesign job.

## 1. The answer key is broken

Run `python3 tools/key_audit.py` for the full output. Both keys were transcribed from Parts 8 and 10, one row per case.

| | Session 1 | Session 2 | Both |
| --- | --- | --- | --- |
| single-answer items | 161 | 172 | 333 |
| correct answer is A | 67.1% | **95.3%** | **81.7%** |
| longest unbroken run of one letter | 30 | **140** | - |
| letters never correct | E | D, E | E |

A candidate who answers A to every single-answer item scores 272/333, about 82%, without reading a single stem. In Session 2 that strategy scores 95%. The two sessions also differ so much in bias (67% vs 95%) that scores are not comparable between them, which breaks the guide's own workflow of "repair after Session 1, then confirm on Session 2."

Second-order tell: in the overwhelming majority of items, the correct option is also the longest, most hedged option, and the wrong options are short and absolute. A student trained on this file learns "pick the long careful one," which is a real test-taking heuristic but not clinical reasoning, and the actual exam is written to defeat it.

**Fix.** Rebuild every key to 18-22% per letter per session, no run longer than three, all five letters live in both sessions. Then re-audit with the same script. Equalise option length within each item: if the correct answer needs a qualifier, give the distractors qualifiers too.

## 2. The distractors do not teach, and neither do the rationales

Roughly half the items are given away by implausible options: "Patch the eye and begin oral antihistamine" for a child with proptosis and an RAPD, "Use topical anesthetic at home", "Share antiviral medication with household members", "Hair color" as a parameter to monitor in uveitis. An item with one credible option is a free point, and free points hide exactly the gaps a candidate needs to find.

The rationales explain only the correct answer. Nothing explains why the tempting wrong answer is tempting. That is where the learning is: the difference between orbital cellulitis and cavernous sinus thrombosis, between a small subperiosteal collection that can be treated medically and one that needs drainage, between DLK and post-LASIK infectious keratitis.

**Fix.** Every item gets four credible options plus at most one clear discard. Every rationale gets a per-distractor block: why a competent candidate is drawn to it, and the specific finding that rules it out. The rebuilt Case 1 in `index.html` is the pattern.

Related: items are not tagged by blueprint item type, so a candidate cannot see whether they are failing diagnosis, treatment, basic science, or legal items. The blueprint scores those separately. Tag every item and score by tag.

## 3. Claims that outrun the evidence

- The cover asserts "Blueprint-verified", "Double-checked against the live official blueprint", and "The May 2026 NBEO matrix and outline were downloaded again for this edition." That is a self-certification: nothing in the document lets a reader check it, and no version or checksum of the source documents is recorded.
- The format facts do hold up. I fetched NBEO's Part II PAM/TMOD exam page: 350 items, cases with 3-6 items each, approximately 120 TMOD items, two sessions of 175 items, 3.5 hours per session, separate PAM and TMOD pass/fail decisions. Source: https://optometry.org/exams/part-ii-pam-tmod/
- All five cited NBEO PDF URLs return HTTP 200, so the citations are real links, not invented ones. I could not parse the PDFs in this environment, so the domain ranges and item-type percentages in the guide remain **transcribed but unconfirmed**. They should be labelled that way until someone diffs them against the current Content Matrix.
- The Pearson tutorial URL (`home.pearsonvue.com/nbeo/tutorial/pam-tmod`) failed to resolve. NBEO's own page says the tutorial is being updated. Replace the deep link with the exam page.
- "245-245 items" and "163-163 items" appear on the cover as if they were ranges. They are single values rendered into a range slot.

**Fix.** Replace every self-certification with a dated verification table: what was checked, against which document, on what date, and what remains unconfirmed. A guide that says "this figure is transcribed, confirm it" is more trustworthy than one that says "verified" with nothing behind it.

## 4. Structure and typography

- **Five-column condition tables** (pp. 11-16) are the core reference content and the hardest thing in the book to read: five text columns at roughly 7pt, no visual weighting, the trap column - the most valuable column - is last and lightest.
- **Empty and near-empty pages**: p. 9 carries one paragraph and a callout, p. 10 carries three sentences, p. 29 is a title with nothing under it. Three of 120 pages are structural filler.
- **Bulleted list rendering** is broken throughout the checklist pages: markers sit on their own line, offset from the text.
- **No emergency keying.** The emergency gate is the highest-stakes content and looks identical to the study-schedule tables. Red-boxing everything on one page is not a system.
- **Undifferentiated hierarchy.** Section headers, table headers, and body copy all sit close together in size and weight, so 120 pages read as one long texture. Nothing is scannable under time pressure, which is the one condition this content will actually be used in.
- Two-column condition cards with a keyed trap strip fit the same information in less space and survive being read at arm's length.

## What is in the rebuild

The full guide, 179 letter pages, built from data rather than typed: `python3 tools/build.py` then `node tools/to_pdf.mjs`.

| | Previous edition | This edition |
| --- | --- | --- |
| Correct answer is A | 81.7% of single-answer items | 19.6% |
| Longest run of one letter | 140 | 3 |
| Letters never correct | E in both sessions, D in Session 2 | none |
| Best single-letter guess | 272/333, 82% | 30/140, 21% |
| Correct option strictly the longest | most items | 13%, against 20% by chance |
| Per-distractor teaching | none | 711 rows, two or three per item |
| Item-type tags | none | every item, with score-by-tag sheets |
| Item-type allocation | untagged | Tx 44.3%, Dx 34.0%, Sci 16.6%, Law 5.1%, all inside the published bands |
| Self-certification | "Blueprint-verified" | dated verification table, three states |
| Empty or filler pages | 3 of 120 | none |

Every page is a fixed letter box with `overflow:hidden`, and `node tools/shoot.mjs` measures all 179 in a real render and fails if any is clipped. The answer letters are generated to the distribution target after authoring, so the audit on page 4 of the manual is printed from the same build that produced the pages.

### Layout of the rebuild

Part 1 front matter and key integrity, Part 2 the exam to scale with item types and pacing, Part 3 an eighteen-pattern emergency gate, Part 4 twenty-four condition cards, Part 5 pharmacology in three sheets, Part 6 optics and the law items, Part 7 competing pairs generated from the case data, Parts 8 and 9 the two sessions with a case index and a score-by-tag sheet each, and Part 10 the printed key, an eighteen-day schedule keyed to case numbers, the recall deck, sources and a colophon.

### What is still unconfirmed

Per-domain item ranges and item-type percentage bands remain transcribed from the prior edition. The official Content Matrix PDF resolves but was not machine-read, and both figures are marked unconfirmed wherever they appear in the manual.
