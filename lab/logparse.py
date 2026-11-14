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


def cuts(log):
    """g17: the three cut signals of 0.40.16, each with its real meaning (PLAN rev 2 §4, ACCURACY C6/C8).
    messages_dropped: prompt.go:77, `truncated` = number of messages KEPT (system messages from the dropped part are
    added back). native_messages_dropped: routes.go native path, `truncated` = index of the first kept message.
    runner_token_cut: llama_server.go WARN (P13's cut of tokens from the middle of one rendered prompt)."""
    out = []
    for line in log.splitlines():
        if 'msg="truncating input messages which exceed context length"' in line:
            out.append({"kind": "messages_dropped", "kept": int(_kv(line)["truncated"])})
        elif 'msg="truncating native chat messages' in line:
            out.append({"kind": "native_messages_dropped", "first_kept_index": int(_kv(line)["truncated"])})
        elif 'msg="truncating input prompt"' in line:
            d = _kv(line)
            out.append({"kind": "runner_token_cut", **{k: int(d[k]) for k in ("limit", "prompt", "keep", "new") if k in d}})
    return out
