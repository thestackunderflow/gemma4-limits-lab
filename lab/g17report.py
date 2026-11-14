"""g17: every number for the script, computed from the rows -> out/g17/results.json (nothing typed by hand).
    python -m lab.g17report
Winner rule (written before battery 2 finished): an arm is "right" in a chat when the turn-20 STL passes the plate
checker (60 x 40 x 5, two 4.5 mm through holes 36 mm apart) AND the turn-20 reply lists all 8 facts. Eligible arms are
right at temp 0 and in >= 4 of 5 Google-sampling reps; the winner is the eligible arm with the fewest mean prompt
tokens per turn. With no eligible arm, the arm with the most right chats (then fewest tokens) is named, flagged."""
import json
import os
import re

from lab import g17chat as g

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "g17")


def load(p):
    return json.load(open(p, encoding="utf-8"))


def reqs(cid):
    p = os.path.join(OUT, "chats", cid, "requests.jsonl")
    return [json.loads(x) for x in open(p, encoding="utf-8") if x.strip()]


def chat(cid):
    p = os.path.join(OUT, "chats", cid, "summary.json")
    return load(p) if os.path.exists(p) else None


def knows_plate(text):
    return bool(re.search(r"(?<![\d.])60(?![\d])", text) and re.search(r"(?<![\d.])40(?![\d])", text))


def right(s):
    return bool(s and (s.get("checker") or {}).get("pass") and s["turn20_recall"]["score"] == 8)


def secs_per_turn(cid):
    t = {}
    for r in reqs(cid):
        t[r["turn"]] = t.get(r["turn"], 0) + (r["seconds"] or 0)
    return round(sum(t.values()) / len(t), 2) if t else None


def brief(cid):
    s = chat(cid)
    if not s:
        return None
    rr = reqs(cid)
    return {"id": cid, "num_ctx": s["provenance"]["num_ctx"], "fix": s["provenance"]["fix"],
            "sampling": s["provenance"]["sampling"], "seed": s["provenance"]["options"].get("seed"),
            "turn1_gone_turn": s["first_turn1_gone_turn"], "message_drop_turn": s["first_message_drop_turn"],
            "runner_cut_turn": s["first_runner_cut_turn"], "all_http_200": s["all_http_200"],
            "done_reasons": s["done_reasons"], "length_stops": sum(r["done_reason"] == "length" for r in rr),
            "marker_kept_turns": sum(bool(v) for v in s["marker_by_turn"].values()),
            "recall": s["turn20_recall"]["score"], "recall_missing": s["turn20_recall"]["missing"],
            "stale_values": s["turn20_recall"]["stale"], "stl": s["turn20_stl"],
            "checker_pass": (s.get("checker") or {}).get("pass"), "checker_size": (s.get("checker") or {}).get("size"),
            "right": right(s), "mean_tokens_per_turn": s["mean_tokens_per_turn"],
            "seconds_per_turn": secs_per_turn(cid), "requests": s["n_requests"], "tool_calls": s["tool_calls"],
            "minutes": s["minutes"], "summaries_recall": [x["recall"]["score"] for x in s.get("summaries", [])]}


def reuse(cid):
    rr = [r for r in reqs(cid) if r["status"] == 200]
    s = chat(cid)
    d = s["first_message_drop_turn"] if s else None

    def agg(rows):
        sent = sum(r["prompt_eval_count"] or 0 for r in rows)
        cached = sum(r["prompt_eval_cached_count"] or 0 for r in rows)
        return {"requests": len(rows), "sent": sent, "reused": cached,
                "reused_pct": round(100 * cached / sent, 1) if sent else None}
    out = {"all": agg(rr), "per_turn_last_request": {}}
    for r in rr:
        out["per_turn_last_request"][r["turn"]] = [r["prompt_eval_count"], r["prompt_eval_cached_count"]]
    if d:
        out["before_first_drop"] = agg([r for r in rr if r["turn"] < d])
        out["from_first_drop"] = agg([r for r in rr if r["turn"] >= d])
        out["drop_requests"] = agg([r for r in rr if any(c["kind"] != "runner_token_cut" for c in r["cuts"])])
    out["loads"] = sum(1 for r in rr if (r.get("load_duration") or 0) > 1e9)
    out["load_s_total"] = round(sum((r.get("load_duration") or 0) for r in rr) / 1e9, 1)
    out["prefill_s_total"] = round(sum((r.get("prompt_eval_duration") or 0) for r in rr) / 1e9, 1)
    return out


