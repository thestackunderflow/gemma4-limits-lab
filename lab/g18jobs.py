"""g18 (PLAN rev 2 §5.2): the taste test. The 5 `llm` SolidCraft jobs (local-model-solidcraft-lab simple/tasks.py,
checked by its checker/simple.py), one setting changed at a time from the baseline. Pure parts only (tests/test_g18.py).

Winner rule (written before any row ran): score = jobs the checker passes at temp 0 seed 42 (rep 1), "k of 5 jobs";
a job with any cut line or a "length" stop is "ran out of room" (not right). Right per minute = right / job minutes
(model load excluded, reported apart). The winner is the non-baseline arm with the highest right per minute (ties:
more right, then fewer minutes). Null result (PLAN §8): every arm's temp-0 score within 1 job of every other arm's.
"""
import math

JOBS = ("new", "cube", "block", "hole", "resize")
MENU_TOKENS = 4469            # SolidCraft 0.28.0 menu on e4b (g17 G17-SIZE, out/g17/size/size.json)


def smallest_ctx(menu_tokens, room=4096, step=4096):
    """The smallest window holding the menu + 4K, rounded up to a multiple of 4,096."""
    return int(math.ceil((menu_tokens + room) / step) * step)


SMALL_CTX = smallest_ctx(MENU_TOKENS)
SYSTEM3 = ("Units are millimetres.\n"
           "Make one change per tool call.\n"
           "Check the design with inspect_design before you finish or export.")
SAMPLING = {"t0": {"temperature": 0}, "google": {"temperature": 1.0, "top_p": 0.95, "top_k": 64}}

_BASE = {"tag": "gemma4:e4b-it-q4_K_M", "num_ctx": SMALL_CTX, "think": False, "system": None}
ARMS = {
    "baseline": dict(_BASE),
    "e2b": dict(_BASE, tag="gemma4:e2b-it-q4_K_M"),
    "q12_qat": dict(_BASE, tag="gemma4:12b-it-qat"),
    "q12_q4km": dict(_BASE, tag="gemma4:12b-it-q4_K_M"),
    "think_on": dict(_BASE, think=True),
    "system3": dict(_BASE, system=SYSTEM3),
    "ctx_32k": dict(_BASE, num_ctx=32768),
}


def battery(arms, sampling, reps):
    """One line per job run: ID ARM JOB SAMPLING SEED (temp 0: seed 42 every rep; google: seed = rep)."""
    out = []
    for arm in arms:
        for job in JOBS:
            for r in range(1, reps + 1):
                seed = 42 if sampling == "t0" else r
                out.append("%s-%s-%s-r%d %s %s %s %d" % (arm, job, sampling, r, arm, job, sampling, seed))
    return out


def outcome(check, reqs):
    if check is None or not reqs or any(r.get("status") != 200 for r in reqs):
        return "error"
    if any(r.get("cuts") for r in reqs) or any(r.get("done_reason") == "length" for r in reqs):
        return "ran out of room"
    return "right" if check.get("pass") else "wrong"


def write_tps(reqs):
    ev = sum(r.get("eval_count") or 0 for r in reqs)
    ns = sum(r.get("eval_duration") or 0 for r in reqs)
    return round(ev / (ns / 1e9), 2) if ns else None


def job_seconds(wall, reqs):
    return round(wall - sum(r.get("load_duration") or 0 for r in reqs) / 1e9, 2)


def summarize(rows):
    """{arm: {sampling: {...}}}. temp 0: rep 1 is the score, later reps only set reps_identical. google: every rep."""
    out = {}
    for arm in sorted({r["arm"] for r in rows}):
        out[arm] = {}
        for samp in ("t0", "google"):
            rs = [r for r in rows if r["arm"] == arm and r["sampling"] == samp]
            if not rs:
                continue
            scored = [r for r in rs if r.get("rep", 1) == 1] if samp == "t0" else rs
            right = sum(r["outcome"] == "right" for r in scored)
            minutes = round(sum(r["job_seconds"] for r in scored) / 60, 3)
            s = {"right": right, "n": len(scored), "minutes": minutes,
                 "right_per_minute": round(right / minutes, 3) if minutes else None,
                 "outcomes": {o: sum(r["outcome"] == o for r in scored)
                              for o in ("right", "wrong", "ran out of room", "error")}}
            if samp == "t0":
                s["label"] = "%d of %d jobs" % (right, len(scored))
                first = {r["job"]: r for r in scored}
                later = [r for r in rs if r.get("rep", 1) > 1 and r["job"] in first]
                s["reps_identical"] = (all(r["call_names"] == first[r["job"]]["call_names"]
                                           and r["outcome"] == first[r["job"]]["outcome"] for r in later)
                                       if later else None)
            else:
                s["label"] = "%d of %d" % (right, len(scored))
                seeds = sorted({r["seed"] for r in rs})
                s["per_rep"] = [sum(r["outcome"] == "right" for r in rs if r["seed"] == sd) for sd in seeds]
            out[arm][samp] = s
    return out


def winner(summary):
    t0 = {a: v["t0"] for a, v in summary.items() if "t0" in v}
    incomplete = sorted(a for a, v in t0.items() if v["n"] < len(JOBS))
    t0 = {a: v for a, v in t0.items() if a not in incomplete}
    scores = [v["right"] for v in t0.values()]
    null = bool(scores) and max(scores) - min(scores) <= 1
    cands = [(a, v) for a, v in t0.items() if a != "baseline"]
    if not cands:
        return {"arm": None, "null": null, "incomplete": incomplete}
    a, v = max(cands, key=lambda kv: (kv[1]["right_per_minute"] or 0, kv[1]["right"], -kv[1]["minutes"]))
    base = t0.get("baseline")
    return {"arm": a, "null": null, "incomplete": incomplete, "right": v["right"], "right_per_minute": v["right_per_minute"],
            "baseline_right": base["right"] if base else None,
            "baseline_right_per_minute": base["right_per_minute"] if base else None,
            "beats_baseline": bool(base) and (v["right_per_minute"] or 0) > (base["right_per_minute"] or 0)}


def tool_json(text):
    """SolidCraft 0.28.0 headless appends a 'Note: ...' line after the JSON: read the JSON value at the start."""
    import json
    try:
        return json.JSONDecoder().raw_decode(text.lstrip())[0]
    except ValueError:
        return {"_text": text[:2000]}


def keep_warm(arm):
    """12B arms: one model load per arm, not per job (load seconds and job seconds then labelled warm)."""
    return ARMS[arm]["tag"].startswith("gemma4:12b")
