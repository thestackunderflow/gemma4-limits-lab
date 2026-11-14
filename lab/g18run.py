"""g18 runner (stdlib + the llm lab's checker). Runs INSIDE sc5-app:0.28.0 on the Ollama container's network, like
g17run (same HTTP, log-cut and MCP helpers). Driver: scripts/g18.sh.

    python3 -m lab.g18run job ID ARM JOB SAMPLING SEED

One MCP process per job (headless SolidCraft keeps its design per process): new_design (+ the 20 mm cube for 'new'
and 'resize', a scripted execute, no AI), the model's tool loop (max 8 requests, results cut at 8,000 chars as in the
llm lab), then the check with the same process: inspect_design (+ export check.stl for 'hole') scored by
/sc simple/tasks.py. Fresh load per job (unload first); load seconds are reported apart from the job seconds.
Writes out/g18/runs/ID/{requests.jsonl, tools.jsonl, check.json, summary.json}; summary.json last.
"""
import json
import os
import sys
import time

from lab import g18jobs as j, logparse
from lab.g17run import fields, get, mark, mcp_start, post, since, tools_from, unload

sys.path.insert(0, "/sc/harness")
sys.path.insert(0, "/sc")

OUT = os.path.join(os.environ.get("G18_ROOT", "/work"), "out", "g18")
MAX_ITER = 8
CUT = 8000


def text_json(res):
    return j.tool_json("\n".join(x["text"] for x in res.get("content", []) if x.get("type") == "text"))


