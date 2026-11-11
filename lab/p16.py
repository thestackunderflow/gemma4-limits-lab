"""Part 16 (P-NEEDLE): single fact by depth and 8-fact recall, 4K-128K.
python -m lab.p16 run --models e4b --lengths 4096,8192,16384,32768,65536,131072 [--extras 1]
Every row asserts the prompt arrived whole: no "truncating input prompt" WARN for the request, and the prompt plus
1,024 tokens of answer room fit in num_ctx. The model stays loaded per (model, length): prefix caching can shorten
prefill on later cells of the same length, so prompt_eval_count is recorded, not used as the check."""
import os
import sys
import time

from lab import common as c, haystack, logparse, needle, ollama as o
from lab.p_fit import TOK_PER_WORD

OUT = os.path.join(c.ROOT, "out", "p16")
ANSWER_ROOM = 1024


def build(length, facts, depths, start):
    words = int((length - ANSWER_ROOM - 200) / TOK_PER_WORD)
    paras = haystack.paragraphs()
    paras = paras[start:] + paras[:start]
    return needle.build(paras, words, facts, depths)


def ask(tag, length, text, questions, qfirst=False, think=False, temp=0.0, seed=42):
    q = "\n".join(questions) + "\nAnswer with the codes only."
    p = (q + "\n\n" + text + "\n\n" + q) if qfirst else (text + "\n\n" + q)
    m = o.log_mark()
    st, js, dt = o.generate(tag, p, {"temperature": temp, "seed": seed, "num_ctx": length,
                                     "num_predict": 4096 if think else 128}, keep_alive="20m", think=think)
    log = o.log_since(m, settle=0.3)
    return st, js, dt, log


def run(models, lengths, extras=True):
    w = c.writer("p16", "needle")
    for key in models:
        tag = c.TAGS[key]
        for L in lengths:
            first = c.fresh()
            depths = [0.1, 0.5, 0.9] + ([0.0, 0.25, 0.75, 1.0] if L <= 32768 else [])
            cells = [("single", d, n) for d in depths for n in range(3)] + [("eight", None, n) for n in range(3)]
            if extras and L == 32768:
                cells += [("single-qfirst", 0.5, n) for n in range(3)] + [("single-think", 0.5, n) for n in range(3)]
            for kind, d, n in cells:
                seed = 42 + n + int(L / 1024)
                if kind.startswith("single"):
                    facts = needle.facts(1, seed=seed)
                    h = build(L, facts, [d], start=n * 211)
                    qs = [facts[0]["question"]]
                else:
                    facts = needle.facts(8, seed=seed)
                    h = build(L, facts, [i / 8 + 1 / 16 for i in range(8)], start=n * 211)
                    qs = [f["question"] for f in facts]
                st, js, dt, log = ask(tag, L, h["text"], qs, qfirst=kind == "single-qfirst",
                                      think=kind == "single-think")
                if st != 200:
                    r = w.write(c.provenance(tag, log, num_ctx=L, fresh_load=first, model=key, kind=kind,
                                             depth=d, rep=n + 1, status=st, error=js.get("error")))
                    c.say("NEEDLE", key, L, kind, d, n, "status", st, js.get("error"))
                    break
                trunc = logparse.truncations(log)
                reply = js.get("response") or ""
                sc = needle.score(reply, facts)
                r = w.write(c.provenance(tag, log, num_ctx=L, fresh_load=first, model=key, kind=kind, depth=d,
                                         rep=n + 1, status=st, words=h["words"], facts=[f["answer"] for f in facts],
                                         reply=reply[-400:], score=sc, of=len(facts), truncation_warn=trunc,
                                         arrived_whole=not trunc, think=kind == "single-think",
                                         seconds=round(dt, 1), **c.speed(js)))
                c.say("NEEDLE", key, L, kind, d, n, f"{sc}/{len(facts)}", "whole" if not trunc else "TRUNCATED",
                      r["prompt_eval_count"], r["seconds"])
                first = False
        c.fresh()


if __name__ == "__main__":
    a = c.args(sys.argv[2:])
    run(a.get("models", "e4b").split(","), [int(x) for x in a.get("lengths", "4096,8192,16384,32768,65536,131072")
                                            .split(",")], a.get("extras", "1") == "1")
