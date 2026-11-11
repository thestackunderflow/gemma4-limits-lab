"""Shared helpers for the measurement runners: provenance row, fresh-load guard, sampler window."""
import json
import os
import sys
import time

from lab import logparse, ollama as o, rows, samples

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAGS = {"e2b": "gemma4:e2b-it-q4_K_M", "e4b": "gemma4:e4b-it-q4_K_M", "12b-qat": "gemma4:12b-it-qat",
        "12b-q4": "gemma4:12b-it-q4_K_M", "26b": "gemma4:26b"}
_info = {}
_last_kv = {}


def info(tag):
    if tag not in _info:
        s = o.show(tag)
        _info[tag] = {"digest": o.digest(tag), "capabilities": s.get("capabilities", []),
                      "mtp_draft": "draft_num_predict" in (s.get("parameters") or ""),
                      "context_length_max": next((v for k, v in s.get("model_info", {}).items()
                                                  if k.endswith(".context_length")), None)}
    return _info[tag]


VERSION = None


def version():
    global VERSION
    if VERSION is None:
        VERSION = o.version()
    return VERSION


def say(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


MIN_WINDOWS_FREE_GB = 2.0   # owner rule: never start a load with Windows under 2 GB free


def drop_caches():
    try:
        os.system("sync")
        with open("/proc/sys/vm/drop_caches", "w") as f:
            f.write("3")
        return True
    except OSError:
        return False


def windows_free():
    s = samples.read()
    return s[-1]["win_free_gb"] if s and time.time() - s[-1]["t"] < 60 else None


def fresh():
    """Unload everything, drop the VM page cache, wait for Windows free RAM >= 2 GB (up to 10 min).
    True when nothing is loaded (the next request is a fresh load)."""
    ok = o.unload_all()
    drop_caches()
    for _ in range(120):
        w = windows_free()
        if w is None or w >= MIN_WINDOWS_FREE_GB:
            break
        say("waiting: Windows free", w, "GB")
        time.sleep(5)
        drop_caches()
    else:
        raise SystemExit("Windows free RAM stayed under %.1f GB" % MIN_WINDOWS_FREE_GB)
    return ok


def provenance(tag, log, num_ctx=None, temperature=0, fresh_load=True, **extra):
    kv = logparse.kv_type(log)
    if kv:
        _last_kv[tag] = kv
    row = {"tag": tag, "digest": info(tag)["digest"], "num_ctx": num_ctx or logparse.ctx_arg(log) or "default",
           "kv_type": kv or (_last_kv.get(tag, "not-loaded") + ("" if fresh_load else " (from the load before)")),
           "mtp_draft": info(tag)["mtp_draft"], "temperature": temperature, "ollama_version": version(),
           "fresh_load": fresh_load, "t": time.strftime("%Y-%m-%dT%H:%M:%S")}
    row.update(extra)
    return rows.check(row)


def speed(js):
    """Prefill and write tok/s from the Ollama timings (ns)."""
    pe, pd = js.get("prompt_eval_count"), js.get("prompt_eval_duration")
    ec, ed = js.get("eval_count"), js.get("eval_duration")
    return {"prompt_eval_count": pe, "eval_count": ec,
            "prefill_tok_s": round(pe / (pd / 1e9), 1) if pe and pd else None,
            "write_tok_s": round(ec / (ed / 1e9), 1) if ec and ed else None,
            "prefill_s": round(pd / 1e9, 2) if pd else None,
            "load_s": round(js.get("load_duration", 0) / 1e9, 2) if js.get("load_duration") else None,
            "total_s": round(js.get("total_duration", 0) / 1e9, 2) if js.get("total_duration") else None}


def window(t0, t1):
    return samples.window(t0, t1)


def writer(video, name):
    return rows.Writer(os.path.join(ROOT, "out", video, name + ".jsonl"))


def args(argv=None):
    """--key value pairs -> dict."""
    a = argv if argv is not None else sys.argv[1:]
    out = {}
    for i in range(0, len(a) - 1, 2):
        out[a[i].lstrip("-")] = a[i + 1]
    return out


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