def arm(prefix, t0_id):
    t0 = brief(t0_id)
    reps = [b for b in (brief(f"{prefix}-g{s}") for s in range(1, 6)) if b]
    rights = sum(b["right"] for b in reps)
    return {"t0": t0, "reps": reps, "reps_done": len(reps), "reps_right": rights,
            "reps_recall": [b["recall"] for b in reps], "reps_pass": [b["checker_pass"] for b in reps],
            "reps_turn1_gone": [b["turn1_gone_turn"] for b in reps],
            "mean_tokens_per_turn_all": round(sum(b["mean_tokens_per_turn"] for b in ([t0] if t0 else []) + reps)
                                              / max(len(reps) + bool(t0), 1), 1),
            "seconds_per_turn_all": round(sum(b["seconds_per_turn"] for b in ([t0] if t0 else []) + reps)
                                          / max(len(reps) + bool(t0), 1), 2),
            "right_total": rights + bool(t0 and t0["right"]), "chats": len(reps) + bool(t0),
            "recall_total": sum(b["recall"] for b in ([t0] if t0 else []) + reps),
            "recall8_chats": sum(b["recall"] == 8 for b in ([t0] if t0 else []) + reps),
            "checker_pass_chats": sum(bool(b["checker_pass"]) for b in ([t0] if t0 else []) + reps),
            "length_stops": sum(b["length_stops"] for b in ([t0] if t0 else []) + reps),
            "turn1_gone": [b["turn1_gone_turn"] for b in ([t0] if t0 else []) + reps]}


