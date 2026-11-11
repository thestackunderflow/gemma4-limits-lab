"""Lab-made test images (seed 42): terminal screenshots with known text, bar charts with known values, and
two-image cards for the interleaved prompt."""
import os
import random

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

OCR_TEXTS = [
    "$ docker compose up -d\nError response from daemon: port 8080 is already allocated",
    "Traceback (most recent call last):\n  File \"app.py\", line 42, in <module>\nKeyError: 'user_id'",
    "$ ollama ps\nNAME             SIZE     PROCESSOR    CONTEXT\ngemma4:latest    9.6 GB   100% GPU     4096",
    "npm ERR! code ERESOLVE\nnpm ERR! Could not resolve dependency: react@18.3.1",
    "FATAL: password authentication failed for user \"postgres\"",
    "$ git push origin main\n! [rejected] main -> main (fetch first)",
    "WARN[0003] container web-07 exited with code 137 (OOMKilled)",
    "server {\n    listen 443 ssl;\n    proxy_pass http://127.0.0.1:3000;\n}",
    "SELECT name, total FROM orders WHERE total > 250 ORDER BY total DESC;",
    "java.lang.OutOfMemoryError: Java heap space\n\tat com.example.Cache.put(Cache.java:88)",
]


def _card(text, path, size=28):
    font = ImageFont.truetype(MONO, size)
    lines = text.replace("\t", "    ").split("\n")
    w = max(900, max(int(font.getlength(l)) for l in lines) + 60)
    h = 60 + len(lines) * (size + 12)
    im = Image.new("RGB", (w, h), (24, 26, 33))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((30, 30 + i * (size + 12)), l, font=font, fill=(230, 230, 230))
    im.save(path)


def ocr_cards(outdir):
    os.makedirs(outdir, exist_ok=True)
    out = []
    for i, t in enumerate(OCR_TEXTS):
        p = os.path.join(outdir, f"ocr_{i:02d}.png")
        _card(t, p)
        out.append({"id": f"ocr{i:02d}", "path": p, "text": t})
    return out


CHART_SETS = [("Monthly sign-ups", ["Jan", "Feb", "Mar", "Apr"]), ("Errors per service", ["auth", "api", "web", "db"]),
              ("Sales by region", ["North", "South", "East", "West"]), ("Build minutes", ["Mon", "Tue", "Wed", "Thu"]),
              ("Tickets closed", ["Q1", "Q2", "Q3", "Q4"])]


def charts(outdir, seed=42):
    os.makedirs(outdir, exist_ok=True)
    rng = random.Random(seed)
    out = []
    for i, (title, labels) in enumerate(CHART_SETS):
        vals = {l: rng.randrange(10, 100, 5) for l in labels}
        fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
        ax.bar(labels, [vals[l] for l in labels], color="#4C78A8")
        ax.set_title(title)
        ax.set_ylim(0, 100)
        ax.set_yticks(range(0, 101, 10))
        ax.grid(axis="y", alpha=0.4)
        p = os.path.join(outdir, f"chart_{i:02d}.png")
        fig.savefig(p)
        plt.close(fig)
        out.append({"id": f"chart{i:02d}", "path": p, "title": title, "values": vals})
    return out


PAIR_WORDS = ["OTTER", "MAPLE", "COMET", "BISON", "TULIP"]


def _big(text, path, color):
    font = ImageFont.truetype(SANS, 96)
    im = Image.new("RGB", (640, 320), color)
    d = ImageDraw.Draw(im)
    d.text((320, 160), text, font=font, fill=(255, 255, 255), anchor="mm")
    im.save(path)


def pairs(outdir, seed=42):
    """Image 1 holds a word, image 2 a number (swapped on odd items); the answer is word-number."""
    os.makedirs(outdir, exist_ok=True)
    rng = random.Random(seed)
    out = []
    for i, word in enumerate(PAIR_WORDS):
        num = rng.randint(10, 99)
        a = os.path.join(outdir, f"pair_{i:02d}_a.png")
        b = os.path.join(outdir, f"pair_{i:02d}_b.png")
        if i % 2 == 0:
            _big(word, a, (60, 90, 160)), _big(str(num), b, (150, 70, 60))
            q = "Reply in the form WORD-NUMBER, using the word from the first image and the number from the second."
        else:
            _big(str(num), a, (150, 70, 60)), _big(word, b, (60, 90, 160))
            q = "Reply in the form WORD-NUMBER, using the word from the second image and the number from the first."
        out.append({"id": f"pair{i:02d}", "paths": [a, b], "question": q, "answer": f"{word}-{num}"})
    return out
