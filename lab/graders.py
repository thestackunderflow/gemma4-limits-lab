"""Graders: every pass/fail in the lab is decided here, by code."""
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile


def norm_text(s):
    return " ".join((s or "").split())


def exact_match(got, want):
    """Exact text after collapsing whitespace (case and punctuation count)."""
    g = norm_text(got)
    # a model often wraps a transcription in a code fence: strip one fence, nothing else
    m = re.fullmatch(r"```[a-zA-Z]*\s*(.*?)\s*```", g)
    if m:
        g = m.group(1)
    return g == norm_text(want)


_INT = re.compile(r"-?\d{1,3}(?:[,   ]\d{3})+(?!\d)|-?\d+")


def last_int(text):
    if not text:
        return None
    t = text.replace("*", "")
    found = _INT.findall(t)
    if not found:
        return None
    return int(re.sub(r"[,   ]", "", found[-1]))


def int_ok(text, want):
    return last_int(text) == want


def _loads(text):
    if isinstance(text, (dict, list)):
        return text
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text or "", re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                return None
    return None


def _num(v):
    try:
        return float(str(v).replace(",", "").strip())
    except Exception:
        return None


def values_in_json(got, want, tol=0):
    """(matching keys, total keys). Numbers compare within tol; strings compare case-insensitively."""
    obj = _loads(got)
    if not isinstance(obj, dict):
        return (0, len(want))
    ok = 0
    for k, w in want.items():
        if k not in obj:
            continue
        g = obj[k]
        if isinstance(w, (int, float)) and not isinstance(w, bool):
            n = _num(g)
            if n is not None and abs(n - w) <= tol:
                ok += 1
        elif isinstance(w, list):
            if isinstance(g, list) and [norm_text(str(x)).lower() for x in g] == [norm_text(str(x)).lower() for x in w]:
                ok += 1
        elif norm_text(str(g)).lower() == norm_text(str(w)).lower():
            ok += 1
    return (ok, len(want))


def extract_code(text):
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text or "", re.S)
    return max(m, key=len) if m else (text or "")


def run_unit_tests(code, tests, timeout=10):
    """Run each assert in its own subprocess (python -I) with a timeout. Returns (passed, total, last_error)."""
    ok, err = 0, ""
    with tempfile.TemporaryDirectory() as d:
        for i, t in enumerate(tests):
            p = os.path.join(d, f"t{i}.py")
            with open(p, "w", encoding="utf-8") as f:
                f.write(code + "\n\n" + t + "\n")
            try:
                r = subprocess.run([sys.executable, "-I", p], capture_output=True, text=True, timeout=timeout, cwd=d)
                if r.returncode == 0:
                    ok += 1
                else:
                    err = (r.stderr or "").strip().splitlines()[-1:] and r.stderr.strip().splitlines()[-1]
            except subprocess.TimeoutExpired:
                err = "timeout"
    return ok, len(tests), err


def _words(s):
    return re.findall(r"[a-z0-9']+", (s or "").lower())


def wer(ref, hyp):
    r, h = _words(ref), _words(hyp)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            cur = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
            prev = cur
    return d[len(h)] / max(1, len(r))


_DOI = re.compile(r"10\.\d{4,9}/[^\s\"<>,;]+", re.I)


def extract_dois(text):
    out = []
    for m in _DOI.findall(text or ""):
        d = m.rstrip(".)]").lower()
        if d not in out:
            out.append(d)
    return out


def title_match(a, b, threshold=0.85):
    na = " ".join(_words(a))
    nb = " ".join(_words(b))
    return difflib.SequenceMatcher(None, na, nb).ratio() >= threshold
