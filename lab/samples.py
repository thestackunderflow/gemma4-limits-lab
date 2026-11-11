"""Host sampler file (scripts/lab.sh sampler): epoch,gpu_mem_used_mib,gpu_util_pct,ollama_mem,windows_free_gb."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, "out", "samples")


def mem_mib(s):
    m = re.match(r"([\d.]+)\s*([KMG]i?B|B)", s or "")
    if not m:
        return None
    v, u = float(m.group(1)), m.group(2)
    return round(v * {"B": 1 / 2 ** 20, "KiB": 1 / 1024, "KB": 1 / 1024, "MiB": 1, "MB": 1, "GiB": 1024,
                      "GB": 1024}[u], 1)


def read(path=None):
    if path is None:
        cur = os.path.join(DIR, "CURRENT")
        if not os.path.exists(cur):
            return []
        path = os.path.join(DIR, open(cur).read().strip() + ".csv")
    if not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        p = line.strip().split(",")
        if len(p) < 5 or not p[0].isdigit():
            continue
        try:
            out.append({"t": int(p[0]), "gpu_mib": float(p[1]), "util": float(p[2]), "ram_mib": mem_mib(p[3]),
                        "win_free_gb": float(p[4])})
        except ValueError:
            continue
    return out


def window(t0, t1, samples=None):
    s = [x for x in (samples if samples is not None else read()) if t0 - 1 <= x["t"] <= t1 + 1]
    if not s:
        return {"n_samples": 0}
    ram = [x["ram_mib"] for x in s if x["ram_mib"] is not None]
    return {"n_samples": len(s), "gpu_mib_max": max(x["gpu_mib"] for x in s),
            "ram_mib_max": max(ram) if ram else None, "win_free_gb_min": min(x["win_free_gb"] for x in s)}
