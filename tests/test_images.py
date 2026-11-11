"""Lab-made images: known text and values, deterministic."""
import os

from PIL import Image

from lab import images


def test_ocr_cards(tmp_path):
    items = images.ocr_cards(str(tmp_path))
    assert len(items) == 10
    for it in items:
        assert os.path.exists(it["path"]) and it["text"].strip()
        assert Image.open(it["path"]).size[0] >= 800


def test_charts_and_pairs(tmp_path):
    ch = images.charts(str(tmp_path))
    assert len(ch) == 5 and all(len(c["values"]) == 4 for c in ch)
    assert all(v % 5 == 0 for c in ch for v in c["values"].values())
    pr = images.pairs(str(tmp_path))
    assert len(pr) == 5
    for p in pr:
        assert len(p["paths"]) == 2 and p["answer"].count("-") == 1


def test_deterministic(tmp_path):
    a = images.charts(str(tmp_path / "a"))
    b = images.charts(str(tmp_path / "b"))
    assert [x["values"] for x in a] == [x["values"] for x in b]
