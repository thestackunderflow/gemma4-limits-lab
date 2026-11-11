"""P-FIT: what num_ctx loads on the 8 GB card, per size and KV type (the KV type is server-wide: the host script
restarts the server with OLLAMA_KV_CACHE_TYPE, the row reads the type back from the log).
python -m lab.p_fit --kv f16 --models e2b,e4b,12b-qat,26b [--reps 3] [--maxfill 1]"""
import sys
import time

from lab import common as c, haystack, logparse, ollama as o

SIZES = {"e2b": [4096, 16384, 32768, 65536, 131072], "e4b": [4096, 16384, 32768, 65536, 131072],
         "12b-qat": [65536, 131072, 262144], "26b": [65536, 131072, 262144]}
TOK_PER_WORD = 1.29          # measured on this haystack: 7,500 words + question = 9,644 tokens (P-TRUNC probe)
MAX_FILL_MINUTES = 50        # one max fill per model per KV type, skipped when the estimate is longer


def fill_prompt(tokens, start=0):
    return haystack.words(int(tokens / TOK_PER_WORD), start=start) + "\n\nSummarise the text above in one sentence."


def cell(key, num_ctx, fill, kv_set, rep, w, kind="speed"):
    tag = c.TAGS[key]
    f = c.fresh()
    m, t0 = o.log_mark(), time.time()
    try:
        st, js, dt = o.generate(tag, fill_prompt(fill, start=rep * 37),
                                {"temperature": 0, "seed": 42, "num_predict": 128, "num_ctx": num_ctx},
                                keep_alive="2m", think=False)
    except Exception as e:  # timeout / connection reset (server killed)
        st, js, dt = 0, {"error": repr(e)[:300]}, time.time() - t0
    ps = o.ps() if st == 200 else []
    t1 = time.time()
    log = o.log_since(m)
    row = c.provenance(tag, log, num_ctx=num_ctx, fresh_load=f, model=key, kv_set=kv_set, rep=rep, kind=kind,
                       fill_target=fill, status=st, loads=(st == 200), error=js.get("error"),
                       processor=(ps[0]["processor"] if ps else None),
                       ps_context_length=(ps[0]["context_length"] if ps else None),
                       offload=logparse.offload(log), ctx_arg=logparse.ctx_arg(log),
                       mmap_disabled=logparse.mmap_disabled(log), gpu_available_gib=logparse.gpu_available_gib(log),
                       log_errors=logparse.errors(log), window=c.window(t0, t1), seconds=round(dt, 1),
                       **c.speed(js))
    w.write(row)
    c.say("FIT", key, kv_set, num_ctx, kind, rep, st, row["processor"], row["offload"], row["prefill_tok_s"],
          row["write_tok_s"], row["window"].get("gpu_mib_max"), row["window"].get("ram_mib_max"))
    c.fresh()
    return row


def run(kv, models, reps=3, maxfill=True):
    w = c.writer("p13", "fit")
    for key in models:
        loaded, rate = [], None
        for nc in SIZES[key]:
            for rep in range(1, reps + 1):
                r = cell(key, nc, min(nc // 2, 16384), kv, rep, w)
                if r["loads"]:
                    loaded.append(nc)
                    rate = r["prefill_tok_s"] or rate
                elif rep == 1:
                    break  # a size that does not load is not repeated
        if maxfill and loaded:
            nc = max(loaded)
            fill = nc - 1024
            est = fill / rate / 60 * 1.5 if rate else 999
            if est <= MAX_FILL_MINUTES:
                cell(key, nc, fill, kv, 1, w, kind="max-fill")
            else:
                c.say("FIT max-fill skipped", key, nc, "estimate min", round(est, 1))
                w.write(c.provenance(c.TAGS[key], "", num_ctx=nc, fresh_load=False, model=key, kv_set=kv,
                                     kind="max-fill-skipped", estimate_minutes=round(est, 1),
                                     kv_type_note="not loaded"))


if __name__ == "__main__":
    a = c.args(sys.argv[1:])
    run(a["kv"], a.get("models", "e2b,e4b,12b-qat,26b").split(","), int(a.get("reps", 3)), a.get("maxfill", "1") == "1")
