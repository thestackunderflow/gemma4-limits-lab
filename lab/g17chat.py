"""g17 pure parts (stdlib only; also runs inside the SolidCraft image): the 20-turn design chat, the 8-fact recall
score, where turn 1 sits after a cut, the running-summary window, tokens per turn."""
import re

SYSTEM = ("You are a CAD assistant working in SolidCraft through its MCP tools. Do each job with the tools and save "
          "every file under /lab/out. End every final reply with the line: -- plate desk")
MARKER = "-- plate desk"

TURNS = [
    "Here is the spec for my mounting plate, part BRK-17, to be printed in PETG: a flat plate 60 x 40 x 5 mm with two "
    "4.5 mm through holes, 36 mm apart along the long side, centred. Build it in SolidCraft now and save the design to "
    "/lab/out/plate.solidcraft.",
    "Try a version 3 mm thick instead.",
    "Make the holes 6 mm.",
    "Move the holes to 30 mm apart.",
    "Try a 70 x 50 mm plate.",
    "Rename this variant BRK-18.",
    "Use PLA for this variant.",
    "Add a third hole in the middle.",
    "Make the plate 8 mm thick.",
    "Make the holes 3.2 mm.",
    "Spread the holes to 50 mm apart.",
    "Try an 80 x 45 mm plate.",
    "Remove the middle hole again.",
    "Make it 4 mm thick.",
    "Try 5.5 mm holes.",
    "Rename this variant BRK-19.",
    "Use ABS for this variant.",
    "Try a 65 x 42 mm plate.",
    "Save this variant to /lab/out/variant.solidcraft.",
    "Go back to the plate exactly as specified in my first message. Build it again from that spec, export it as an STL "
    "to /lab/out/plate.stl, and list every item of that first spec: part name, material, length, width, thickness, "
    "number of holes, hole diameter and hole spacing.",
]
SPEC = TURNS[0].split(": ", 1)[1].split(" Build it")[0]   # what fix (a) pins in the system prompt
PIN = "The original spec of this chat (pinned by the app): part BRK-17, material PETG, " + SPEC

_N = r"(?<![\d.]){}(?![\d]|\.\d)"
FACTS = {
    "name": r"BRK-17",
    "material": r"\bPETG\b",
    "length": _N.format("60"),
    "width": _N.format("40"),
    "thickness": _N.format("5"),
    "holes": r"(?i)(\btwo\b|(?<![\d.])2(?![\d.]))(?=[^.\n]{0,30}hole)|holes?\W{0,20}(\btwo\b|(?<![\d.])2(?![\d.]))",
    "hole_d": _N.format(r"4\.5"),
    "spacing": _N.format("36"),
}
STALE = ["BRK-18", "BRK-19", "PLA", "ABS", "70", "50", "80", "45", "65", "42", "3.2", "5.5", "30"]


def recall(text):
    text = text or ""
    facts = {k: bool(re.search(p, text)) for k, p in FACTS.items()}
    stale = [s for s in STALE if re.search(_N.format(re.escape(s)) if s[0].isdigit() else r"\b%s\b" % re.escape(s), text)]
    return {"score": sum(facts.values()), "facts": facts, "missing": [k for k, v in facts.items() if not v],
            "stale": stale}


def marker_ok(text):
    return MARKER in (text or "")


def turn1_kept(msgs, cut):
    """Is the turn-1 user message still in the prompt after `cut`? msgs = what the app sent."""
    i1 = next(i for i, m in enumerate(msgs) if m.get("role") == "user")
    if not cut:
        return True
    if cut["kind"] == "messages_dropped":
        return i1 >= len(msgs) - cut["kept"]
    if cut["kind"] == "native_messages_dropped":
        return i1 >= cut["first_kept_index"]
    return None   # runner token cut: tokens from the middle, not whole messages (reported apart)


def window_summary(system, summary, turns, keep=4):
    """Fix (c): system + the app's summary (as a user note + ack) + the last `keep` turns (each a message list)."""
    out = [system]
    if summary:
        out += [{"role": "user", "content": "Short spec of our chat so far (kept by the app): " + summary},
                {"role": "assistant", "content": "Noted."}]
        turns = turns[-keep:]
    for t in turns:
        out += t
    return out


def tokens_per_turn(reqs):
    out = {}
    for r in reqs:
        out[r["turn"]] = out.get(r["turn"], 0) + (r.get("prompt_eval_count") or 0)
    return out


def first_turn(reqs, pred):
    for r in reqs:
        if pred(r):
            return r["turn"]
    return None
