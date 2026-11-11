"""Summaries: out/<part>/results.json + the tables of out/<part>/RESULTS.md (python -m lab.report)."""
import json
import os
import statistics as st
from collections import defaultdict

from lab import rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def P(*a):
    return os.path.join(ROOT, "out", *a)


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(st.median(xs), 1) if xs else None


def rng(xs):
    xs = [x for x in xs if x is not None]
    return f"{min(xs)}-{max(xs)}" if xs else None


def jl(path):
    return rows.read(path)


def md_table(head, body):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    out += ["| " + " | ".join("" if v is None else str(v) for v in r) + " |" for r in body]
    return "\n".join(out)


def p13():
    res, md = {}, []
    d = jl(P("p13", "def.jsonl"))
    if d:
        res["default"] = [{k: r.get(k) for k in ("model", "tag", "digest", "ps_context_length", "processor",
                                                 "offload", "server_default", "mtp_draft", "kv_type")} for r in d]
        md.append("### P-DEF: default context, fresh load, no options\n" + md_table(
            ["model", "digest", "/api/ps context_length", "PROCESSOR", "layers on GPU", "server log line"],
            [[r["model"], r["digest"], r["ps_context_length"], r["processor"], r["offload"],
              r["server_default"]] for r in d]))
    t = jl(P("p13", "trunc.jsonl"))
    if t:
        g = defaultdict(list)
        for r in t:
            g[(r["model"], r["endpoint"], r["position"], json.dumps(r["extra"]), str(r["num_ctx"]),
               r.get("sampling", "temp 0"))].append(r)
        body, out = [], []
        for k, rs in g.items():
            warn = [w for r in rs for w in r["truncation_warn"]]
            row = {"model": k[0], "endpoint": k[1], "fact": k[2], "extra": k[3], "num_ctx": k[4], "sampling": k[5],
                   "runs": len(rs), "status": sorted({r["status"] for r in rs}),
                   "prompt_eval_count": sorted({r["prompt_eval_count"] for r in rs if r["prompt_eval_count"]}),
                   "correct": sum(r["correct"] for r in rs), "warn": warn[0] if warn else None,
                   "fresh_all": all(r["fresh_load"] for r in rs), "error": next((r["error"] for r in rs if r["error"]), None),
                   "reply_keys": rs[0]["reply_keys"], "answer_example": (rs[0]["answer"] or "")[:80]}
            out.append(row)
            body.append([row[x] for x in ("model", "endpoint", "fact", "extra", "num_ctx", "sampling", "status",
                                          "prompt_eval_count", "correct", "runs", "warn", "error")])
        res["truncation"] = out
        md.append("### P-TRUNC: a ~9.6K-token prompt (fact = line 1 or last line)\n" + md_table(
            ["model", "endpoint", "fact at", "extra", "num_ctx", "sampling", "HTTP", "prompt_eval_count", "right",
             "of", "WARN in log", "error"], body))
    f = jl(P("p13", "fit.jsonl"))
    if f:
        g = defaultdict(list)
        for r in f:
            g[(r["model"], r["kv_set"], r["num_ctx"], r["kind"])].append(r)
        out, body = [], []
        for k, rs in sorted(g.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], x[0][3])):
            ok = [r for r in rs if r.get("loads")]
            row = {"model": k[0], "kv_set": k[1], "num_ctx": k[2], "kind": k[3], "loads": f"{len(ok)}/{len(rs)}",
                   "kv_read_back": sorted({r["kv_type"] for r in ok}), "processor": sorted({r["processor"] for r in ok if r.get("processor")}),
                   "offload": sorted({tuple(r["offload"]) for r in ok if r.get("offload")}),
                   "gpu_mib_max_median": med([r["window"].get("gpu_mib_max") for r in ok]),
                   "container_ram_mib_max_median": med([r["window"].get("ram_mib_max") for r in ok]),
                   "prompt_tokens": med([r.get("prompt_eval_count") for r in ok]),
                   "prefill_tok_s_median": med([r.get("prefill_tok_s") for r in ok]),
                   "write_tok_s_median": med([r.get("write_tok_s") for r in ok]),
                   "prefill_s_median": med([r.get("prefill_s") for r in ok]),
                   "load_s_median": med([r.get("load_s") for r in ok]),
                   "error": next((r.get("error") for r in rs if r.get("error")), None),
                   "estimate_minutes": next((r.get("estimate_minutes") for r in rs if r.get("estimate_minutes")), None)}
            out.append(row)
            body.append([row[x] for x in ("model", "kv_set", "num_ctx", "kind", "loads", "kv_read_back", "processor",
                                          "offload", "gpu_mib_max_median", "container_ram_mib_max_median",
                                          "prompt_tokens", "prefill_tok_s_median", "write_tok_s_median",
                                          "prefill_s_median", "error")])
        res["fit"] = out
        md.append("### P-FIT: what loads (3 fresh loads per cell, medians)\n" + md_table(
            ["model", "KV set", "num_ctx", "kind", "loads", "KV in log", "PROCESSOR", "layers GPU", "GPU MiB max",
             "container MiB max", "prompt tok", "prefill tok/s", "write tok/s", "prefill s", "error"], body))
    return res, md


