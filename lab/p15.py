"""Part 15 (P-CAN, P-AUD): the model card's capability lines, each scored by code.
python -m lab.p15 can --models e4b,12b-qat [--temp 0 --reps 1] | tools --models 26b | aud --models e2b,e4b,12b-q4"""
import base64
import json
import os
import subprocess
import sys
import time

import jsonschema
import requests

from lab import common as c, graders as g, images, logparse, ollama as o, samples, tasks

OUT = os.path.join(c.ROOT, "out", "p15")
KEEP = "15m"   # P-CAN runs warm (one load per model per section); only the first row of a section is a fresh load


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


class Session:
    def __init__(self, key, temp, seed, w, section):
        self.key, self.tag, self.temp, self.seed, self.w, self.section = key, c.TAGS[key], temp, seed, w, section
        self.first = c.fresh()

    def chat(self, messages, think=False, num_predict=1024, **extra):
        # llama-server keeps a host-RAM prompt cache that grows over a long warm session (2.3 -> 4.7 GiB in 25 min
        # on 11 Nov, which took Windows under 1 GB free once): reload when the container passes 6 GiB.
        last = samples.mem()[-1:] if samples.mem() else []
        if last and (last[0]["ram_mib"] or 0) > 6144:
            c.say("container RAM", last[0]["ram_mib"], "MiB: reloading")
            self.first = c.fresh()
        m = o.log_mark()
        st, js, dt = o.chat(self.tag, messages, {"temperature": self.temp, "seed": self.seed,
                                                 "num_predict": num_predict, "num_ctx": 8192},
                            keep_alive=KEEP, think=think, **extra)
        log = o.log_since(m, settle=0.2)
        fresh, self.first = self.first, False
        return st, js, dt, log, fresh

    def row(self, item_id, log, fresh, **kw):
        r = c.provenance(self.tag, log, num_ctx=8192, temperature=self.temp, fresh_load=fresh, model=self.key,
                         section=self.section, item=item_id, seed=self.seed, **kw)
        self.w.write(r)
        return r


def content(js):
    return ((js.get("message") or {}).get("content") or "").strip()


def sec_ocr(s):
    items = images.ocr_cards(os.path.join(OUT, "images"))
    n = 0
    for it in items:
        st, js, dt, log, f = s.chat([{"role": "user", "content": "Transcribe all the text in this image exactly as "
                                      "written, keeping the line breaks. Output only the text.",
                                      "images": [b64(it["path"])]}])
        ok = g.exact_match(content(js), it["text"])
        n += ok
        s.row(it["id"], log, f, status=st, answer=content(js), want=it["text"], passed=ok, seconds=round(dt, 1))
    return n, len(items)


def sec_charts(s):
    items = images.charts(os.path.join(OUT, "images"))
    n = 0
    for it in items:
        keys = list(it["values"])
        st, js, dt, log, f = s.chat([{"role": "user", "content": "Read the value of each bar in this chart. Reply "
                                      "with JSON only, keys " + ", ".join(keys) + ", numbers as values.",
                                      "images": [b64(it["path"])]}])
        exact = g.values_in_json(content(js), it["values"])
        near = g.values_in_json(content(js), it["values"], tol=5)
        ok = exact[0] == exact[1]
        n += ok
        s.row(it["id"], log, f, status=st, answer=content(js), want=it["values"], passed=ok, exact=exact,
              within_5=near, seconds=round(dt, 1))
    return n, len(items)


def sec_pairs(s):
    items = images.pairs(os.path.join(OUT, "images"))
    n = 0
    for it in items:
        msgs = [{"role": "user", "content": "Image 1:", "images": [b64(it["paths"][0])]},
                {"role": "user", "content": "Image 2:", "images": [b64(it["paths"][1])]},
                {"role": "user", "content": it["question"] + " Output only that."}]
        st, js, dt, log, f = s.chat(msgs)
        ok = it["answer"].upper() in content(js).upper().replace(" ", "")
        n += ok
        s.row(it["id"], log, f, status=st, answer=content(js), want=it["answer"], passed=ok, seconds=round(dt, 1))
    return n, len(items)


def _args_match(got, want):
    for k, v in want.items():
        gv = got.get(k)
        if isinstance(v, (int, float)):
            try:
                if float(gv) != float(v):
                    return False
            except (TypeError, ValueError):
                return False
        elif str(gv).strip().lower() != str(v).lower():
            return False
    return True


