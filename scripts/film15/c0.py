"""Part 15 filming C0 (no camera): request files built with the lab's own code (SHOTLIST-15 §0 C0), copy of film14/c0.py.
Run in the runner image: docker compose --profile tools run --rm -T runner python scripts/film15/c0.py
Body = what lab/p15.py Session.chat + lab/ollama.py chat sent for the P15 rows (temperature 0, seed 42, num_ctx 8192,
num_predict 1024, "think": false), except keep_alive 2m (lab 15m; no effect on the reply). Images are the saved PNG
bytes in out/p15/images (never re-drawn: images.ocr_cards/charts are called on a scratch dir only for the prompt
text, the chart keys and the wanted values)."""
import base64
import hashlib
import json
import os
import sys
import tempfile

sys.path.insert(0, "/work")
from lab import common as c, images, tasks  # noqa: E402

OUT = "/work/out/p15-film"
IMG = "/work/out/p15/images"
E4B = c.TAGS["e4b"]


def b64(path):
    return base64.b64encode(open(path, "rb").read()).decode()


def body(tag, messages, num_predict=1024, think=False, **extra):
    b = {"model": tag, "messages": messages, "stream": False, "keep_alive": "2m",
         "options": {"temperature": 0.0, "seed": 42, "num_predict": num_predict, "num_ctx": 8192}, "think": think}
    b.update(extra)
    return b


scratch = tempfile.mkdtemp()
ocr = [i for i in images.ocr_cards(scratch) if i["id"] == "ocr00"][0]
chart = [i for i in images.charts(scratch) if i["id"] == "chart04"][0]
mul1 = [i for i in tasks.tool_prompts() if i["id"] == "mul1"][0]

files = {
    "ocr00.json": body(E4B, [{"role": "user", "content": "Transcribe all the text in this image exactly as written, "
                              "keeping the line breaks. Output only the text.",
                              "images": [b64(os.path.join(IMG, "ocr_00.png"))]}]),
    "chart04.json": body(E4B, [{"role": "user", "content": "Read the value of each bar in this chart. Reply with JSON "
                                "only, keys " + ", ".join(chart["values"]) + ", numbers as values.",
                                "images": [b64(os.path.join(IMG, "chart_04.png"))]}]),
    "tools-e4b.json": body(E4B, [{"role": "user", "content": mul1["prompt"]}], tools=tasks.TOOLS),
}
os.makedirs(OUT, exist_ok=True)
for name, b in files.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(b, fh, ensure_ascii=False, indent=1)
        fh.write("\n")

with open(os.path.join(OUT, "want-ocr00.txt"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(images.OCR_TEXTS[0] + "\n")

# lab/p15.py tool_loop round 2 in shell form (P14's send-result.sh with tools-e4b.json): assistant message with its
# tool_calls, then the tool result as json.dumps writes it ('{"result": N}', with the space), post again
SEND = r"""#!/bin/sh
# usage: send-result.sh N   (step 1 reply in /tmp/r1.json)
jq --argjson n "$1" --slurpfile r /tmp/r1.json '.messages += [
  {role:"assistant", content:($r[0].message.content // ""), tool_calls:$r[0].message.tool_calls},
  {role:"tool", tool_name:"multiply", content:"{\"result\": \($n)}"}]' /film/tools-e4b.json |
curl -s $OLLAMA_HOST/api/chat -d @- | jq -r .message.content
"""
with open(os.path.join(OUT, "send-result.sh"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(SEND)
os.chmod(os.path.join(OUT, "send-result.sh"), 0o755)

for name in list(files) + ["want-ocr00.txt", "send-result.sh"]:
    print(hashlib.sha256(open(os.path.join(OUT, name), "rb").read()).hexdigest()[:16], name)
print("chart04 values", chart["values"], "ocr00 text ok", ocr["text"] == images.OCR_TEXTS[0])
