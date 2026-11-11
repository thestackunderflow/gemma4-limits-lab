"""Public-domain haystack: Project Gutenberg eBook #1342 (data/SOURCES.md). Paragraphs between the START/END marks."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = {"pg1342": os.path.join(ROOT, "data", "pg1342.txt")}


def paragraphs(book="pg1342"):
    t = open(BOOKS[book], encoding="utf-8").read()
    t = t[t.find("\n", t.find("*** START")):t.find("*** END")]
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", t)]
    return [p for p in paras if len(p.split()) >= 8]


def words(n, book="pg1342", start=0):
    """About n words of whole paragraphs, starting at paragraph `start`."""
    ps, out, c, i = paragraphs(book), [], 0, start
    while c < n:
        p = ps[i % len(ps)]
        out.append(p)
        c += len(p.split())
        i += 1
    return "\n\n".join(out)
