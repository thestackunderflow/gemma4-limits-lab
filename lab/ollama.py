"""Thin Ollama HTTP client + /api/ps parser + server-log window (the log is teed to out/logs/server.log)."""
import os
import time

import requests

URL = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11437")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "out", "logs", "server.log")
TIMEOUT = 7200


def processor(size, size_vram):
    """The PROCESSOR column exactly as `ollama ps` computes it."""
    if size_vram == 0:
        return "100% CPU"
    if size_vram == size:
        return "100% GPU"
    cpu = round((size - size_vram) / size * 100)
    return f"{int(cpu)}%/{int(100 - cpu)}% CPU/GPU"


def parse_ps(js):
    out = []
    for m in js.get("models", []):
        out.append({"name": m.get("name"), "digest": (m.get("digest") or "")[:12],
                    "context_length": m.get("context_length"), "size": m.get("size"),
                    "size_vram": m.get("size_vram"),
                    "processor": processor(m.get("size", 0), m.get("size_vram", 0))})
    return out


def version():
    return requests.get(f"{URL}/api/version", timeout=30).json()["version"]


def show(tag):
    return requests.post(f"{URL}/api/show", json={"model": tag}, timeout=60).json()


def tags():
    return requests.get(f"{URL}/api/tags", timeout=60).json().get("models", [])


def digest(tag):
    for m in tags():
        if m["name"] == tag or m.get("model") == tag:
            return m["digest"][:12]
    return None


def ps():
    return parse_ps(requests.get(f"{URL}/api/ps", timeout=60).json())


def unload_all():
    for m in ps():
        requests.post(f"{URL}/api/generate", json={"model": m["name"], "keep_alive": 0}, timeout=300)
    for _ in range(120):
        if not ps():
            return True
        time.sleep(0.5)
    return False


def post(path, body, timeout=TIMEOUT):
    """POST and return (status, json-or-text, seconds)."""
    t0 = time.time()
    r = requests.post(f"{URL}{path}", json=body, timeout=timeout)
    dt = time.time() - t0
    try:
        js = r.json()
    except Exception:
        js = {"_text": r.text[:2000]}
    return r.status_code, js, dt


def chat(tag, messages, options=None, keep_alive=0, **extra):
    body = {"model": tag, "messages": messages, "stream": False, "keep_alive": keep_alive,
            "options": options or {}}
    body.update(extra)
    return post("/api/chat", body)


def generate(tag, prompt, options=None, keep_alive=0, **extra):
    body = {"model": tag, "prompt": prompt, "stream": False, "keep_alive": keep_alive, "options": options or {}}
    body.update(extra)
    return post("/api/generate", body)


def openai_chat(tag, messages, **extra):
    body = {"model": tag, "messages": messages, "stream": False}
    body.update(extra)
    return post("/v1/chat/completions", body)


def log_mark():
    return os.path.getsize(LOG) if os.path.exists(LOG) else 0


def log_since(mark, settle=1.0):
    time.sleep(settle)
    if not os.path.exists(LOG):
        return ""
    with open(LOG, "rb") as f:
        f.seek(mark)
        return f.read().decode("utf-8", "replace")