def summary_table(path, keys):
    s = jl(path)
    g = defaultdict(list)
    for r in s:
        g[tuple(str(r.get(k)) for k in keys)].append(r)
    return g


def p14():
    res, md = {"counts": []}, []
    g = summary_table(P("p14", "cant-summary.jsonl"), ["model", "section", "fix", "think"])
    body = []
    for k, rs in g.items():
        t0 = [r for r in rs if r["temp"] == 0]
        t1 = [r for r in rs if r["temp"] == 1.0]
        val = "passed" if "passed" in rs[0] else "title_matches"
        row = {"model": k[0], "section": k[1], "fix": k[2], "think": k[3],
               "temp0": t0[0][val] if t0 else None, "total": rs[0].get("total", rs[0].get("listed")),
               "temp1_range": rng([r[val] for r in t1]), "temp1_runs": len(t1)}
        if k[1] == "cite":
            row.update({"doi_resolves_temp0": t0[0]["doi_resolves"] if t0 else None,
                        "doi_resolves_temp1_range": rng([r["doi_resolves"] for r in t1]),
                        "listed_temp0": t0[0]["listed"] if t0 else None})
        res["counts"].append(row)
        body.append([row["model"], row["section"], row["fix"], row["think"], row["temp0"], row["total"],
                     row["temp1_range"], row["temp1_runs"], row.get("doi_resolves_temp0"),
                     row.get("doi_resolves_temp1_range")])
    md.append("### P-CANT counts (temp 0 seed 42; temp 1.0 range over runs)\n" + md_table(
        ["model", "section", "fix", "think", "temp 0", "of", "temp 1.0 range", "runs", "DOIs resolve (t0)",
         "DOIs resolve (t1 range)"], body))
    tok = P("p14", "tokenizer-dump.json")
    if os.path.exists(tok):
        res["tokenizer"] = json.load(open(tok, encoding="utf-8"))
    return res, md


def p15():
    res, md = {"can": []}, []
    for r in jl(P("p15", "can-summary.jsonl")):
        res["can"].append(r)
    body = []
    for r in res["can"]:
        v = r["result"]
        body.append([r["model"], r["section"], r["temperature"], r["rep"],
                     json.dumps(v) if isinstance(v, dict) else f"{v[0]}/{v[1]}"])
    md.append("### P-CAN scores\n" + md_table(["model", "section", "temp", "run", "passed"], body))
    a = jl(P("p15", "aud.jsonl"))
    if a:
        res["audio"] = [{k: r.get(k) for k in ("model", "item", "route", "status", "has_audio_capability", "wer",
                                               "answer", "error", "body")} for r in a]
        md.append("### P-AUD\n" + md_table(["model", "clip", "route", "HTTP", "WER", "reply / error"],
                                           [[r["model"], r["item"], r.get("route"), r["status"], r.get("wer"),
                                             (r.get("answer") or str(r.get("error") or r.get("body") or ""))[:90]
                                             .replace("|", "/").replace("\n", " ")] for r in a]))
    return res, md