def provenance(tag):
    show = post("/api/show", {"model": tag})[1]
    dig = next((m["digest"][:12] for m in get("/api/tags")["models"] if m["name"] == tag), None)
    return {"tag": tag, "digest": dig, "ollama_version": get("/api/version")["version"],
            "renderer": show.get("renderer"), "parser": show.get("parser"),
            "num_parallel": os.environ.get("OLLAMA_NUM_PARALLEL"), "kv_type_env": os.environ.get("OLLAMA_KV_CACHE_TYPE"),
            "solidcraft": os.environ.get("SC_VERSION"), "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}


def step_job(rid, arm_name, job, samp, seed):
    from simple.tasks import TASKS, score
    arm = j.ARMS[arm_name]
    d = os.path.join(OUT, "runs", rid)
    os.makedirs(d, exist_ok=True)
    opts = dict(j.SAMPLING[samp], seed=int(seed), num_ctx=arm["num_ctx"])
    mcp = mcp_start()
    tools = tools_from(mcp)
    setup = {"new_design": text_json(mcp.call_tool("new_design", {}))}
    if TASKS[job]["setup"] == "cube":
        setup["box"] = text_json(mcp.call_tool("execute", {"command": "solid.box",
                                                           "params": {"length": 20, "width": 20, "height": 20}}))
    setup["inspect"] = text_json(mcp.call_tool("inspect_design", {}))
    warm = j.keep_warm(arm_name)
    loaded = [m["name"] for m in get("/api/ps").get("models", [])]
    if not (warm and loaded == [arm["tag"]]):
        unload()
    msgs = ([{"role": "system", "content": arm["system"]}] if arm["system"] else []) + [
        {"role": "user", "content": TASKS[job]["prompt"]}]
    reqs, ps = [], None
    reqf = open(os.path.join(d, "requests.jsonl"), "w", encoding="utf-8")
    toolf = open(os.path.join(d, "tools.jsonl"), "w", encoding="utf-8")
    t0 = time.time()
    try:
        for it in range(MAX_ITER):
            body = {"model": arm["tag"], "messages": msgs, "tools": tools, "stream": False, "keep_alive": "10m" if warm else "5m",
                    "think": arm["think"], "options": opts}
            m = mark()
            st, js, secs, nbytes = post("/api/chat", body)
            lg = since(m)
            if ps is None:
                ps = get("/api/ps").get("models")
            msg = js.get("message") or {}
            calls = msg.get("tool_calls") or []
            row = {"i": it, "status": st, **fields(js), "seconds": secs, "request_bytes": nbytes,
                   "cuts": logparse.cuts(lg), "offload": logparse.offload(lg), "draft_loaded": logparse.draft_loaded(lg),
                   "kv_type": logparse.kv_type(lg), "content": (msg.get("content") or "")[:2000],
                   "thinking_chars": len(msg.get("thinking") or ""), "error": js.get("error"),
                   "tool_calls": [{"name": c.get("function", {}).get("name"),
                                   "arguments": c.get("function", {}).get("arguments")} for c in calls]}
            reqs.append(row)
            reqf.write(json.dumps(row, ensure_ascii=False) + "\n")
            reqf.flush()
            hist = {k: v for k, v in msg.items() if v not in (None, "", [])}
            hist.update({"role": "assistant", "content": msg.get("content") or ""})
            msgs.append(hist)
            if st != 200 or row["done_reason"] != "stop" or not calls:
                break
            for c in calls:
                fn = c.get("function", {})
                args = fn.get("arguments") if isinstance(fn.get("arguments"), dict) else {"_raw": fn.get("arguments")}
                try:
                    res = mcp.call_tool(fn.get("name"), args)
                    text = "\n".join(x["text"] for x in res.get("content", []) if x.get("type") == "text")
                    err = bool(res.get("isError"))
                except Exception as e:  # noqa: BLE001
                    text, err = "error: %s" % e, True
                toolf.write(json.dumps({"i": it, "name": fn.get("name"), "arguments": args, "isError": err,
                                        "result": text[:600], "result_chars": len(text)}) + "\n")
                toolf.flush()
                msgs.append({"role": "tool", "content": text[:CUT], "tool_name": fn.get("name")})
        wall = round(time.time() - t0, 2)
        ins = text_json(mcp.call_tool("inspect_design", {}))
        tris, exp = None, None
        if job == "hole" and isinstance(ins, dict) and len(ins.get("bodies") or []) == 1:
            stl = "/lab/out/check.stl"
            exp = text_json(mcp.call_tool("export", {"path": stl}))
            if os.path.exists(stl):
                from checker.stl import read_stl
                tris = read_stl(stl)
        try:
            check = score(job, ins if isinstance(ins, dict) else {}, tris)
        except Exception as e:  # noqa: BLE001
            check = {"pass": False, "error": repr(e)}
    finally:
        mcp.close()
        reqf.close()
        toolf.close()
    if not warm:
        unload()
    json.dump({"setup": setup, "check": check, "export": exp, "inspect": ins}, open(os.path.join(d, "check.json"), "w"),
              indent=1, default=str)
    s = {"id": rid, "arm": arm_name, "job": job, "sampling": samp, "seed": int(seed),
         "rep": int(rid.rsplit("-r", 1)[1]) if "-r" in rid else 1,
         "provenance": dict(provenance(arm["tag"]), num_ctx=arm["num_ctx"], think=arm["think"],
                            system=arm["system"], options=opts, max_iter=MAX_ITER, tool_cut=CUT),
         "warm_model": warm, "loaded_before": loaded, "n_requests": len(reqs), "wall_seconds": wall, "job_seconds": j.job_seconds(wall, reqs),
         "load_seconds": round(sum(r.get("load_duration") or 0 for r in reqs) / 1e9, 2),
         "write_tps": j.write_tps(reqs), "prompt_eval_first": reqs[0].get("prompt_eval_count") if reqs else None,
         "max_prompt_eval": max((r.get("prompt_eval_count") or 0) for r in reqs) if reqs else None,
         "done_reasons": sorted({str(r["done_reason"]) for r in reqs}), "statuses": sorted({r["status"] for r in reqs}),
         "cuts": [c for r in reqs for c in r["cuts"]], "offload": next((r["offload"] for r in reqs if r["offload"]), None),
         "draft_loaded": any(r["draft_loaded"] for r in reqs), "api_ps": ps,
         "thinking_chars": sum(r["thinking_chars"] for r in reqs),
         "call_names": [c["name"] for r in reqs for c in r["tool_calls"]],
         "pass": bool((check or {}).get("pass")), "outcome": j.outcome(check, reqs)}
    json.dump(s, open(os.path.join(d, "summary.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: s[k] for k in ("id", "outcome", "job_seconds", "load_seconds", "write_tps", "n_requests")}))


if __name__ == "__main__":
    if sys.argv[1] == "job":
        step_job(*sys.argv[2:7])
