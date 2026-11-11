"""Host sampler files (scripts/lab.sh sampler): <run>.gpu.csv (epoch,gpu_mem_used_mib,gpu_util_pct, ~1 s) and
<run>.mem.csv (epoch,ollama_mem,windows_free_gb, ~4 s)."""
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


def _current():
    cur = os.path.join(DIR, "CURRENT")
    return open(cur).read().strip() if os.path.exists(cur) else None


def _rows(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    for line in open(path, encoding="utf-8", errors="replace"):
        p = line.strip().split(",")
        if len(p) >= 3 and p[0].isdigit():
            out.append(p)
    return out


def gpu(name=None):
    name = name or _current()
    out = []
    for p in _rows(name and os.path.join(DIR, name + ".gpu.csv")):
        try:
            out.append({"t": int(p[0]), "gpu_mib": float(p[1]), "util": float(p[2])})
        except ValueError:
            pass
    return out


def mem(name=None):
    name = name or _current()
    out = []
    for p in _rows(name and os.path.join(DIR, name + ".mem.csv")):
        try:
            out.append({"t": int(p[0]), "ram_mib": mem_mib(p[1]), "win_free_gb": float(p[2])})
        except ValueError:
            pass
    return out


def read():
    """Latest memory samples (Windows free RAM), used by the load guard."""
    return mem()


def window(t0, t1):
    g = [x for x in gpu() if t0 - 1 <= x["t"] <= t1 + 1]
    m = [x for x in mem() if t0 - 2 <= x["t"] <= t1 + 2]
    ram = [x["ram_mib"] for x in m if x["ram_mib"] is not None]
    return {"n_gpu": len(g), "gpu_mib_max": max((x["gpu_mib"] for x in g), default=None),
            "gpu_mib_before": None, "n_mem": len(m), "ram_mib_max": max(ram) if ram else None,
            "win_free_gb_min": min((x["win_free_gb"] for x in m), default=None)}