def p16():
    res, md = {}, []
    n = jl(P("p16", "needle.jsonl"))
    g = defaultdict(list)
    for r in n:
        if r.get("status") == 200:
            g[(r["model"], r["num_ctx"], r["kind"], r.get("depth"))].append(r)
    out, body = [], []
    for k, rs in sorted(g.items(), key=lambda x: (x[0][0], x[0][1], x[0][2], -1 if x[0][3] is None else x[0][3])):
        row = {"model": k[0], "num_ctx": k[1], "kind": k[2], "depth": k[3], "score": sum(r["score"] for r in rs),
               "of": sum(r["of"] for r in rs), "runs": len(rs), "all_whole": all(r["arrived_whole"] for r in rs),
               "prefill_s_max": max((r.get("prefill_s") or 0) for r in rs),
               "prompt_tokens_max": max((r.get("prompt_eval_count") or 0) for r in rs)}
        out.append(row)
        body.append([row[x] for x in ("model", "num_ctx", "kind", "depth", "score", "of", "all_whole",
                                      "prompt_tokens_max", "prefill_s_max")])
    res["needle"] = out
    md.append("### P-NEEDLE\n" + md_table(["model", "num_ctx", "kind", "depth", "found", "of", "arrived whole",
                                           "prompt tokens (max)", "prefill s (max)"], body))
    return res, md


COMMANDS = {
    "p13": "`scripts/stage1.sh` = `scripts/lab.sh up f16; scripts/lab.sh run p13 def --models e2b,e4b,12b-qat; "
           "scripts/lab.sh run p13 trunc --reps 3; scripts/lab.sh run p_fit --kv f16 --models e2b,e4b,12b-qat; "
           "scripts/lab.sh up q8_0; scripts/lab.sh run p_fit --kv q8_0 --models e2b,e4b,12b-qat`; 26B rows: "
           "`scripts/stage4.sh`",
    "p14": "`scripts/lab.sh run p14 sources; scripts/lab.sh run p14 run --models e4b --t1reps 5; "
           "scripts/lab.sh run p14 run --models 12b-qat --t1reps 0; scripts/lab.sh run p14 tokens` (stage2.sh)",
    "p15": "`scripts/lab.sh run p15 aud --models e2b,e4b,12b-q4,12b-qat; scripts/lab.sh run p15 can --models "
           "e4b,12b-qat` (stage2.sh); `p15 can --models e4b,12b-qat --temp 1.0 --reps 5` (stage3.sh); "
           "`p15 can --models 26b --sections tools` (stage4.sh)",
    "p16": "`scripts/lab.sh run p16 run --models e4b --lengths 4096,...,131072; ... --models 12b-qat` (stage3.sh); "
           "26B short set in stage4.sh",
}


if __name__ == "__main__":
    for name, fn in (("p13", p13), ("p14", p14), ("p15", p15), ("p16", p16)):
        try:
            res, md = fn()
        except FileNotFoundError:
            continue
        if not res or not any(res.values()):
            continue
        os.makedirs(P(name), exist_ok=True)
        json.dump(res, open(P(name, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        open(P(name, "tables.md"), "w", encoding="utf-8").write("\n\n".join(md) + "\n")
        allrows = [r for f in os.listdir(P(name)) if f.endswith(".jsonl") and "summary" not in f
                   for r in jl(P(name, f))]
        tags = sorted({(r["tag"], r["digest"], r["mtp_draft"]) for r in allrows if "tag" in r})
        vers = sorted({r["ollama_version"] for r in allrows if "ollama_version" in r})
        head = [f"# {name.upper()} results (generated by `python -m lab.report`; raw rows in `out/{name}/*.jsonl`)", "",
                "- Engine: `ollama/ollama:0.40.16@sha256:910d0d8107b538fb0894e63163eb195de0cc7aefcbc666dc62d3b18f71124592`"
                f" (version reported by every row: {vers})",
                "- Host: RTX 4060 8 GB (about 3.0 GB held by the Windows desktop before any load), driver 610.88, "
                "Docker Desktop WSL 2, Ollama container cap 12g (16g for the 26B stage), OLLAMA_FLASH_ATTENTION=1, "
                "OLLAMA_NUM_PARALLEL=1, OLLAMA_KEEP_ALIVE=0",
                "- Tags (tag, digest, MTP draft): " + "; ".join(f"`{t}` {d} draft={m}" for t, d, m in tags),
                "- Commands: " + COMMANDS.get(name, ""),
                "- Server logs: `out/logs/` (archive: see LAB-STATUS.md)", ""]
        open(P(name, "RESULTS.md"), "w", encoding="utf-8").write("\n".join(head) + "\n" + "\n\n".join(md) + "\n")
        print(name, "ok")
