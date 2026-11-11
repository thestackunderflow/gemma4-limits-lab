"""Parse the Ollama 0.40.16 server log (lines as in tests/fixtures/server-0.40.16-e4b.log)."""
import re


def _kv(line):
    return dict(re.findall(r'(\w+)=("[^"]*"|\S+)', line))


def default_context(log):
    for line in log.splitlines():
        if 'msg="vram-based default context"' in line:
            d = _kv(line)
            return {"total_vram": d["total_vram"].strip('"'), "default_num_ctx": int(d["default_num_ctx"])}
    return None


def truncations(log):
    out = []
    for line in log.splitlines():
        if 'msg="truncating input prompt"' in line:
            d = _kv(line)
            out.append({k: int(d[k]) for k in ("limit", "prompt", "keep", "new") if k in d})
    return out


def kv_type(log):
    m = re.search(r"llama_kv_cache: size = .*?K \((\w+)\)", log)
    return m.group(1) if m else None


def ctx_arg(log):
    m = None
    for m in re.finditer(r'starting llama-server.* -c (\d+)', log):
        pass
    return int(m.group(1)) if m else None


def offload(log):
    """The main model's line (the first one; the MTP draft model loads after it and prints its own)."""
    m = re.search(r"offloaded (\d+)/(\d+) layers to GPU", log)
    return (int(m.group(1)), int(m.group(2))) if m else None


def draft_loaded(log):
    return "loading draft model" in log


def mmap_disabled(log):
    return "disabling mmap" in log


def gpu_available_gib(log):
    m = re.search(r'msg="gpu memory".*?available="([\d.]+) GiB"', log)
    return float(m.group(1)) if m else None


def errors(log):
    return [l for l in log.splitlines() if "level=ERROR" in l or "out of memory" in l.lower()][:5]


def offload_all(log):
    return [(int(a), int(b)) for a, b in re.findall(r"offloaded (\d+)/(\d+) layers to GPU", log)]
