"""Row guard: every result row carries its provenance, or it is not written."""
import json
import os

REQUIRED = ["tag", "digest", "num_ctx", "kv_type", "mtp_draft", "temperature", "ollama_version", "fresh_load"]


def check(row):
    for k in REQUIRED:
        if k not in row or row[k] is None:
            raise ValueError(f"row is missing {k}: {sorted(row)}")
    return row


class Writer:
    """Append rows (JSON lines) to out/<video>/rows.jsonl after the guard."""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def write(self, row):
        check(row)
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        return row


def read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(x) for x in f if x.strip()]