def tool_loop(s, prompt, tools=None, max_rounds=3, system=None, think=False):
    """Model asks -> our code runs the tool -> result goes back. Returns (calls, final_text, seconds, log, fresh)."""
    tools = tools or tasks.TOOLS
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    calls, logs, t0, fresh0 = [], "", time.time(), None
    for _ in range(max_rounds):
        st, js, dt, log, f = s.chat(msgs, tools=tools, think=think)
        fresh0 = f if fresh0 is None else fresh0
        logs += log
        m = js.get("message") or {}
        tc = m.get("tool_calls") or []
        if not tc:
            return calls, (m.get("content") or "").strip(), time.time() - t0, logs, fresh0, st
        msgs.append({"role": "assistant", "content": m.get("content") or "", "tool_calls": tc})
        for call in tc:
            fn = call.get("function", {})
            name, a = fn.get("name"), fn.get("arguments") or {}
            if isinstance(a, str):
                try:
                    a = json.loads(a)
                except ValueError:
                    a = {}
            res = tasks.run_tool(name, a)
            calls.append({"name": name, "arguments": a, "result": res})
            msgs.append({"role": "tool", "content": json.dumps(res), "tool_name": name})
    return calls, "", time.time() - t0, logs, fresh0, st


def sec_tools(s):
    schemas = {t["function"]["name"]: t["function"]["parameters"] for t in tasks.TOOLS}
    n = 0
    for it in tasks.tool_prompts():
        calls, final, dt, log, f, st = tool_loop(s, it["prompt"])
        first = calls[0] if calls else {}
        right_tool = first.get("name") == it["tool"]
        valid = False
        if right_tool:
            try:
                jsonschema.validate(first["arguments"], schemas[it["tool"]])
                valid = True
            except jsonschema.ValidationError:
                pass
        args_ok = right_tool and _args_match(first.get("arguments", {}), it["args"])
        ans_ok = it["answer"].lower() in final.replace(",", "").lower()
        ok = right_tool and valid and args_ok and ans_ok
        n += ok
        s.row(it["id"], log, f, status=st, calls=calls, answer=final, right_tool=right_tool, schema_valid=valid,
              args_ok=args_ok, answer_ok=ans_ok, passed=ok, seconds=round(dt, 1))
    return n, 10


def sec_coding(s):
    n = 0
    for it in tasks.coding():
        st, js, dt, log, f = s.chat([{"role": "user", "content": it["prompt"]}])
        code = g.extract_code(content(js))
        ok_n, tot, err = g.run_unit_tests(code, it["tests"])
        ok = ok_n == tot
        n += ok
        s.row(it["id"], log, f, status=st, answer=content(js)[:3000], tests_passed=ok_n, tests_total=tot,
              last_error=err, passed=ok, seconds=round(dt, 1))
    return n, 10


def sec_multilingual(s):
    n = 0
    for it in tasks.multilingual():
        st, js, dt, log, f = s.chat([{"role": "user", "content": it["prompt"]}])
        ok = g.int_ok(content(js), it["answer"])
        n += ok
        s.row(it["id"], log, f, status=st, lang=it["lang"], answer=content(js), want=it["answer"], passed=ok,
              seconds=round(dt, 1))
    return n, 10


def sec_thinking(s):
    res = {}
    for think in (False, True):
        n, secs = 0, []
        for it in tasks.puzzles():
            st, js, dt, log, f = s.chat([{"role": "user", "content": it["prompt"]}], think=think,
                                        num_predict=8192 if think else 1024)
            ok = g.int_ok(content(js), it["answer"])
            n += ok
            secs.append(dt)
            s.row(it["id"], log, f, status=st, think=think, answer=content(js)[-400:],
                  thinking_chars=len((js.get("message") or {}).get("thinking") or ""), eval_count=js.get("eval_count"),
                  want=it["answer"], passed=ok, seconds=round(dt, 1))
        res["on" if think else "off"] = {"passed": n, "total": 10, "seconds_total": round(sum(secs), 1)}
    return res


def sec_json(s):
    n = 0
    for it in tasks.json_extractions():
        st, js, dt, log, f = s.chat([{"role": "user", "content": it["prompt"]}], format=it["schema"])
        ok_n, tot = g.values_in_json(content(js), it["answer"], tol=0)
        ok = ok_n == tot
        n += ok
        s.row(it["id"], log, f, status=st, answer=content(js), want=it["answer"], fields_ok=ok_n, fields=tot,
              passed=ok, seconds=round(dt, 1))
    return n, 10


SECTIONS = {"ocr": sec_ocr, "charts": sec_charts, "pairs": sec_pairs, "tools": sec_tools, "coding": sec_coding,
            "multilingual": sec_multilingual, "thinking": sec_thinking, "json": sec_json}


