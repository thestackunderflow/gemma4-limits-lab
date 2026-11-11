"""Part 14 (P-CANT): five measured failures and the fix for each.
python -m lab.p14 run --models e4b,12b-qat --t1reps 5 [--sections mul,letters,dates,cutoff,cite]
python -m lab.p14 sources      (fetch the release pages the cutoff answers come from, same day)
python -m lab.p14 tokens --url http://gemma4-limits-tok:8080   (real tokenizer dump via llama-server /tokenize)"""
import json
import os
import re
import sys
import time

import requests

from lab import common as c, graders as g, tasks
from lab.p15 import Session, content, tool_loop

OUT = os.path.join(c.ROOT, "out", "p14")
TODAY = "2026-11-10"
REPOS = {"ollama": ("ollama/ollama", "Ollama"), "node": ("nodejs/node", "Node.js"),
         "kubernetes": ("kubernetes/kubernetes", "Kubernetes"), "rust": ("rust-lang/rust", "Rust"),
         "vscode": ("microsoft/vscode", "Visual Studio Code")}
GEMMA_SOURCE = ("Gemma 4 model card (Google), https://ai.google.dev/gemma/docs/core/model_card_4, fetched 10 Nov 2026: "
                "\"Gemma 4 models are multimodal, handling text and image input (with audio supported on E2B, E4B, "
                "and 12B models) and generating text output.\" \"The small models feature a 128K context window, "
                "while the medium models support 256K.\"")


