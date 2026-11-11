"""Needle-in-a-haystack generator (seed 42). Facts are made-up access codes, so the model cannot know them.
The haystack is public-domain text (data/SOURCES.md); a fact sentence is inserted between paragraphs at a depth."""
import random

NAMES = ["Amber", "Basalt", "Cedar", "Delta", "Ember", "Fjord", "Granite", "Harbor", "Indigo", "Juniper",
         "Kestrel", "Lantern", "Meadow", "Nimbus", "Orchid", "Pioneer"]


def facts(n, seed=42):
    rng = random.Random(seed)
    names = rng.sample(NAMES, n)
    out = []
    used = set()
    for name in names:
        while True:
            code = "%s-%d" % (rng.choice("KMRTVXZ"), rng.randint(10, 99))
            if code not in used:
                used.add(code)
                break
        out.append({"key": name, "answer": code,
                    "sentence": f"The access code for the {name} room is {code}.",
                    "question": f"What is the access code for the {name} room?"})
    return out


def build(paragraphs, target_words, facts, depths):
    """Take paragraphs until ~target_words, then insert each fact at its depth (0..1) at a paragraph boundary."""
    body, n = [], 0
    i = 0
    while n < target_words:
        p = paragraphs[i % len(paragraphs)]
        body.append(p)
        n += len(p.split())
        i += 1
    total = sum(len(p) for p in body)
    placed = []
    for f, d in sorted(zip(facts, depths), key=lambda x: -x[1]):
        # find the paragraph boundary nearest to depth d (by characters)
        target, acc, idx = d * total, 0, 0
        for k, p in enumerate(body):
            if acc >= target:
                idx = k
                break
            acc += len(p)
        else:
            idx = len(body)
        body.insert(idx, f["sentence"])
        placed.append(dict(f, depth=d))
    return {"text": "\n\n".join(body), "facts": placed, "words": n}


def score(reply, facts):
    r = (reply or "").upper()
    return sum(1 for f in facts if f["answer"].upper() in r)
