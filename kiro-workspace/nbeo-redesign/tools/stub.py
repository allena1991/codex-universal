#!/usr/bin/env python3
"""Fill content/cases with worst-case stub cases, to calibrate the layout.

Every text field is padded to its cap, so a build that fits with stubs will fit
with real content. Run before authoring, then let real batches overwrite the
files. Delete any stub file that is still present at the end: the case titles
all start with "Stub", which tools/build.py has no reason to accept in print.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from render import CAPS                                          # noqa: E402

TOPICS = {
    1: ["orbital cellulitis", "microbial keratitis", "HSV epithelial keratitis",
        "Acanthamoeba keratitis", "keratoconus", "herpes zoster ophthalmicus",
        "posterior capsule opacification", "anterior uveitis", "scleritis",
        "neovascular AMD", "PDR with DME", "CRVO", "PVD with retinal tear",
        "CRAO", "central serous chorioretinopathy", "hydroxychloroquine screening",
        "POAG", "acute angle closure", "neovascular glaucoma", "optic neuritis",
        "arteritic AION", "papilloedema", "third-nerve palsy", "Horner syndrome",
        "ocular myasthenia", "convergence insufficiency", "accommodative esotropia",
        "fourth-nerve palsy", "myopia control", "induced prism",
        "vertex conversion", "sterile infiltrate", "low vision assessment",
        "acquired dyschromatopsia", "telephone triage and screening statistics"],
    2: ["pseudomyopia", "anisometropia", "vertical imbalance", "toric rotation",
        "flat GP fit", "RP-spectrum low vision", "accommodative insufficiency",
        "high AC/A esophoria", "divergence insufficiency", "intermittent exotropia",
        "ethambutol toxicity", "retinoblastoma", "sebaceous carcinoma",
        "congenital nasolacrimal obstruction", "orbital trapdoor fracture",
        "post-LASIK keratitis", "alkali burn", "neurotrophic keratopathy",
        "endophthalmitis", "toxic anterior segment syndrome", "UGH syndrome",
        "bag-IOL dislocation", "ocular toxoplasmosis", "peripheral ulcerative keratitis",
        "tractional detachment", "acute retinal necrosis", "choroidal melanoma",
        "chiasmal compression", "internuclear ophthalmoplegia",
        "homonymous hemianopia", "amaurosis fugax", "angle recession",
        "topiramate angle closure", "plateau iris", "informed refusal and statistics"],
}
DOMAINS = ["Cornea and refractive surgery", "Retina, choroid, vitreous",
           "Optic nerve and neuro-ophthalmic", "Glaucoma", "Contact lenses",
           "Lids, lacrimal, adnexa, orbit", "Episclera, sclera, anterior uvea",
           "Emergencies and trauma", "Accommodation and vergence",
           "Lens, cataract, IOL, perioperative"]


def pad(text, cap):
    """Grow text to the cap so the stub is the worst case, not the best."""
    filler = (" The stem carries the host factor, the interval and the number "
              "that decides between two otherwise identical options, at length.")
    while len(text) < cap - 12:
        text += filler
    return text[:cap - 2].rsplit(" ", 1)[0] + "."


def make_case(session, n):
    topic = TOPICS[session][n - 1]
    items = []
    for k in range(5):
        kind = ["diagnosis", "treatment", "basic", "diagnosis", "treatment"][k]
        multi = k == 3
        options = [{"t": pad("Stub option %d for %s" % (j + 1, topic),
                             CAPS["option"])} for j in range(6 if multi else 5)]
        if multi:
            for j in (1, 2, 4):
                options[j]["correct"] = True
        else:
            options[(n + k) % 5]["correct"] = True
        items.append({
            "type": kind,
            "format": "multi" if multi else None,
            "q": pad("Stub question %d about %s" % (k + 1, topic), 100),
            "options": options,
            "why": pad("Stub explanation for %s" % topic, CAPS["why"]),
            "short": pad("Stub short answer", CAPS["short"]),
            "dis": [{"refs": [(n + k + 1 + d) % 5 if not multi else 0],
                     "label": pad("Stub label", CAPS["label"]),
                     "tempting": pad("Stub tempting", CAPS["tempting"]),
                     "ruled": pad("Stub ruled out", CAPS["ruled"])}
                    for d in range(3)],
        })
        if not multi:
            correct = (n + k) % 5
            items[-1]["dis"] = [d for d in items[-1]["dis"]
                                if d["refs"][0] != correct][:2]
    for item in items:
        if item["format"] is None:
            del item["format"]
    return {
        "id": "S%d-%02d" % (session, n),
        "session": session,
        "n": n,
        "domain": DOMAINS[(n - 1) % len(DOMAINS)],
        "title": "Stub presentation for %s" % topic,
        "stem": pad("Stub stem for %s" % topic, CAPS["stem"]),
        "items": items,
        "rules": pad("Stub if-then rule", CAPS["rules"]),
        "pair": {"this": topic.title(), "vs": "The mimic",
                 "rows": [["Tempo", "Hours", "Weeks"], ["Pain", "Severe", "None"],
                          ["Pupil", "RAPD", "Normal"]],
                 "decider": pad("Stub decider", 200)} if n % 3 == 1 else None,
    }


def main():
    out = os.path.join(ROOT, "content", "cases")
    os.makedirs(out, exist_ok=True)
    batches = {1: [(1, 10), (11, 20), (21, 30), (31, 35)],
               2: [(1, 10), (11, 20), (21, 30), (31, 35)]}
    for session, spans in batches.items():
        for letter, (lo, hi) in zip("abcd", spans):
            cases = [make_case(session, n) for n in range(lo, hi + 1)]
            for c in cases:
                if c["pair"] is None:
                    del c["pair"]
            path = os.path.join(out, "s%d-%s.json" % (session, letter))
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(cases, fh, indent=1)
            print("wrote", os.path.basename(path), len(cases), "cases")


if __name__ == "__main__":
    main()