def sources():
    os.makedirs(os.path.join(OUT, "sources"), exist_ok=True)
    out = {}
    for k, (repo, name) in REPOS.items():
        r = requests.get(f"https://api.github.com/repos/{repo}/releases/latest", timeout=60,
                         headers={"Accept": "application/vnd.github+json"})
        js = r.json()
        rec = {"name": name, "repo": repo, "status": r.status_code, "tag": js.get("tag_name"),
               "release_name": js.get("name"), "published_at": js.get("published_at"), "url": js.get("html_url"),
               "body": (js.get("body") or "")[:1500], "fetched": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        out[k] = rec
        c.say("SRC", k, rec["status"], rec["tag"], rec["published_at"])
    out["gemma"] = {"name": "Gemma", "tag": "Gemma 4", "body": GEMMA_SOURCE, "url":
                    "https://ai.google.dev/gemma/docs/core/model_card_4", "fetched": "2026-11-11T03:27Z (plan ACCURACY S1)"}
    c.dump(os.path.join(OUT, "sources", "releases.json"), out)


def _version(tag):
    m = re.search(r"\d+\.\d+(?:\.\d+)?", tag or "")
    return m.group(0) if m else tag


def cutoff_items():
    src = json.load(open(os.path.join(OUT, "sources", "releases.json"), encoding="utf-8"))
    items = []
    for k, rec in src.items():
        if k == "gemma":
            q = ("What is the newest generation of Google's open-weight Gemma models? Answer with the name "
                 "(for example 'Gemma 2') only.")
            want = "gemma 4"
            paste = rec["body"]
        else:
            q = f"What is the latest stable release version of {rec['name']}? Answer with the version number only."
            want = _version(rec["tag"])
            paste = (f"Release page {rec['url']} (fetched {rec['fetched']}): {rec['release_name']} "
                     f"(tag {rec['tag']}), published {rec['published_at']}.\n{rec['body'][:800]}")
        items.append({"id": f"cut_{k}", "prompt": q, "answer": want, "paste": paste})
    return items


def _ok(text, want):
    t = (text or "").lower().replace("*", "")
    if isinstance(want, int):
        return g.last_int(t) == want
    return str(want).lower() in t


def sec_mul(s, think):
    n = 0
    for it in tasks.multiplications():
        st, js, dt, log, f = s.chat([{"role": "user", "content": it["prompt"]}], think=think,
                                    num_predict=8192 if think else 256)
        ok = g.int_ok(content(js), it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, think=think, answer=content(js)[-300:], want=it["answer"], passed=ok,
              eval_count=js.get("eval_count"), seconds=round(dt, 1))
    return n


def sec_mul_tool(s):
    n = 0
    tool = [t for t in tasks.TOOLS if t["function"]["name"] == "multiply"]
    for it in tasks.multiplications():
        calls, final, dt, log, f, st = tool_loop(s, it["prompt"], tools=tool)
        ok = g.int_ok(final, it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, fix="calculator tool", calls=calls, answer=final[-300:],
              want=it["answer"], passed=ok, used_tool=bool(calls), seconds=round(dt, 1))
    return n


def sec_letters(s, fix):
    n = 0
    for it in tasks.letter_counts():
        st, js, dt, log, f = s.chat([{"role": "user", "content": it["fix_prompt"] if fix else it["prompt"]}],
                                    num_predict=1024)
        ok = g.int_ok(content(js), it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, fix="spell first" if fix else None, answer=content(js)[-300:],
              want=it["answer"], passed=ok, seconds=round(dt, 1))
    return n


def sec_dates(s, fix):
    n = 0
    sysmsg = [{"role": "system", "content": tasks.date_system_prompt(TODAY)}] if fix else []
    for it in tasks.date_questions(TODAY):
        st, js, dt, log, f = s.chat(sysmsg + [{"role": "user", "content": it["prompt"]}], num_predict=256)
        ok = _ok(content(js), it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, fix="date in system prompt" if fix else None, answer=content(js)[-300:],
              want=it["answer"], passed=ok, seconds=round(dt, 1))
    return n


def sec_cutoff(s, fix):
    n = 0
    for it in cutoff_items():
        p = (f"Use the source below to answer.\n\nSource:\n{it['paste']}\n\nQuestion: {it['prompt']}" if fix
             else it["prompt"])
        st, js, dt, log, f = s.chat([{"role": "user", "content": p}], num_predict=256)
        ok = _ok(content(js), it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, fix="paste the source" if fix else None, answer=content(js)[-400:],
              want=it["answer"], passed=ok, seconds=round(dt, 1))
    return n


CITE_PROMPT = ("List 10 real, peer-reviewed papers about attention mechanisms and efficient inference for "
               "transformer language models, published before 2024. One per line, in the form: "
               "Title | DOI. No other text.")


def resolve_doi(doi):
    try:
        r = requests.get(f"https://doi.org/{doi}", headers={"Accept": "application/vnd.citationstyles.csl+json"},
                         timeout=30, allow_redirects=True)
        if r.status_code == 200:
            try:
                t = r.json().get("title")
                return True, t if isinstance(t, str) else (t[0] if t else None), r.status_code
            except ValueError:
                return True, None, r.status_code
        h = requests.get(f"https://doi.org/api/handles/{doi}", timeout=30)
        return h.status_code == 200 and h.json().get("responseCode") == 1, None, r.status_code
    except Exception as e:
        return None, repr(e)[:100], 0


def sec_cite(s):
    st, js, dt, log, f = s.chat([{"role": "user", "content": CITE_PROMPT}], num_predict=2048)
    lines = [l for l in content(js).splitlines() if "|" in l]
    res = []
    for l in lines[:10]:
        title, _, rest = l.partition("|")
        dois = g.extract_dois(rest) or g.extract_dois(l)
        doi = dois[0] if dois else None
        real, real_title, code = resolve_doi(doi) if doi else (False, None, None)
        match = bool(real and real_title and g.title_match(re.sub(r"^\W*\d+[.)]\s*", "", title).strip(" *"),
                                                           real_title))
        res.append({"line": l.strip()[:300], "doi": doi, "doi_resolves": real, "doi_title": real_title,
                    "http": code, "title_matches": match})
    nreal = sum(1 for r in res if r["doi_resolves"])
    nmatch = sum(1 for r in res if r["title_matches"])
    s.row("citations", log, f, status=st, answer=content(js)[:3000], citations=res, n_listed=len(res),
          n_doi_resolves=nreal, n_title_matches=nmatch, seconds=round(dt, 1))
    return {"listed": len(res), "doi_resolves": nreal, "title_matches": nmatch}


def run(models, t1reps, sections):
    w = c.writer("p14", "cant")
    summ = os.path.join(OUT, "cant-summary.jsonl")

    def log_sum(**kw):
        with open(summ, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(kw) + "\n")
        c.say("CANT", kw)

    for key in models:
        settings = [(0.0, 42, 1)] + [(1.0, 1000 + r, r) for r in range(1, t1reps + 1)]
        for temp, seed, rep in settings:
            for sec in sections:
                s = Session(key, temp, seed, w, sec)
                if sec == "mul":
                    log_sum(model=key, section="mul", think=False, temp=temp, rep=rep, passed=sec_mul(s, False), total=20)
                    log_sum(model=key, section="mul", think=True, temp=temp, rep=rep, passed=sec_mul(s, True), total=20)
                    log_sum(model=key, section="mul", fix="calculator tool", temp=temp, rep=rep, passed=sec_mul_tool(s), total=20)
                elif sec == "letters":
                    log_sum(model=key, section="letters", temp=temp, rep=rep, passed=sec_letters(s, False), total=20)
                    log_sum(model=key, section="letters", fix="spell first", temp=temp, rep=rep, passed=sec_letters(s, True), total=20)
                elif sec == "dates":
                    log_sum(model=key, section="dates", temp=temp, rep=rep, passed=sec_dates(s, False), total=10)
                    log_sum(model=key, section="dates", fix="date in system prompt", temp=temp, rep=rep, passed=sec_dates(s, True), total=10)
                elif sec == "cutoff":
                    log_sum(model=key, section="cutoff", temp=temp, rep=rep, passed=sec_cutoff(s, False), total=6)
                    log_sum(model=key, section="cutoff", fix="paste the source", temp=temp, rep=rep, passed=sec_cutoff(s, True), total=6)
                elif sec == "cite":
                    log_sum(model=key, section="cite", temp=temp, rep=rep, **sec_cite(s))
            c.fresh()


TOKEN_WORDS = ["strawberry", "mississippi", "bookkeeper", "embarrassment", "hippopotamus", " strawberry",
               "Strawberry", "4821 × 7293", "35159553", "12,345,678", "2026-11-10"]


def tokens(url):
    out = []
    for w_ in TOKEN_WORDS + [t["word"] for t in tasks.letter_counts()[:5]]:
        r = requests.post(f"{url}/tokenize", json={"content": w_, "with_pieces": True, "add_special": False},
                          timeout=60)
        js = r.json()
        out.append({"text": w_, "tokens": js.get("tokens")})
        c.say("TOK", w_, js.get("tokens"))
    c.dump(os.path.join(OUT, "tokenizer-dump.json"), {"source": url, "items": out})


if __name__ == "__main__":
    cmd = sys.argv[1]
    a = c.args(sys.argv[2:])
    if cmd == "sources":
        sources()
    elif cmd == "run":
        run(a.get("models", "e4b,12b-qat").split(","), int(a.get("t1reps", 5)),
            a.get("sections", "mul,letters,dates,cutoff,cite").split(","))
    elif cmd == "tokens":
        tokens(a.get("url", "http://gemma4-limits-tok:8080"))
