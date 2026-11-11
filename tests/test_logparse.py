"""Server-log parser, tested on real Ollama 0.40.16 lines (tests/fixtures/server-0.40.16-e4b.log)."""
import os

from lab import logparse

FIX = open(os.path.join(os.path.dirname(__file__), "fixtures", "server-0.40.16-e4b.log"), encoding="utf-8").read()


def test_default_context_line():
    d = logparse.default_context(FIX)
    assert d == {"total_vram": "8.0 GiB", "default_num_ctx": 4096}


def test_truncation_warn():
    t = logparse.truncations(FIX)
    assert t == [{"limit": 2051, "prompt": 9644, "keep": 5, "new": 2051}]


def test_kv_type_ctx_offload_draft_mmap():
    assert logparse.kv_type(FIX) == "f16"
    assert logparse.ctx_arg(FIX) == 4096
    assert logparse.offload(FIX) == (43, 43)
    assert logparse.draft_loaded(FIX) is True
    assert logparse.mmap_disabled(FIX) is True
    assert logparse.gpu_available_gib(FIX) == 6.5


def test_empty_log():
    assert logparse.default_context("") is None
    assert logparse.truncations("") == []
    assert logparse.kv_type("") is None
    assert logparse.offload("") is None
