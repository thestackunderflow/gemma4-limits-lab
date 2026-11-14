"""g17 runner (stdlib only). Runs INSIDE sc5-app:0.28.0 (SolidCraft 0.28.0 + python3) sharing the Ollama container's
network; /work = this lab, /sc = local-model-solidcraft-lab (its MCP client and plate checker, read-only),
/lab/out = this chat's own folder (SolidCraft's allowed path). Driver: scripts/g17.sh.

    python3 -m lab.g17run size                      G17-SIZE (+ the lab-only context / truncate:false rows)
    python3 -m lab.g17run stateless                 G17-STATELESS (turn 2 alone, temp 0 + 5 temp-1 reps)
    python3 -m lab.g17run chat ID CTX FIX THINK SAMPLING SEED KEEP_ALIVE
        CTX: a number or 'default' (no num_ctx sent); FIX: none|pin|summary; THINK: true|false;
        SAMPLING: t0 (temperature 0) | google (1.0 / 0.95 / 64); KEEP_ALIVE: e.g. 5m or 0
Writes out/g17/<step>/... ; a chat writes out/g17/chats/ID/{requests.jsonl,tools.jsonl,summary.json} and the files
SolidCraft saved. summary.json is written last: a folder without it is a partial run (the driver sets it aside).
"""
import json
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request

from lab import g17chat as g, logparse

sys.path.insert(0, "/sc/harness")
sys.path.insert(0, "/sc")

URL = os.environ.get("OLLAMA", "http://127.0.0.1:11434")
ROOT = os.environ.get("G17_ROOT", "/work")   # filmed takes mount this lab at /g
LOG = ROOT + "/out/logs/server.log"
OUT = ROOT + "/out/g17"
TAG = os.environ.get("G17_TAG", "gemma4:e4b-it-q4_K_M")
CUT = 8000              # tool results cut as the llm lab's messenger did
MAX_ITER = 8            # model requests per user turn (tool loop cap)
SAMPLING = {"t0": {"temperature": 0}, "google": {"temperature": 1.0, "top_p": 0.95, "top_k": 64}}
SUMMARY_TURNS = (6, 11, 16)   # fix (c): before these turns the app asks for a spec so far (every 5 turns)
SUMMARY_ASK = ("Write a short spec of our chat so far, under 80 words: first the original spec from my first message "
               "(part name, material, every size and the holes), then the current variant. No tools.")


