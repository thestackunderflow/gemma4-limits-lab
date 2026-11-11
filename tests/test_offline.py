"""Offline tests (no GPU, no server): graders, needle generator, row guard, /api/ps parser, task sets.
Written before the code they test (red phase log: out/red-phase.log)."""
import json

import pytest

from lab import graders, needle, rows, ollama, tasks


# ---------- graders ----------
def test_exact_match_normalises_whitespace_only():
    assert graders.exact_match("Error:  port 8080\n in use ", "Error: port 8080 in use")
    assert not graders.exact_match("Error: port 8081 in use", "Error: port 8080 in use")
    assert not graders.exact_match("error: port 8080 in use", "Error: port 8080 in use")  # case counts


def test_last_int_reads_commas_markdown_and_negatives():
    assert graders.last_int("The answer is **12,345,678**.") == 12345678
    assert graders.last_int("first 3 then -42") == -42
    assert graders.last_int("no number") is None
    assert graders.last_int("1 234 567") == 1234567  # thin-space style groups
    assert graders.last_int("= 37,421,698\n") == 37421698


def test_values_in_json_counts_matching_keys():
    got = '{"a": 10, "b": "20", "c": 31}'
    assert graders.values_in_json(got, {"a": 10, "b": 20, "c": 30}) == (2, 3)
    assert graders.values_in_json(got, {"a": 10, "b": 20, "c": 30}, tol=1) == (3, 3)
    assert graders.values_in_json("not json", {"a": 1}) == (0, 1)


def test_extract_code_and_unit_tests():
    text = "Here:\n```python\ndef add(a, b):\n    return a + b\n```\nDone."
    code = graders.extract_code(text)
    assert code.strip().startswith("def add")
    ok, total, _ = graders.run_unit_tests(code, ["assert add(2, 3) == 5", "assert add(-1, 1) == 0"])
    assert (ok, total) == (2, 2)
    ok, total, _ = graders.run_unit_tests("def add(a, b):\n    return a - b\n", ["assert add(2, 3) == 5"])
    assert (ok, total) == (0, 1)
    ok, total, err = graders.run_unit_tests("while True: pass\n", ["assert True"], timeout=2)
    assert ok == 0 and "timeout" in err


def test_wer():
    assert graders.wer("the cat sat", "the cat sat") == 0.0
    assert graders.wer("the cat sat", "the cat") == pytest.approx(1 / 3)
    assert graders.wer("This is a LibriVox recording.", "this is a librivox recording") == 0.0  # case + punctuation


def test_dois_and_title_match():
    text = "1. Vaswani et al. doi: 10.48550/arXiv.1706.03762. 2) https://doi.org/10.1145/3292500.3330701."
    assert graders.extract_dois(text) == ["10.48550/arxiv.1706.03762", "10.1145/3292500.3330701"]
    assert graders.title_match("Attention Is All You Need", "Attention is all you need.")
    assert not graders.title_match("Attention Is All You Need", "Deep Residual Learning for Image Recognition")


# ---------- needle generator ----------
def test_needle_is_deterministic_and_placed_at_depth():
    filler = ["Paragraph %d. " % i + "word " * 50 for i in range(400)]
    a = needle.build(filler, target_words=10000, facts=needle.facts(1, seed=42), depths=[0.5])
    b = needle.build(filler, target_words=10000, facts=needle.facts(1, seed=42), depths=[0.5])
    assert a["text"] == b["text"]
    f = a["facts"][0]
    pos = a["text"].index(f["sentence"]) / len(a["text"])
    assert 0.45 < pos < 0.55
    assert f["answer"] in f["sentence"]


def test_needle_eight_facts_all_present_and_scored():
    filler = ["Para %d. " % i + "text " * 40 for i in range(400)]
    facts = needle.facts(8, seed=42)
    assert len({f["answer"] for f in facts}) == 8
    h = needle.build(filler, target_words=8000, facts=facts, depths=[i / 8 + 1 / 16 for i in range(8)])
    for f in facts:
        assert f["sentence"] in h["text"]
    reply = " ".join(f["answer"] for f in facts[:5])
    assert needle.score(reply, facts) == 5


# ---------- row guard ----------
def test_row_guard_requires_provenance_fields():
    good = {"tag": "gemma4:e4b-it-q4_K_M", "digest": "dc35e8d9c606", "num_ctx": 4096, "kv_type": "f16",
            "mtp_draft": True, "temperature": 0, "ollama_version": "0.40.16", "fresh_load": True}
    rows.check(good)
    for k in rows.REQUIRED:
        bad = dict(good)
        bad.pop(k)
        with pytest.raises(ValueError):
            rows.check(bad)
    bad = dict(good, kv_type=None)
    with pytest.raises(ValueError):
        rows.check(bad)


# ---------- /api/ps parser ----------
def test_ps_parser_and_processor_split_like_ollama_ps():
    ps = {"models": [{"name": "gemma4:26b", "digest": "abc", "size": 20000, "size_vram": 7000,
                      "context_length": 4096, "expires_at": "x"}]}
    m = ollama.parse_ps(ps)[0]
    assert m["context_length"] == 4096
    assert m["processor"] == "65%/35% CPU/GPU"
    assert ollama.processor(100, 100) == "100% GPU"
    assert ollama.processor(100, 0) == "100% CPU"


# ---------- task sets ----------
def test_task_sets_have_the_planned_sizes_and_answers():
    assert len(tasks.multiplications()) == 20
    for t in tasks.multiplications():
        assert 1000 <= t["a"] <= 9999 and t["answer"] == t["a"] * t["b"]
    assert len(tasks.letter_counts()) == 20
    for t in tasks.letter_counts():
        assert t["answer"] == t["word"].lower().count(t["letter"])
    assert len(tasks.date_questions("2026-11-10")) == 10
    assert len(tasks.coding()) == 10
    assert len(tasks.multilingual()) == 10
    assert len(tasks.puzzles()) == 10
    assert len(tasks.json_extractions()) == 10
    assert len(tasks.tool_prompts()) == 10


def test_date_questions_answers_from_today():
    qs = {q["id"]: q for q in tasks.date_questions("2026-11-10")}
    assert qs["today_weekday"]["answer"] == "tuesday"
    assert qs["plus10_weekday"]["answer"] == "friday"


def test_coding_reference_solutions_pass_their_tests():
    for t in tasks.coding():
        ok, total, err = graders.run_unit_tests(t["reference"], t["tests"])
        assert ok == total, (t["name"], err)


def test_json_extractions_schema_matches_answer():
    import jsonschema
    for t in tasks.json_extractions():
        jsonschema.validate(t["answer"], t["schema"])
