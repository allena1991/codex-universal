#!/usr/bin/env python3
"""Answer-key audit for the 2026 NBEO Part II PAM/TMOD guide (350 items).

Keys transcribed from Part 8 (Session 1 rationales) and Part 10 (Session 2
rationales) of the source PDF, one row per case, five items per case.
Multiple-response items are reported separately: they cannot carry positional
bias the way single-answer items do.
"""

from collections import Counter

# 35 cases x 5 items = 175 items per session.
SESSION_1 = [
    ["C", "BCE", "B", "A", "C"],      # 1  orbital cellulitis
    ["B", "AC", "B", "A", "C"],       # 2  microbial keratitis
    ["A", "B", "B", "ABC", "B"],      # 3  HSV epithelial keratitis
    ["A", "B", "A", "B", "B"],        # 4  Acanthamoeba
    ["B", "B", "B", "B", "AD"],       # 5  keratoconus
    ["A", "B", "B", "AB", "A"],       # 6  herpes zoster ophthalmicus
    ["B", "B", "ABC", "A", "B"],      # 7  posterior capsule opacification
    ["A", "A", "A", "AB", "B"],       # 8  anterior uveitis
    ["A", "A", "B", "A", "B"],        # 9  scleritis
    ["B", "B", "B", "B", "B"],        # 10 neovascular AMD
    ["C", "AB", "B", "A", "B"],       # 11 PDR with DME
    ["A", "B", "A", "A", "A"],        # 12 CRVO
    ["A", "B", "B", "ABC", "A"],      # 13 PVD with tear
    ["A", "B", "AB", "A", "B"],       # 14 CRAO
    ["A", "A", "A", "A", "B"],        # 15 CSCR
    ["A", "C", "AB", "B", "B"],       # 16 hydroxychloroquine
    ["A", "A", "A", "B", "B"],        # 17 POAG
    ["A", "A", "A", "A", "A"],        # 18 acute angle closure
    ["A", "A", "ABC", "A", "A"],      # 19 neovascular glaucoma
    ["A", "A", "C", "A", "A"],        # 20 optic neuritis
    ["A", "B", "A", "A", "A"],        # 21 arteritic AION
    ["A", "B", "A", "A", "A"],        # 22 papilledema
    ["A", "A", "A", "B", "A"],        # 23 third-nerve palsy
    ["A", "A", "A", "A", "A"],        # 24 Horner syndrome
    ["A", "A", "A", "A", "A"],        # 25 ocular myasthenia
    ["A", "A", "A", "A", "A"],        # 26 convergence insufficiency
    ["A", "A", "A", "A", "A"],        # 27 accommodative esotropia
    ["A", "A", "A", "A", "A"],        # 28 fourth-nerve palsy
    ["A", "A", "AB", "A", "A"],       # 29 myopia control
    ["C", "A", "A", "A", "C"],        # 30 induced prism
    ["B", "A", "A", "A", "A"],        # 31 vertex conversion
    ["A", "A", "A", "A", "A"],        # 32 sterile infiltrate
    ["C", "A", "D", "A", "A"],        # 33 low vision
    ["A", "A", "A", "A", "A"],        # 34 acquired dyschromatopsia
    ["A", "A", "ABC", "D", "A"],      # 35 telephone triage / stats
]

