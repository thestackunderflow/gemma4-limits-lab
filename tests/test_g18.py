"""g18 (one setting changed at a time on the 5 `llm` SolidCraft jobs): pure parts, tests first (PLAN rev 2 §5.2)."""
from lab import g18jobs as j


def test_arms_change_one_thing_from_the_baseline():
    base = j.ARMS["baseline"]
    assert base == {"tag": "gemma4:e4b-it-q4_K_M", "num_ctx": j.SMALL_CTX, "think": False, "system": None}
    for name, arm in j.ARMS.items():
        diff = [k for k in base if arm[k] != base[k]]
        assert len(diff) == (0 if name == "baseline" else 1), (name, diff)
    assert j.ARMS["ctx_32k"]["num_ctx"] == 32768
    assert {j.ARMS[a]["tag"] for a in ("e2b", "q12_qat", "q12_q4km")} == {
        "gemma4:e2b-it-q4_K_M", "gemma4:12b-it-qat", "gemma4:12b-it-q4_K_M"}
    assert len(j.SYSTEM3.strip().splitlines()) == 3


def test_small_window_holds_menu_plus_4k():
    # 4,469-token menu (g17 G17-SIZE) + 4,096 -> rounded up to a multiple of 4,096
    assert j.smallest_ctx(4469) == 12288
    assert j.smallest_ctx(4000) == 8192
    assert j.SMALL_CTX == 12288


def test_battery_lines_and_ids_are_unique():
    lines = j.battery(["baseline", "think_on"], "t0", reps=2)
    assert len(lines) == 2 * 5 * 2
    ids = [l.split()[0] for l in lines]
    assert len(set(ids)) == len(ids)
    assert lines[0].split() == ["baseline-new-t0-r1", "baseline", "new", "t0", "42"]
    g = j.battery(["baseline"], "google", reps=5)
    assert {l.split()[4] for l in g} == {"1", "2", "3", "4", "5"}
    assert all(l.split()[3] == "google" for l in g)


def _req(done="stop", cuts=(), status=200, calls=1, ev=100, evd=2e9, pec=5000, load=0):
    return {"status": status, "done_reason": done, "cuts": list(cuts), "tool_calls": [{"name": "x"}] * calls,
            "eval_count": ev, "eval_duration": evd, "prompt_eval_count": pec, "load_duration": load}


def test_outcome_scoring():
    assert j.outcome({"pass": True}, [_req()]) == "right"
    assert j.outcome({"pass": False}, [_req()]) == "wrong"
    # any cut line or a length stop = ran out of room, even if the part passes (accuracy S)
    assert j.outcome({"pass": True}, [_req(cuts=[{"kind": "messages_dropped", "kept": 2}])]) == "ran out of room"
    assert j.outcome({"pass": True}, [_req(done="length")]) == "ran out of room"
    assert j.outcome({"pass": True}, [_req(status=500)]) == "error"
    assert j.outcome(None, []) == "error"


def test_write_speed_and_job_seconds():
    reqs = [_req(ev=100, evd=2e9), _req(ev=50, evd=1e9)]
    assert j.write_tps(reqs) == 50.0
    assert j.write_tps([]) is None
    # job seconds exclude the model load (reported apart)
    assert j.job_seconds(30.0, [_req(load=4e9), _req(load=0)]) == 26.0


def _row(arm, job, samp, seed, result, secs, calls=("execute",)):
    return {"arm": arm, "job": job, "sampling": samp, "seed": seed, "outcome": result, "job_seconds": secs,
            "call_names": list(calls), "rep": 1}


def test_arm_summary_counts_right_per_minute():
    rows = [_row("baseline", jb, "t0", 42, "right" if jb != "hole" else "wrong", 30.0) for jb in j.JOBS]
    s = j.summarize(rows)["baseline"]["t0"]
    assert s["right"] == 4 and s["n"] == 5 and s["label"] == "4 of 5 jobs"
    assert s["minutes"] == 2.5 and s["right_per_minute"] == 1.6
    g = [_row("baseline", jb, "google", sd, "right", 60.0) for jb in j.JOBS for sd in range(1, 6)]
    sg = j.summarize(g)["baseline"]["google"]
    assert sg["label"] == "25 of 25" and sg["per_rep"] == [5, 5, 5, 5, 5]


def test_reps_identical_flag():
    a = [_row("baseline", "cube", "t0", 42, "right", 30.0, ("execute",))]
    b = [dict(a[0], rep=2)]
    assert j.summarize(a + b)["baseline"]["t0"]["reps_identical"] is True
    c = [dict(a[0], rep=2, call_names=["batch"])]
    assert j.summarize(a + c)["baseline"]["t0"]["reps_identical"] is False
    # score counts rep 1 only
    assert j.summarize(a + b)["baseline"]["t0"]["n"] == 1


def test_winner_and_null_rule():
    def arm_rows(arm, k, secs):
        return [_row(arm, jb, "t0", 42, "right" if i < k else "wrong", secs) for i, jb in enumerate(j.JOBS)]
    rows = arm_rows("baseline", 2, 60) + arm_rows("think_on", 4, 60) + arm_rows("e2b", 3, 30)
    w = j.winner(j.summarize(rows))
    assert w["arm"] == "e2b" and w["null"] is False           # 3 right in 2.5 min beats 4 in 5 min
    flat = arm_rows("baseline", 3, 60) + arm_rows("think_on", 4, 60) + arm_rows("e2b", 3, 30)
    assert j.winner(j.summarize(flat))["null"] is True         # every arm within 1 job of every other


def test_tool_json_ignores_the_headless_note():
    t = '{\n  "name": "Untitled"\n}\nNote: this is a headless session because the SolidCraft app was not found.'
    assert j.tool_json(t) == {"name": "Untitled"}
    assert j.tool_json("not json") == {"_text": "not json"}


def test_12b_arms_stay_loaded_between_jobs():
    # 14 Nov: a fresh 12B load per job took Windows to 1.2 GB free RAM and C: to 4 GB (pagefile); one load per arm
    assert j.keep_warm("q12_qat") and j.keep_warm("q12_q4km")
    assert not any(j.keep_warm(a) for a in ("baseline", "e2b", "think_on", "system3", "ctx_32k"))


def test_rep2_without_rep1_is_not_compared():
    b = [dict(_row("baseline", "cube", "t0", 42, "right", 30.0), rep=2)]
    assert j.summarize(b)["baseline"]["t0"]["reps_identical"] is None


def test_winner_ignores_incomplete_arms():
    rows = [_row("baseline", jb, "t0", 42, "right", 30) for jb in j.JOBS] + [_row("ctx_32k", "new", "t0", 42, "right", 2)]
    w = j.winner(j.summarize(rows))
    assert w["arm"] is None and w["incomplete"] == ["ctx_32k"]
