"""Part 14 filming C0 (no camera): request files built with the lab's own code (SHOTLIST-14 §0 C0).
Run in the runner image: docker compose --profile tools run --rm -T runner python scripts/film14/c0.py
Body = what lab/p15.py Session.chat + lab/ollama.py chat sent for the P14 rows (temperature 0, seed 42, num_ctx 8192,
the row's num_predict, "think" always sent: False unless the think rows), except keep_alive 2m (lab 15m; no effect on
the reply)."""
import hashlib
import json
import os
import sys

sys.path.insert(0, "/work")
from lab import common as c, p14, tasks  # noqa: E402

OUT = "/work/out/p14-film"
E4B, B12 = c.TAGS["e4b"], c.TAGS["12b-qat"]


def body(tag, messages, num_predict, think=False, **extra):
    b = {"model": tag, "messages": messages, "stream": False, "keep_alive": "2m",
         "options": {"temperature": 0.0, "seed": 42, "num_predict": num_predict, "num_ctx": 8192}, "think": think}
    b.update(extra)
    return b


mul = tasks.multiplications()[0]
user = [{"role": "user", "content": mul["prompt"]}]
tool = [t for t in tasks.TOOLS if t["function"]["name"] == "multiply"]
book = [i for i in tasks.letter_counts() if i["id"] == "let_bookkeeper"][0]
wd = [i for i in tasks.date_questions(p14.TODAY) if i["id"] == "today_weekday"][0]
cut = [i for i in p14.cutoff_items() if i["id"] == "cut_ollama"][0]
paste = f"Use the source below to answer.\n\nSource:\n{cut['paste']}\n\nQuestion: {cut['prompt']}"

files = {
    "mul00.json": body(E4B, user, 256),
    "mul00-think.json": body(E4B, user, 8192, think=True),
    "tool-12b.json": body(B12, user, 1024, tools=tool),
    "tool-e4b.json": body(E4B, user, 1024, tools=tool),
    "let-bookkeeper-spell.json": body(E4B, [{"role": "user", "content": book["fix_prompt"]}], 1024),
    "date-none.json": body(E4B, [{"role": "user", "content": wd["prompt"]}], 256),
    "date-sys.json": body(E4B, [{"role": "system", "content": tasks.date_system_prompt(p14.TODAY)},
                                {"role": "user", "content": wd["prompt"]}], 256),
    "cut-ollama.json": body(B12, [{"role": "user", "content": cut["prompt"]}], 256),
    "cut-ollama-paste.json": body(B12, [{"role": "user", "content": paste}], 256),
}
os.makedirs(OUT, exist_ok=True)
for name, b in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(b, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

# lab/p15.py tool_loop step 2 in shell form: assistant message with its tool_calls, then the tool result, post again
# tool content written as Python json.dumps writes it ('{"result": N}', with the space), as the lab sent it
SEND = r"""#!/bin/sh
# usage: send-result.sh N   (step 1 reply in /tmp/r1.json)
jq --argjson n "$1" --slurpfile r /tmp/r1.json '.messages += [
  {role:"assistant", content:($r[0].message.content // ""), tool_calls:$r[0].message.tool_calls},
  {role:"tool", tool_name:"multiply", content:"{\"result\": \($n)}"}]' /film/tool-12b.json |
curl -s $OLLAMA_HOST/api/chat -d @- | jq -r .message.content
"""
with open(os.path.join(OUT, "send-result.sh"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(SEND)
os.chmod(os.path.join(OUT, "send-result.sh"), 0o755)

for name in list(files) + ["send-result.sh"]:
    print(hashlib.sha256(open(os.path.join(OUT, name), "rb").read()).hexdigest()[:16], name)