SESSION_2 = [
    ["B", "C", "B", "A", "A"],        # 1  pseudomyopia
    ["B", "A", "A", "A", "A"],        # 2  anisometropia
    ["A", "C", "A", "A", "A"],        # 3  vertical imbalance
    ["A", "C", "A", "A", "A"],        # 4  toric rotation / LARS
    ["A", "A", "A", "C", "A"],        # 5  flat GP fit
    ["A", "A", "A", "A", "A"],        # 6  RP-spectrum low vision
    ["A", "C", "A", "A", "A"],        # 7  accommodative insufficiency
    ["A", "A", "A", "A", "A"],        # 8  high AC/A esophoria
    ["A", "A", "A", "A", "A"],        # 9  divergence insufficiency
    ["A", "A", "A", "A", "A"],        # 10 intermittent exotropia
    ["A", "A", "A", "A", "A"],        # 11 ethambutol toxicity
    ["A", "A", "A", "A", "A"],        # 12 retinoblastoma
    ["A", "A", "A", "A", "A"],        # 13 sebaceous carcinoma
    ["A", "A", "A", "A", "A"],        # 14 congenital NLD obstruction
    ["A", "A", "A", "A", "A"],        # 15 trapdoor fracture
    ["A", "A", "A", "A", "A"],        # 16 post-LASIK keratitis
    ["A", "ABC", "A", "A", "A"],      # 17 alkali burn
    ["A", "A", "A", "A", "A"],        # 18 neurotrophic keratopathy
    ["A", "A", "A", "A", "A"],        # 19 endophthalmitis
    ["A", "A", "A", "A", "A"],        # 20 TASS
    ["A", "A", "A", "A", "A"],        # 21 UGH syndrome
    ["A", "A", "A", "A", "A"],        # 22 bag-IOL dislocation
    ["A", "A", "A", "A", "A"],        # 23 toxoplasmosis
    ["A", "A", "A", "ABC", "A"],      # 24 PUK with RA
    ["A", "A", "A", "A", "A"],        # 25 tractional detachment
    ["A", "A", "A", "A", "A"],        # 26 acute retinal necrosis
    ["A", "A", "A", "A", "A"],        # 27 choroidal melanoma
    ["A", "A", "A", "A", "A"],        # 28 chiasmal compression
    ["A", "A", "A", "A", "A"],        # 29 internuclear ophthalmoplegia
    ["A", "A", "A", "A", "A"],        # 30 homonymous hemianopia
    ["A", "A", "A", "A", "A"],        # 31 amaurosis fugax
    ["A", "A", "A", "A", "A"],        # 32 angle recession
    ["A", "A", "A", "A", "A"],        # 33 topiramate angle closure
    ["A", "A", "A", "A", "A"],        # 34 plateau iris
    ["A", "ABC", "A", "A", "A"],      # 35 informed refusal / stats
]


def flatten(cases):
    return [answer for case in cases for answer in case]


def longest_run(letters):
    best = run = 1
    for i in range(1, len(letters)):
        run = run + 1 if letters[i] == letters[i - 1] else 1
        best = max(best, run)
    return best


def report(name, cases):
    key = flatten(cases)
    assert len(key) == 175, "%s has %d items, expected 175" % (name, len(key))
    single = [k for k in key if len(k) == 1]
    multi = [k for k in key if len(k) > 1]
    counts = Counter(single)
    print("\n%s" % name)
    print("  %d items: %d single-answer, %d multiple-response"
          % (len(key), len(single), len(multi)))
    for letter in "ABCDE":
        n = counts.get(letter, 0)
        share = 100.0 * n / len(single)
        print("  %s %4d  %5.1f%%  %s" % (letter, n, share, "#" * int(round(share / 2))))
    print("  longest run of one letter: %d consecutive single-answer items"
          % longest_run(single))
    unused = ", ".join(l for l in "ABCDE" if counts.get(l, 0) == 0)
    print("  never correct: %s" % (unused or "none"))
    return counts, len(single)


def main():
    c1, n1 = report("Session 1", SESSION_1)
    c2, n2 = report("Session 2", SESSION_2)

    total = Counter()
    total.update(c1)
    total.update(c2)
    n = n1 + n2

    print("\nBoth sessions (%d single-answer items)" % n)
    for letter in "ABCDE":
        print("  %s %4d  %5.1f%%" % (letter, total.get(letter, 0),
                                     100.0 * total.get(letter, 0) / n))

    a = total.get("A", 0)
    print("\n  Blind-A score: %d/%d = %.0f%% of single-answer items, "
          "with no stem read." % (a, n, 100.0 * a / n))
    print("  Session 2 alone: %d/%d = %.0f%%."
          % (c2.get("A", 0), n2, 100.0 * c2.get("A", 0) / n2))
    print("  Rebuild target: 18-22%% per letter, no run longer than 3, "
          "every letter used in every session.")


if __name__ == "__main__":
    main()
