"""Part 13 runners. P-DEF: the default context on this card. P-TRUNC: what happens to a 10K-token prompt at it.
python -m lab.p13 def | trunc [--reps 3]"""
import sys
import time

from lab import common as c, haystack, logparse, ollama as o

FACT = "The access code for the vault is K-77."
QUESTION = "What is the access code for the vault? Answer with the code only."
OPTS = {"temperature": 0, "seed": 42, "num_predict": 64}


def p_def():
    w = c.writer("p13", "def")
    for key in ["e2b", "e4b", "12b-qat", "26b"]:
        tag = c.TAGS[key]
        f = c.fresh()
        m, t0 = o.log_mark(), time.time()
        st, js, dt = o.generate(tag, "Say OK.", {"temperature": 0, "seed": 42, "num_predict": 4}, keep_alive="2m",
                                think=False)
        ps = o.ps()
        t1 = time.time()
        log = o.log_since(m)
        whole = open(o.LOG, encoding="utf-8", errors="replace").read()
        row = c.provenance(tag, log, num_ctx="default (no option)", fresh_load=f, model=key, status=st,
                           ps=ps, ps_context_length=(ps[0]["context_length"] if ps else None),
                           processor=(ps[0]["processor"] if ps else None),
                           server_default=logparse.default_context(whole), ctx_arg=logparse.ctx_arg(log),
                           offload=logparse.offload(log), mmap_disabled=logparse.mmap_disabled(log),
                           gpu_available_gib=logparse.gpu_available_gib(log), window=c.window(t0, t1),
                           seconds=round(dt, 1), **c.speed(js))
        w.write(row)
        c.say("DEF", key, row["ps_context_length"], row["processor"], row["offload"])
        c.fresh()


def prompt(position, words=7500):
    body = haystack.words(words)
    if position == "start":
        return FACT + "\n\n" + body + "\n\n" + QUESTION
    return body + "\n\n" + FACT + "\n\n" + QUESTION


def one(tag, endpoint, position, extra=None, num_ctx=None, temperature=0, seed=42):
    p = prompt(position)
    opts = dict(OPTS, temperature=temperature, seed=seed)
    if num_ctx:
        opts["num_ctx"] = num_ctx
    extra = extra or {}
    f = c.fresh()
    m, t0 = o.log_mark(), time.time()
    if endpoint == "chat":
        st, js, dt = o.chat(tag, [{"role": "user", "content": p}], opts, think=False, **extra)
        answer = (js.get("message") or {}).get("content")
        pe = js.get("prompt_eval_count")
    elif endpoint == "generate":
        st, js, dt = o.generate(tag, p, opts, think=False, **extra)
        answer, pe = js.get("response"), js.get("prompt_eval_count")
    else:
        st, js, dt = o.openai_chat(tag, [{"role": "user", "content": p}], temperature=temperature, seed=seed,
                                   max_tokens=64, reasoning_effort="none", **extra)
        ch = (js.get("choices") or [{}])[0]
        answer = (ch.get("message") or {}).get("content")
        pe = (js.get("usage") or {}).get("prompt_tokens")
    log = o.log_since(m)
    return c.provenance(tag, log, num_ctx=num_ctx or "default (no option)", temperature=temperature,
                        fresh_load=f, endpoint=endpoint, position=position, extra=extra, status=st,
                        prompt_eval_count=pe, answer=answer, correct=bool(answer and "K-77" in answer),
                        truncation_warn=logparse.truncations(log), ctx_arg=logparse.ctx_arg(log),
                        reply_keys=sorted(js.keys()), error=js.get("error") or js.get("_text"),
                        seconds=round(dt, 1))


def p_trunc(reps=3):
    w = c.writer("p13", "trunc")
    cases = [("chat", "start", None, None), ("chat", "end", None, None),
             ("generate", "start", None, None), ("generate", "end", None, None),
             ("openai", "start", None, None), ("openai", "end", None, None),
             ("chat", "start", {"truncate": False}, None), ("generate", "start", {"truncate": False}, None),
             ("chat", "start", {"shift": False}, None), ("generate", "start", {"shift": False}, None),
             ("chat", "start", None, 16384), ("chat", "end", None, 16384)]
    for rep in range(1, reps + 1):
        for key in (["e4b", "12b-qat"] if rep == 1 else ["e4b"]):
            for ep, pos, extra, nc in cases:
                if key == "12b-qat" and (extra or ep == "generate"):
                    continue
                r = w.write(dict(one(c.TAGS[key], ep, pos, extra, nc), rep=rep, model=key))
                c.say("TRUNC", key, rep, ep, pos, extra, nc, r["status"], r["prompt_eval_count"], r["correct"],
                      r["truncation_warn"])
    # headline answer at Google's recommended sampling: temperature 1.0, 5 reps, default and the fix
    for nc in (None, 16384):
        for s in range(5):
            r = w.write(dict(one(c.TAGS["e4b"], "chat", "start", None, nc, temperature=1.0, seed=1000 + s),
                             rep=s + 1, model="e4b", sampling="google-recommended temp 1.0"))
            c.say("TRUNC t1", nc, s, r["prompt_eval_count"], r["correct"])


if __name__ == "__main__":
    cmd = sys.argv[1]
    a = c.args(sys.argv[2:])
    if cmd == "def":
        p_def()
    elif cmd == "trunc":
        p_trunc(int(a.get("reps", 3)))