def can(models, sections, temp=0.0, reps=1):
    w = c.writer("p15", "can")
    summary_path = os.path.join(OUT, "can-summary.jsonl")
    for key in models:
        for rep in range(1, reps + 1):
            seed = 42 if temp == 0 else 1000 + rep
            for sec in sections:
                s = Session(key, temp, seed, w, sec)
                r = SECTIONS[sec](s)
                line = {"model": key, "section": sec, "temperature": temp, "rep": rep, "seed": seed, "result": r}
                with open(summary_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(line) + "\n")
                c.say("CAN", key, sec, "temp", temp, "rep", rep, r)
            c.fresh()


# ---------- P-AUD ----------
LIBRIVOX_INTRO = ("Chapter 1 of Pride and Prejudice. This is a LibriVox recording. All LibriVox recordings are in "
                  "the public domain. For more information or to volunteer, please visit librivox.org. Pride and "
                  "Prejudice by Jane Austen. Chapter 1. It is a truth universally acknowledged, that a single man in "
                  "possession of a good fortune, must be in want of a wife.")
ESPEAK_TEXT = "The quick brown fox jumps over the lazy dog. Ollama runs Gemma four on an eight gigabyte card."


def make_clips():
    d = os.path.join(OUT, "audio")
    os.makedirs(d, exist_ok=True)
    clips = []
    es = os.path.join(d, "espeak.wav")
    if not os.path.exists(es):
        subprocess.run(["espeak-ng", "-s", "150", "-w", es + ".raw.wav", ESPEAK_TEXT], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", es + ".raw.wav", "-ar", "16000", "-ac", "1", es],
                       check=True)
        os.remove(es + ".raw.wav")
    clips.append({"id": "espeak", "path": es, "truth": ESPEAK_TEXT, "truth_note": "lab-made, exact"})
    lv = os.path.join(d, "librivox.wav")
    if os.path.exists(lv):
        clips.append({"id": "librivox", "path": lv, "truth": LIBRIVOX_INTRO,
                      "truth_note": "best-guess script (standard LibriVox disclaimer + first sentence), not checked "
                                    "by ear; a 30 s cut can end mid-sentence; transcript kept for a human check"})
    return clips


def aud(models):
    w = c.writer("p15", "aud")
    clips = make_clips()
    for key in models:
        tag = c.TAGS[key]
        caps = c.info(tag)["capabilities"]
        has_audio = "audio" in caps
        s = Session(key, 0.0, 42, w, "audio")
        # control: same prompt, no clip
        st, js, dt, log, f = s.chat([{"role": "user", "content": "Transcribe this audio exactly. Output only the "
                                      "words spoken."}])
        s.row("no-clip-control", log, f, status=st, answer=content(js), capabilities=caps, route="/api/chat")
        for cl in clips:
            st, js, dt, log, f = s.chat([{"role": "user", "content": "Transcribe this audio exactly. Output only "
                                          "the words spoken.", "images": [b64(cl["path"])]}])
            ans = content(js) if st == 200 else ""
            s.row(cl["id"], log, f, status=st, answer=ans, error=js.get("error"), route="/api/chat images field",
                  capabilities=caps, has_audio_capability=has_audio,
                  wer=round(g.wer(cl["truth"], ans), 3) if ans else None, truth=cl["truth"],
                  truth_note=cl["truth_note"], seconds=round(dt, 1))
            c.say("AUD chat", key, cl["id"], st, (ans or js.get("error", ""))[:80])
            m, t0 = o.log_mark(), time.time()
            try:
                r = requests.post(f"{o.URL}/v1/audio/transcriptions", data={"model": tag},
                                  files={"file": (os.path.basename(cl["path"]), open(cl["path"], "rb"), "audio/wav")},
                                  timeout=900)
                st2, body = r.status_code, r.text[:2000]
                try:
                    txt = r.json().get("text", "")
                except ValueError:
                    txt = ""
            except Exception as e:
                st2, body, txt = 0, repr(e)[:300], ""
            log = o.log_since(m, settle=0.2)
            s.row(cl["id"], log, False, status=st2, answer=txt, body=body, route="/v1/audio/transcriptions",
                  capabilities=caps, wer=round(g.wer(cl["truth"], txt), 3) if txt else None, truth=cl["truth"],
                  seconds=round(time.time() - t0, 1))
            c.say("AUD v1", key, cl["id"], st2, (txt or body)[:80])
        c.fresh()


if __name__ == "__main__":
    cmd = sys.argv[1]
    a = c.args(sys.argv[2:])
    models = a.get("models", "e4b,12b-qat").split(",")
    if cmd == "can":
        can(models, a.get("sections", ",".join(SECTIONS)).split(","), float(a.get("temp", 0)), int(a.get("reps", 1)))
    elif cmd == "aud":
        aud(models)