def post(path, body, timeout=1800):
    data = json.dumps(body).encode()
    req = urllib.request.Request(URL + path, data=data, headers={"Content-Type": "application/json"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, raw = e.code, e.read()
    try:
        js = json.loads(raw)
    except ValueError:
        js = {"_text": raw[:2000].decode("utf-8", "replace")}
    return status, js, round(time.time() - t0, 2), len(data)


def get(path):
    with urllib.request.urlopen(URL + path, timeout=60) as r:
        return json.loads(r.read())


def mark():
    return os.path.getsize(LOG) if os.path.exists(LOG) else 0


def since(m, settle=0.4):
    time.sleep(settle)
    with open(LOG, "rb") as f:
        f.seek(m)
        return f.read().decode("utf-8", "replace")


def unload():
    for m in get("/api/ps").get("models", []):
        post("/api/generate", {"model": m["name"], "keep_alive": 0})
    for _ in range(120):
        if not get("/api/ps").get("models"):
            return True
        time.sleep(0.5)
    return False


def provenance(extra=None):
    show = post("/api/show", {"model": TAG})[1]
    dig = next((m["digest"][:12] for m in get("/api/tags")["models"] if m["name"] == TAG), None)
    p = {"tag": TAG, "digest": dig, "ollama_version": get("/api/version")["version"],
         "renderer": show.get("renderer"), "parser": show.get("parser"),
         "num_parallel": os.environ.get("OLLAMA_NUM_PARALLEL"), "kv_type_env": os.environ.get("OLLAMA_KV_CACHE_TYPE"),
         "solidcraft": os.environ.get("SC_VERSION"), "t": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    p.update(extra or {})
    return p


def tools_from(mcp):
    return [{"type": "function", "function": {"name": t["name"], "description": t.get("description", ""),
                                              "parameters": t.get("inputSchema", {"type": "object"})}}
            for t in mcp.request("tools/list", {})["tools"]]


def mcp_start(path="/lab/out"):
    from mcp_client import McpClient
    m = McpClient(["solidcraft-cli", "mcp", "--allow-path", path])
    m.start()
    return m


def fields(js):
    keep = ("done_reason", "prompt_eval_count", "prompt_eval_cached_count", "prompt_eval_duration", "eval_count",
            "eval_duration", "load_duration", "total_duration")
    return {k: js.get(k) for k in keep}


def counted(messages, tools, ctx, think=False):
    """One counted request (num_predict 1) + the rendered string (_debug_render_only)."""
    body = {"model": TAG, "messages": messages, "stream": False, "keep_alive": "5m", "think": think,
            "options": {"num_ctx": ctx, "temperature": 0, "seed": 42, "num_predict": 1}}
    if tools:
        body["tools"] = tools
    r = post("/api/chat", dict(body, _debug_render_only=True))[1]
    rendered = (r.get("debug_info") or {}).get("rendered_template")
    m = mark()
    st, js, secs, nbytes = post("/api/chat", body)
    return {"status": st, **fields(js), "cuts": logparse.cuts(since(m)), "rendered_chars": len(rendered or ""),
            "request_bytes": nbytes}, rendered


# -- G17-SIZE --------------------------------------------------------------------------------------------------------
def step_size():
    d = os.path.join(OUT, "size")
    os.makedirs(d, exist_ok=True)
    mcp = mcp_start()
    tools = tools_from(mcp)
    mcp.close()
    json.dump(tools, open(os.path.join(d, "tools.json"), "w"), indent=1)
    unload()
    cube = [{"role": "user", "content": "make a 20 mm cube"}]
    sysm = [{"role": "system", "content": g.SYSTEM}]
    rows = []
    for name, msgs, tl in [("cube_no_tools", cube, None), ("cube_with_tools", cube, tools),
                           ("system_cube_no_tools", sysm + cube, None), ("system_cube_with_tools", sysm + cube, tools),
                           ("system_turn1_with_tools", sysm + [{"role": "user", "content": g.TURNS[0]}], tools),
                           ("pinned_system_turn1_with_tools",
                            [{"role": "system", "content": g.SYSTEM + "\n" + g.PIN}, {"role": "user", "content": g.TURNS[0]}],
                            tools)]:
        r, rendered = counted(msgs, tl, 32768)
        r["name"] = name
        rows.append(r)
        open(os.path.join(d, "rendered-%s.txt" % name), "w", encoding="utf-8").write(rendered or "")
    # the same with the default window (no num_ctx): Part 13's runner cut takes the middle
    body = {"model": TAG, "messages": sysm + [{"role": "user", "content": g.TURNS[0]}], "tools": tools, "stream": False,
            "keep_alive": "5m", "think": False, "options": {"temperature": 0, "seed": 42, "num_predict": 1}}
    m = mark()
    st, js, secs, _ = post("/api/chat", body)
    lg = since(m)
    rows.append({"name": "system_turn1_with_tools_default_ctx", "status": st, **fields(js), "cuts": logparse.cuts(lg),
                 "default_context": logparse.default_context(lg), "ctx_arg": logparse.ctx_arg(lg)})
    # lab-only rows (README, not filmed): truncate:false over the window, and the deprecated context array
    long_hist = sysm + [{"role": "user", "content": ("Plate note %d: 60 x 40 x 5 mm. " % i) * 30} for i in range(12)]
    st, js, _, _ = post("/api/chat", {"model": TAG, "messages": long_hist, "stream": False, "keep_alive": "5m",
                                      "think": False, "truncate": False, "options": {"num_ctx": 2048, "num_predict": 4}})
    rows.append({"name": "truncate_false_over_window", "status": st, "error": js.get("error"), **fields(js)})
    m = mark()
    st1, j1, _, _ = post("/api/generate", {"model": TAG, "prompt": "Remember this: part BRK-17 is a plate 60 x 40 x 5 "
                                           "mm in PETG. Reply OK.", "stream": False, "keep_alive": "5m", "think": False,
                                           "options": {"temperature": 0, "seed": 42, "num_ctx": 8192}})
    st2, j2, _, _ = post("/api/generate", {"model": TAG, "prompt": "What size and material is part BRK-17?",
                                           "context": j1.get("context"), "stream": False, "keep_alive": "5m",
                                           "think": False, "options": {"temperature": 0, "seed": 42, "num_ctx": 8192}})
    lg = since(m)
    rows.append({"name": "context_array_recall", "status": [st1, st2], "context_len": len(j1.get("context") or []),
                 "reply": j2.get("response"), "recall": g.recall(j2.get("response")),
                 "deprecated_warn": "context field is deprecated" in lg, "returned_context": bool(j2.get("context")),
                 **fields(j2)})
    unload()
    res = {"provenance": provenance(), "n_tools": len(tools), "tools_json_chars": len(json.dumps(tools)), "rows": rows}
    json.dump(res, open(os.path.join(d, "size.json"), "w"), indent=1)
    print(json.dumps({r["name"]: (r.get("prompt_eval_count"), r.get("status")) for r in rows}))


# -- G17-STATELESS ---------------------------------------------------------------------------------------------------
def knows_plate(text):
    return bool(re.search(r"(?<![\d.])60(?![\d])", text) and re.search(r"(?<![\d.])40(?![\d])", text))


def step_stateless():
    d = os.path.join(OUT, "stateless")
    os.makedirs(d, exist_ok=True)
    mcp = mcp_start()
    tools = tools_from(mcp)
    mcp.close()
    unload()
    rows = []
    for samp, seed in [("t0", 42)] + [("google", s) for s in range(1, 6)]:
        body = {"model": TAG, "stream": False, "keep_alive": "5m", "think": False, "tools": tools,
                "messages": [{"role": "system", "content": g.SYSTEM}, {"role": "user", "content": g.TURNS[1]}],
                "options": dict(SAMPLING[samp], num_ctx=16384, seed=seed)}
        st, js, secs, _ = post("/api/chat", body)
        msg = js.get("message") or {}
        text = (msg.get("content") or "") + json.dumps(msg.get("tool_calls") or [])
        rows.append({"sampling": samp, "seed": seed, "status": st, **fields(js), "content": msg.get("content"),
                     "tool_calls": msg.get("tool_calls"), "knows_plate": knows_plate(text), "seconds": secs})
    unload()
    json.dump({"provenance": provenance({"num_ctx": 16384, "think": False}), "rows": rows},
              open(os.path.join(d, "stateless.json"), "w"), indent=1)
    print(json.dumps([(r["sampling"], r["knows_plate"]) for r in rows]))


# -- one design chat -------------------------------------------------------------------------------------------------
def step_chat(cid, ctx, fix, think, samp, seed, keep_alive):
    d = os.path.join(OUT, "chats", cid)
    os.makedirs(d, exist_ok=True)
    reqf = open(os.path.join(d, "requests.jsonl"), "w", encoding="utf-8")
    toolf = open(os.path.join(d, "tools.jsonl"), "w", encoding="utf-8")
    think_b = think == "true"
    opts = dict(SAMPLING[samp], seed=int(seed))
    if ctx != "default":
        opts["num_ctx"] = int(ctx)
    ka = 0 if keep_alive == "0" else keep_alive
    system = {"role": "system", "content": g.SYSTEM + ("\n" + g.PIN if fix == "pin" else "")}
    mcp = mcp_start()
    tools = tools_from(mcp)
    unload()
    turns, reqs, summary, summaries = [], [], None, []
    t_start = time.time()

    def send(msgs, turn, kind, with_tools=True):
        body = {"model": TAG, "messages": msgs, "stream": False, "keep_alive": ka, "think": think_b, "options": opts}
        if with_tools:
            body["tools"] = tools
        loaded = bool(get("/api/ps").get("models"))
        m = mark()
        st, js, secs, nbytes = post("/api/chat", body)
        lg = since(m)
        cuts = logparse.cuts(lg)
        mcut = next((c for c in cuts if c["kind"] != "runner_token_cut"), None)
        msg = js.get("message") or {}
        row = {"turn": turn, "kind": kind, "status": st, **fields(js), "seconds": secs, "request_bytes": nbytes,
               "n_msgs": len(msgs), "loaded_before": loaded, "cuts": cuts,
               "turn1_kept": g.turn1_kept(msgs, mcut) if any(x.get("content") == g.TURNS[0] for x in msgs) else False,
               "runner_cut": any(c["kind"] == "runner_token_cut" for c in cuts),
               "content": (msg.get("content") or "")[:3000], "thinking_chars": len(msg.get("thinking") or ""),
               "tool_calls": [{"name": c.get("function", {}).get("name"), "arguments": c.get("function", {}).get("arguments")}
                              for c in (msg.get("tool_calls") or [])],
               "error": js.get("error"), "offload": logparse.offload(lg), "kv_type": logparse.kv_type(lg)}
        if kind == "summary":
            row["summary"] = True
        reqs.append(row)
        reqf.write(json.dumps(row, ensure_ascii=False) + "\n")
        reqf.flush()
        if os.environ.get("G17_LIVE"):   # filmed takes: one short line per request (<= 44 columns)
            print("t%-2d sent %5s reused %5s %s%s" % (turn, row["prompt_eval_count"], row["prompt_eval_cached_count"],
                  "CUT " if mcut else "", "summary" if kind == "summary" else ",".join(c["name"] for c in row["tool_calls"])[:14]),
                  flush=True)
        return row, msg

    def window(cur):
        if fix == "summary":
            return g.window_summary(system, summary, turns + [cur], keep=4 + 1)  # the last 4 turns + the current one
        return [system] + [m for t in turns + [cur] for m in t]

    try:
        for t in range(1, 21):
            if fix == "summary" and t in SUMMARY_TURNS:
                msgs = (g.window_summary(system, summary, turns, keep=4)
                        + [{"role": "user", "content": SUMMARY_ASK}])
                row, msg = send(msgs, t, "summary", with_tools=False)
                summary = (msg.get("content") or "").replace(g.MARKER, "").strip()
                summaries.append({"before_turn": t, "text": summary, "recall": g.recall(summary)})
            if t == 20 and os.path.exists("/lab/out/plate.stl"):
                shutil.move("/lab/out/plate.stl", "/lab/out/plate.before-turn20.stl")
            cur = [{"role": "user", "content": g.TURNS[t - 1]}]
            for it in range(MAX_ITER):
                row, msg = send(window(cur), t, "turn")
                hist = {k: v for k, v in msg.items() if v not in (None, "", [])}
                hist.update({"role": "assistant", "content": msg.get("content") or ""})
                cur.append(hist)
                calls = msg.get("tool_calls") or []
                if row["status"] != 200 or row["done_reason"] != "stop" or not calls:
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
                    toolf.write(json.dumps({"turn": t, "name": fn.get("name"), "arguments": args, "isError": err,
                                            "result": text[:600], "result_chars": len(text)}) + "\n")
                    toolf.flush()
                    cur.append({"role": "tool", "content": text[:CUT], "tool_name": fn.get("name")})
            turns.append(cur)
    finally:
        mcp.close()
        reqf.close()
        toolf.close()
    finals = [r for r in reqs if r["kind"] == "turn"]
    last_by_turn = {}
    for r in finals:
        last_by_turn[r["turn"]] = r
    t20 = last_by_turn.get(20, {})
    stl = "/lab/out/plate.stl"
    check = None
    if os.path.exists(stl):
        try:
            from checker.plate import measure
            from checker.stl import read_stl
            check = measure(read_stl(stl), spacing=36)
        except Exception as e:  # noqa: BLE001
            check = {"pass": False, "error": repr(e)}
    ttok = g.tokens_per_turn(reqs)
    s = {"id": cid, "provenance": provenance({"num_ctx": ctx, "fix": fix, "think": think_b, "sampling": samp,
                                              "options": opts, "keep_alive": ka, "max_iter": MAX_ITER, "tool_cut": CUT}),
         "n_requests": len(reqs), "minutes": round((time.time() - t_start) / 60, 2),
         "first_message_drop_turn": g.first_turn(finals, lambda r: any(c["kind"] != "runner_token_cut" for c in r["cuts"])),
         "first_turn1_gone_turn": g.first_turn(finals, lambda r: r["turn1_kept"] is False),
         "first_runner_cut_turn": g.first_turn(finals, lambda r: r["runner_cut"]),
         "all_http_200": all(r["status"] == 200 for r in reqs),
         "done_reasons": sorted({str(r["done_reason"]) for r in reqs}),
         "marker_by_turn": {t: g.marker_ok(r["content"]) for t, r in last_by_turn.items()},
         "tokens_per_turn": ttok, "mean_tokens_per_turn": round(sum(ttok.values()) / max(len(ttok), 1), 1),
         "max_prompt_eval_count": max((r["prompt_eval_count"] or 0) for r in reqs) if reqs else None,
         "tool_calls": sum(len(r["tool_calls"]) for r in reqs),
         "turn20_text": t20.get("content"), "turn20_recall": g.recall(t20.get("content")),
         "turn20_stl": os.path.exists(stl), "checker": check, "summaries": summaries}
    json.dump(s, open(os.path.join(d, "summary.json"), "w"), indent=1, ensure_ascii=False)
    print(json.dumps({k: s[k] for k in ("id", "n_requests", "minutes", "first_message_drop_turn", "first_turn1_gone_turn",
                                        "first_runner_cut_turn", "mean_tokens_per_turn", "tool_calls")}
                     | {"recall": s["turn20_recall"]["score"], "pass": (check or {}).get("pass")}))


if __name__ == "__main__":
    step = sys.argv[1]
    if step == "size":
        step_size()
    elif step == "stateless":
        step_stateless()
    elif step == "chat":
        step_chat(*sys.argv[2:9])