def md(r):
    """RESULTS-g17.md: generated from results.json (copied to the plan folder by hand, never edited)."""
    d, f, z = r["drop"], r["fix"], r["size"]
    L = ["# RESULTS g17 (generated by lab/g17report.py from out/g17/results.json; do not edit)", "",
         "Model %s (%s), Ollama %s, renderer %s, SolidCraft %s, NUM_PARALLEL %s, KV %s, think off unless said." % (
             r["provenance"]["tag"], r["provenance"]["digest"], r["provenance"]["ollama_version"],
             r["provenance"]["renderer"], r["provenance"]["solidcraft"], r["provenance"]["num_parallel"],
             r["provenance"]["kv_type_env"]), "",
         "## Size (G17-SIZE)",
         "- SolidCraft menu: %d tools, %d tokens (cube with tools %d, without %d); system + menu + turn 1 = %d; "
         "with the pinned spec %d." % (z["n_tools"], z["menu_tokens"], z["cube_with_tools"], z["cube_no_tools"],
                                       z["system_tools_turn1"], z["pinned_system_tools_turn1"]),
         "- Default window row: cuts %s (Part 13's runner cut takes the middle: menu + instructions)." %
         json.dumps(z["default_ctx_row"]["cuts"]),
         "- Lab only: truncate false -> HTTP %s; context array: warn %s, recall %d of 8." % (
             z["lab_only_truncate_false"]["status"], z["lab_only_context_array"]["deprecated_warn"],
             z["lab_only_context_array"]["recall"]), "",
         "## Stateless (G17-STATELESS)",
         "- Turn 2 alone knows the plate: temp 0 %s; Google sampling %d of %d; tool calls in %d of %d (every reply asks what to change). "
         "With the list (turn 2 inside the 16K chat) it acted on the plate with tools: %s." % (
             r["stateless"]["turn2_alone_knows_plate_t0"], r["stateless"]["turn2_alone_knows_plate_google"],
             r["stateless"]["google_reps"], r["stateless"]["turn2_alone_tool_calls"], r["stateless"]["google_reps"] + 1,
             [h["acted_on_plate"] for h in r["stateless"]["turn2_with_history"]]), "",
         "## The drop (G17-DROP, temp 0, then Google-sampling reps)",
         "| window | turn 1 gone at turn | first message drop | runner cut | all 200 | length stops | recall | checker |",
         "|---|---|---|---|---|---|---|---|"]
    for w in ("8k", "16k", "32k", "default"):
        b = d[w]
        if b:
            L.append("| %s | %s | %s | %s | %s | %s | %s/8 | %s |" % (w, b["turn1_gone_turn"], b["message_drop_turn"],
                     b["runner_cut_turn"], b["all_http_200"], b["length_stops"], b["recall"], b["checker_pass"]))
    L += ["- Turn 1 gone, Google sampling reps: 8K %s; 16K %s." % (d["8k_turn1_gone_range"], d["16k_turn1_gone_range"]), "",
          "## Reuse (G17-REUSE): prompt tokens reused from the cache / sent"]
    for k, v in r["reuse"].items():
        L.append("- %s: %s of %s (%s%%)%s; loads %s (%s s)" % (k, v["all"]["reused"], v["all"]["sent"], v["all"]["reused_pct"],
                 ("; before the first drop %s%%, from it %s%%, drop requests %s%%" % (v["before_first_drop"]["reused_pct"],
                  v["from_first_drop"]["reused_pct"], v["drop_requests"]["reused_pct"])) if "before_first_drop" in v else "",
                 v["loads"], v["load_s_total"]))
    L += ["", "## Fixes (G17-FIX): right = checker pass AND 8/8 facts at turn 20",
          "| arm | temp 0 right | reps right | reps recall | 8/8 chats | checker pass | length stops | turn 1 gone (t0, reps) | tokens per turn | seconds per turn |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k, v in f.items():
        L.append("| %s | %s | %s of %s | %s | %s of %s | %s of %s | %s | %s | %s | %s |" % (k, v["t0"] and v["t0"]["right"],
                 v["reps_right"], v["reps_done"], v["reps_recall"], v["recall8_chats"], v["chats"], v["checker_pass_chats"],
                 v["chats"], v["length_stops"], v["turn1_gone"], v["mean_tokens_per_turn_all"], v["seconds_per_turn_all"]))
    w = r["winner"]
    L += ["", "**Winner:** %s (%s right, %s tokens per turn)%s." % (w["arm"], w["right"], w["mean_tokens_per_turn"],
                                                                 "; " + w["flag"] if w["flag"] else ""),
          "Most chats with all 8 facts at turn 20: %s (%s)." % (w["best_recall_arm"], w["best_recall_8of8"]), ""]
    return "\n".join(L)


def main():
    size = load(os.path.join(OUT, "size", "size.json"))
    rows = {r["name"]: r for r in size["rows"]}
    st = load(os.path.join(OUT, "stateless", "stateless.json"))
    res = {"video": "g17", "provenance": size["provenance"], "winner_rule": __doc__.split("Winner rule")[1].strip()}
    res["size"] = {
        "n_tools": size["n_tools"], "tools_json_chars": size["tools_json_chars"],
        "menu_tokens": rows["cube_with_tools"]["prompt_eval_count"] - rows["cube_no_tools"]["prompt_eval_count"],
        "cube_no_tools": rows["cube_no_tools"]["prompt_eval_count"],
        "cube_with_tools": rows["cube_with_tools"]["prompt_eval_count"],
        "system_tools_turn1": rows["system_turn1_with_tools"]["prompt_eval_count"],
        "pinned_system_tools_turn1": rows["pinned_system_turn1_with_tools"]["prompt_eval_count"],
        "default_ctx_row": rows["system_turn1_with_tools_default_ctx"],
        "lab_only_truncate_false": {k: rows["truncate_false_over_window"].get(k) for k in ("status", "error")},
        "lab_only_context_array": {k: rows["context_array_recall"].get(k) for k in
                                   ("status", "deprecated_warn", "returned_context", "context_len", "reply")}
        | {"recall": rows["context_array_recall"]["recall"]["score"]},
        "windows_rule": "windows where system + tools + turn 1 fit with room for several turns: 8192, 16384, 32768 "
                        "(the plan's e.g.); 4096 default reported apart"}
    srows = st["rows"]
    res["stateless"] = {"turn2_alone_knows_plate_t0": srows[0]["knows_plate"],
                        "turn2_alone_knows_plate_google": sum(r["knows_plate"] for r in srows[1:]),
                        "google_reps": len(srows) - 1,
                        "turn2_alone_tool_calls": sum(bool(r["tool_calls"]) for r in srows), "t0_reply": (srows[0]["content"] or "")[:300],
                        "t0_tool_calls": srows[0]["tool_calls"]}
    hist = []
    for cid in ["drop-16k-t0"] + [f"base-16k-g{s}" for s in range(1, 6)]:
        if chat(cid):
            r2 = [r for r in reqs(cid) if r["turn"] == 2]
            hist.append({"id": cid, "acted_on_plate": any(r["tool_calls"] for r in r2),
                         "reply": r2[-1]["content"][:200]})
    res["stateless"]["turn2_with_history"] = hist
    res["drop"] = {w: brief(f"drop-{w}-t0") for w in ("8k", "16k", "32k", "default")}
    res["drop"]["8k_reps"] = [brief(f"base-8k-g{s}") for s in range(1, 6) if chat(f"base-8k-g{s}")]
    res["drop"]["16k_reps"] = [brief(f"base-16k-g{s}") for s in range(1, 6) if chat(f"base-16k-g{s}")]
    for w in ("8k", "16k"):
        g_ = [b["turn1_gone_turn"] for b in res["drop"][w + "_reps"]]
        res["drop"][w + "_turn1_gone_range"] = g_
    res["reuse"] = {cid: reuse(cid) for cid in ("drop-8k-t0", "drop-16k-t0", "drop-32k-t0", "reuse-16k-think",
                                                "reuse-16k-cold") if chat(cid)}
    res["fix"] = {"baseline_8k": arm("base-8k", "drop-8k-t0"), "a_pin_8k": arm("fix-pin-8k", "fix-pin-8k-t0"),
                  "b_ctx_32k": arm("fix-ctx32k", "drop-32k-t0"), "c_summary_8k": arm("fix-sum-8k", "fix-sum-8k-t0"),
                  "baseline_16k": arm("base-16k", "drop-16k-t0"), "a_pin_16k": arm("fix-pin-16k", "fix-pin-16k-t0"),
                  "c_summary_16k": arm("fix-sum-16k", "fix-sum-16k-t0")}
    fx = {k: v for k, v in res["fix"].items() if not k.startswith("baseline")}
    elig = [k for k, v in fx.items() if v["t0"] and v["t0"]["right"] and v["reps_right"] >= 4]
    if elig:
        win, flag = min(elig, key=lambda k: fx[k]["mean_tokens_per_turn_all"]), None
    else:
        win = max(fx, key=lambda k: (fx[k]["right_total"], -fx[k]["mean_tokens_per_turn_all"]))
        flag = "no arm met the rule; named by right chats"
    res["winner"] = {"arm": win, "eligible": elig, "flag": flag, "right": f'{fx[win]["right_total"]} of {fx[win]["chats"]}',
                     "mean_tokens_per_turn": fx[win]["mean_tokens_per_turn_all"],
                     "best_recall_arm": max(fx, key=lambda k: (fx[k]["recall8_chats"], -fx[k]["mean_tokens_per_turn_all"])),
}
    b = res["winner"]["best_recall_arm"]
    res["winner"]["best_recall_8of8"] = "%d of %d" % (fx[b]["recall8_chats"], fx[b]["chats"])
    json.dump(res, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    open(os.path.join(OUT, "RESULTS-g17.md"), "w", encoding="utf-8").write(md(res))
    print(json.dumps({"winner": res["winner"], "menu_tokens": res["size"]["menu_tokens"],
                      "turn1_gone": {w: (res["drop"][w] or {}).get("turn1_gone_turn") for w in ("8k", "16k", "32k", "default")}}))


if __name__ == "__main__":
    main()
