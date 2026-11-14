"""g17 (chat memory in a SolidCraft design chat): pure parts, tests first.

Fixture tests/fixtures/g17-cuts.log: line 1 = a real P13 WARN (runner token cut), line 2 = a real 0.40.16 DEBUG line
from the 14 Nov probe (rendered path, prompt.go:77, truncated = messages KEPT), line 3 = the native-path line written
from the v0.40.16 source format (routes.go:3606, truncated = index of the first kept message), line 4 = a llama-server
slot line that must NOT count as a cut.
"""
import os

from lab import g17chat as g, logparse

FIX = open(os.path.join(os.path.dirname(__file__), "fixtures", "g17-cuts.log"), encoding="utf-8").read()


def test_three_cut_signals_with_their_meaning():
    c = logparse.cuts(FIX)
    assert c == [{"kind": "runner_token_cut", "limit": 2051, "prompt": 9644, "keep": 5, "new": 2051},
                 {"kind": "messages_dropped", "kept": 8},
                 {"kind": "native_messages_dropped", "first_kept_index": 3}]


def test_no_cut_lines():
    assert logparse.cuts("slot release truncated = 0\n") == []


def test_turn_script_shape():
    assert len(g.TURNS) == 20
    assert "BRK-17" in g.TURNS[0] and "60 x 40 x 5" in g.TURNS[0]
    assert "first message" in g.TURNS[19]
    # no later turn repeats an original value (the spec lives only in turn 1)
    for t in g.TURNS[1:]:
        assert "BRK-17" not in t and "PETG" not in t and "36 mm" not in t and "4.5" not in t


def test_recall_all_eight():
    text = ("Part BRK-17 in PETG: 60 x 40 x 5 mm, two holes of 4.5 mm, 36 mm apart.")
    r = g.recall(text)
    assert r["score"] == 8 and r["missing"] == []


def test_recall_latest_variant_scores_low_and_flags_stale():
    text = "Part BRK-19 in ABS: 65 x 42 x 4 mm, two holes of 5.5 mm, 50 mm apart."
    r = g.recall(text)
    assert r["score"] == 1          # only "two holes"
    assert set(r["stale"]) >= {"BRK-19", "ABS", "65", "42"}


def test_recall_number_boundaries():
    assert g.recall("4.5 mm holes")["facts"]["thickness"] is False   # the 5 of 4.5 is not a thickness
    assert g.recall("5.5 mm")["facts"]["hole_d"] is False
    assert g.recall("2 holes")["facts"]["holes"] is True
    assert g.recall("holes: 2")["facts"]["holes"] is True


def test_turn_one_present():
    msgs = [{"role": "system", "content": "s"}, {"role": "user", "content": g.TURNS[0]}, {"role": "user", "content": "x"}]
    # the rendered path keeps the last `kept` messages (+ system messages from the dropped part)
    assert g.turn1_kept(msgs, {"kind": "messages_dropped", "kept": 2}) is True
    assert g.turn1_kept(msgs, {"kind": "messages_dropped", "kept": 1}) is False
    assert g.turn1_kept(msgs, {"kind": "native_messages_dropped", "first_kept_index": 1}) is True
    assert g.turn1_kept(msgs, {"kind": "native_messages_dropped", "first_kept_index": 2}) is False
    assert g.turn1_kept(msgs, None) is True


def test_summary_window_keeps_system_summary_last_four_turns():
    sysm = {"role": "system", "content": "S"}
    turns = [[{"role": "user", "content": f"u{i}"}, {"role": "assistant", "content": f"a{i}"}] for i in range(7)]
    w = g.window_summary(sysm, "SPEC", turns, keep=4)
    assert w[0] == sysm
    assert "SPEC" in w[1]["content"] and w[1]["role"] == "user" and w[2]["role"] == "assistant"
    assert [m["content"] for m in w[3:]] == ["u3", "a3", "u4", "a4", "u5", "a5", "u6", "a6"]
    assert g.window_summary(sysm, None, turns[:2], keep=4) == [sysm] + turns[0] + turns[1]


def test_marker():
    assert g.marker_ok("Done.\n-- plate desk") is True
    assert g.marker_ok("Done.") is False


def test_turn_tokens_and_first_drop():
    reqs = [{"turn": 1, "prompt_eval_count": 100, "cut": None, "turn1_kept": True},
            {"turn": 1, "prompt_eval_count": 150, "cut": None, "turn1_kept": True},
            {"turn": 2, "prompt_eval_count": 300, "cut": {"kind": "messages_dropped", "kept": 3}, "turn1_kept": True},
            {"turn": 3, "prompt_eval_count": 320, "cut": {"kind": "messages_dropped", "kept": 3}, "turn1_kept": False},
            {"turn": 4, "prompt_eval_count": 330, "cut": None, "turn1_kept": False}]
    assert g.tokens_per_turn(reqs) == {1: 250, 2: 300, 3: 320, 4: 330}
    assert g.first_turn(reqs, lambda r: r["cut"] is not None) == 2
    assert g.first_turn(reqs, lambda r: not r["turn1_kept"]) == 3


def test_tokens_per_turn_counts_summary_requests():
    reqs = [{"turn": 5, "prompt_eval_count": 100}, {"turn": 5, "prompt_eval_count": 40, "summary": True}]
    assert g.tokens_per_turn(reqs) == {5: 140}
