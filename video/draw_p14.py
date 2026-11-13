"""Gemma Series Part 14 cards (SCRIPT-14.md rev 2), the draw_p13.py pattern (its helpers imported): light, 2560 x 1440,
line diagrams only (the F0 flash and the F2 intern are clean line drawings, no illustrated art), each step adds,
earlier steps stay and turn grey. Text 44 px+. Numbers only from SCRIPT-14.md section 5 (NUMBERS).
  card-f0            F0 flash (cause): the intern writes the product one digit at a time, guessing the next
  card-intern-1..4   F2: the intern; no calculator / calendar / internet (grey outlines); a calculator handed over;
                     the three kinds of fix
  card-think-1..2    F4: thinking off (question -> answer), thinking on (question -> scratch work -> answer)
  card-tool-1..5     F6: the tool-call loop, 4 steps + "that round trip = a tool call"
  card-token         F9: token = a word piece the model reads (bookkeeper -> book | keeper)
  card-sys-1..2      F12: the system prompt goes before your message; the date slots into it
  card-rule13-1..2   F13: the rule card, lines 1-2 (so far: two failures, two fixes)
  card-rule-1..5     F18: lines 1-2 back (line 1 with "no call -> do the math in code"), then 3-5 one at a time
  card-end-1         F19: the same intern, with the tools now
  card-end           F19: Gemma Series Part 14, the Part 15 tile (Next only here), room for the end screen
  ov-sub             F13: the small Like + Subscribe lower-third (P13 cut 3's, no Next)
Run in the draw image:  docker run --rm -v "<lab>:/lab" -w /lab cad3way-draw:1 python3 video/draw_p14.py"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('draw_p13', os.path.join(HERE, 'draw_p13.py'))
d13 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d13)
d13.OUT = os.path.join(d13.LAB, 'video', 'frames-p14')
OUT = d13.OUT
text, canvas, save = d13.text, d13.canvas, d13.save
B, R, M = d13.B, d13.R, d13.M
INK, GREY, DONE, DONEFILL = d13.INK, d13.GREY, d13.DONE, d13.DONEFILL
BLUE, BLUEFILL, ORANGE, ORANGEFILL, GREEN, GREENFILL = (d13.BLUE, d13.BLUEFILL, d13.ORANGE, d13.ORANGEFILL, d13.GREEN,
                                                        d13.GREENFILL)
PAPER, WOOD, WOODLINE = d13.PAPER, d13.WOOD, d13.WOODLINE


# --- the intern at a desk (line drawing) ----------------------------------------------------------------------------
def intern(d, x=520, y=330, grey=False):
    """A seated figure at a desk; (x, y) = the head's centre. Returns the desk top's (x0, x1, y)."""
    c = DONE if grey else INK
    d.ellipse([x - 90, y - 90, x + 90, y + 90], outline=c, width=8, fill=(DONEFILL if grey else (255, 255, 255)))
    d.line([x - 30, y - 10, x - 30, y + 5], fill=c, width=8)                    # eyes
    d.line([x + 30, y - 10, x + 30, y + 5], fill=c, width=8)
    d.arc([x - 40, y + 5, x + 40, y + 50], 20, 160, fill=c, width=7)            # smile
    d.polygon([(x - 130, y + 120), (x + 130, y + 120), (x + 160, y + 460), (x - 160, y + 460)],
              outline=c, width=8, fill=(DONEFILL if grey else BLUEFILL))
    d.line([x + 120, y + 200, x + 330, y + 420], fill=c, width=14)              # writing arm
    dy = y + 460
    d.rectangle([x - 360, dy, x + 1250, dy + 60], fill=(DONEFILL if grey else WOOD), outline=(DONE if grey else WOODLINE),
                width=6)
    d.line([x - 300, dy + 60, x - 300, dy + 330], fill=(DONE if grey else WOODLINE), width=14)
    d.line([x + 1190, dy + 60, x + 1190, dy + 330], fill=(DONE if grey else WOODLINE), width=14)
    return x - 360, x + 1250, dy


def calculator(d, x, y, grey=False, dashed=False):
    c = DONE if (grey or dashed) else BLUE
    d.rounded_rectangle([x, y, x + 200, y + 280], 18, outline=c, width=7, fill=(None if dashed else (DONEFILL if grey else BLUEFILL)))
    d.rectangle([x + 25, y + 25, x + 175, y + 85], outline=c, width=5)
    for i in range(3):
        for j in range(3):
            d.rectangle([x + 30 + j * 50, y + 110 + i * 52, x + 70 + j * 50, y + 148 + i * 52], outline=c, width=4)


def calendar(d, x, y, grey=False, dashed=False):
    c = DONE if (grey or dashed) else BLUE
    d.rectangle([x, y, x + 260, y + 240], outline=c, width=7, fill=(None if dashed else (DONEFILL if grey else BLUEFILL)))
    d.rectangle([x, y, x + 260, y + 60], outline=c, width=7)
    for i in range(3):
        for j in range(4):
            d.rectangle([x + 20 + j * 60, y + 85 + i * 50, x + 55 + j * 60, y + 115 + i * 50], outline=c, width=3)


def laptop(d, x, y, grey=False, dashed=False, signal=False):
    c = DONE if (grey or dashed) else BLUE
    d.rectangle([x + 20, y, x + 300, y + 190], outline=c, width=7, fill=(None if dashed else (DONEFILL if grey else BLUEFILL)))
    d.polygon([(x, y + 210), (x + 320, y + 210), (x + 340, y + 250), (x - 20, y + 250)], outline=c, width=6)
    cx, cy = x + 160, y + 150                                                    # wifi arcs
    for r in (30, 60, 90):
        d.arc([cx - r, cy - r, cx + r, cy + r], 225, 315, fill=c, width=6)
    if not signal:
        d.line([cx - 80, cy - 110, cx + 80, cy + 10], fill=(ORANGE if not grey else DONE), width=9)


def card_f0():
    im, d = canvas()
    x0, x1, dy = intern(d, 560, 360)
    d.rectangle([900, dy - 230, 1900, dy - 10], fill=PAPER, outline=INK, width=5)       # the sheet
    digits = '3978816'
    for k, ch in enumerate(digits):
        text(d, (960 + k * 110, dy - 70), ch, 120, fill=(INK if k < 6 else ORANGE), path=M, anchor='ls')
    text(d, (960 + 6 * 110 + 60, dy - 210), '?', 96, fill=ORANGE, anchor='ls')
    d.ellipse([1500, 120, 2420, 420], outline=GREY, width=6, fill=(255, 255, 255))     # the thought
    text(d, (1960, 250), 'the next digit', 64, fill=INK, anchor='ms')
    text(d, (1960, 340), 'that looks right', 64, fill=INK, anchor='ms')
    text(d, (1280, 1380), 'no calculator: it guesses one digit after the other', 60, fill=ORANGE, anchor='ms')
    save(im, 'card-f0')


def card_intern():
    for step in (1, 2, 3, 4):
        im, d = canvas('Picture an intern on day one')
        x0, x1, dy = intern(d, 560, 420, grey=(step == 4))
        if step == 1:
            text(d, (1100, 520), 'fast, fluent,', 72, fill=INK)
            text(d, (1100, 620), 'sure of every answer', 72, fill=INK)
        if step >= 2:
            g = step == 4
            calculator(d, 1000, dy - 290, dashed=True)
            calendar(d, 1450, dy - 250, dashed=True)
            laptop(d, 1960, dy - 260, dashed=True)
            for xx, s in ((1100, 'no calculator'), (1580, 'no calendar'), (2120, 'no internet')):
                text(d, (xx, dy - 330), s, 52, fill=(DONE if g else ORANGE), anchor='ms')
        if step >= 3:
            calculator(d, 1000, dy - 290, grey=(step == 4))
            if step == 3:
                text(d, (1100, dy + 160), '↑ hand it over', 60, fill=BLUE, anchor='ms')
        if step == 4:
            d.rounded_rectangle([1060, 200, 2440, 1290], 30, fill=(255, 255, 255), outline=BLUE, width=7)
            text(d, (1120, 330), 'Every fix in this video:', 72, fill=INK)
            for k, s in enumerate(('the right tool', 'the right page', 'a better way to work')):
                y = 520 + k * 250
                d.rounded_rectangle([1120, y, 2380, y + 190], 24, fill=BLUEFILL, outline=BLUE, width=6)
                text(d, (1180, y + 125), s, 80, fill=BLUE, anchor='ls')
        save(im, f'card-intern-{step}')


def flow_box(d, x, y, w, h, s, cur, sub=None):
    d.rounded_rectangle([x, y, x + w, y + h], 24, fill=(BLUEFILL if cur else DONEFILL), outline=(BLUE if cur else DONE),
                        width=6)
    text(d, (x + w / 2, y + (h / 2 + 24 if not sub else h / 2 - 8)), s, 72, fill=(INK if cur else GREY), anchor='ms')
    if sub:
        text(d, (x + w / 2, y + h / 2 + 70), sub, 52, fill=(GREY if cur else DONE), path=R, anchor='ms')


def arrow(d, a, b, cur, label=None, at=None):
    c = ORANGE if cur else DONE
    d.line([a, b], fill=c, width=10)
    import math
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (-1, 1):
        d.line([b, (b[0] - 40 * math.cos(ang + s * 0.45), b[1] - 40 * math.sin(ang + s * 0.45))], fill=c, width=10)
    if label:
        text(d, at, label, 56, fill=(INK if cur else DONE), path=(M if cur else M), anchor='ms')


def card_think():
    for step in (1, 2):
        im, d = canvas('Thinking mode')
        y = 360
        cur1 = step == 1
        text(d, (160, y - 30), 'thinking off', 64, fill=(INK if cur1 else DONE), anchor='ls')
        flow_box(d, 160, y, 620, 220, 'question', cur1)
        arrow(d, (800, y + 110), (1760, y + 110), cur1)
        flow_box(d, 1780, y, 620, 220, 'answer', cur1)
        if step == 2:
            y = 860
            text(d, (160, y - 30), 'thinking on', 64, fill=INK, anchor='ls')
            flow_box(d, 160, y, 620, 220, 'question', True)
            arrow(d, (800, y + 110), (960, y + 110), True)
            flow_box(d, 980, y, 620, 220, 'scratch work', True, sub='written first')
            arrow(d, (1620, y + 110), (1760, y + 110), True)
            flow_box(d, 1780, y, 620, 220, 'answer', True)
        save(im, f'card-think-{step}')


def card_tool():
    """The loop: your app (left), the model (right), your code (under the app). Each step adds; earlier steps grey."""
    steps = [('a tool exists: multiply(a, b)', 'app2model'), ('call multiply 2824, 1409', 'model2app'),
             ('2824 × 1409 = 3979016 → back', 'code'), ('3,979,016', 'answer')]
    for step in range(1, 6):
        im, d = canvas('A tool call: the model asks, your code runs it')
        flow_box(d, 160, 300, 460, 220, 'your app', True)
        flow_box(d, 1940, 300, 460, 220, 'model', True)
        flow_box(d, 160, 960, 460, 220, 'your code', step >= 3)
        for k in range(min(step, 4)):
            cur = (k == step - 1)
            s, kind = steps[k]
            if kind == 'app2model':
                arrow(d, (640, 370), (1920, 370), cur, f'1  {s}', (1280, 340))
            elif kind == 'model2app':
                arrow(d, (1920, 470), (640, 470), cur, f'2  {s}', (1280, 560))
            elif kind == 'code':
                arrow(d, (390, 540), (390, 940), cur)
                text(d, (160, 1290), f'3  {s}', 60, fill=(INK if cur else DONE), path=M, anchor='ls')
                arrow(d, (640, 1070), (1990, 540), cur)
            else:
                d.rounded_rectangle([1940, 640, 2400, 860], 24, fill=(GREENFILL if cur else DONEFILL),
                                    outline=(GREEN if cur else DONE), width=6)
                text(d, (2170, 780), s, 64, fill=(GREEN if cur else DONE), path=M, anchor='ms')
                text(d, (2170, 920), '4  the answer', 56, fill=(INK if cur else DONE), anchor='ms')
        if step == 5:
            d.rounded_rectangle([1300, 1040, 2400, 1190], 24, fill=ORANGEFILL, outline=ORANGE, width=6)
            text(d, (1850, 1140), 'that round trip = a tool call', 68, fill=ORANGE, anchor='ms')
        save(im, f'card-tool-{step}')


def card_token():
    im, d = canvas('The model reads tokens, not letters')
    d.rounded_rectangle([160, 280, 2400, 480], 24, fill=ORANGEFILL, outline=ORANGE, width=6)
    text(d, (1280, 410), 'token = a word piece the model reads', 80, fill=INK, anchor='ms')
    text(d, (220, 760), 'bookkeeper', 110, fill=GREY, path=M, anchor='ls')
    text(d, (1100, 760), '→', 110, fill=ORANGE, anchor='ls')
    for x, s in ((1300, 'book'), (1760, 'keeper')):
        w = 120 + 66 * len(s)
        d.rounded_rectangle([x, 640, x + w, 800], 20, fill=BLUEFILL, outline=BLUE, width=6)
        text(d, (x + w / 2, 760), s, 110, fill=BLUE, path=M, anchor='ms')
    text(d, (220, 1050), 'two pieces: the letters inside are not seen one by one', 60, fill=GREY, path=R, anchor='ls')
    save(im, 'card-token')


def card_sys():
    for step in (1, 2):
        im, d = canvas('The system prompt: sent before your message')
        d.rounded_rectangle([160, 300, 2400, 640], 24, fill=BLUEFILL, outline=BLUE, width=6)
        text(d, (220, 400), 'system prompt', 72, fill=BLUE, anchor='ls')
        text(d, (220, 480), 'instructions the app sends before your message', 56, fill=GREY, path=R, anchor='ls')
        if step == 2:
            d.rounded_rectangle([220, 520, 2340, 620], 18, fill=(255, 255, 255), outline=ORANGE, width=6)
            text(d, (260, 596), "Today's date is Tuesday, 10 November 2026", 60, fill=ORANGE, path=M, anchor='ls')
        d.rounded_rectangle([160, 760, 2400, 1000], 24, fill=(DONEFILL if step == 2 else (255, 255, 255)),
                            outline=(DONE if step == 2 else INK), width=6)
        text(d, (220, 860), 'your message', 72, fill=(GREY if step == 2 else INK), anchor='ls')
        text(d, (220, 950), 'What day of the week is it today?', 56, fill=(DONE if step == 2 else GREY), path=R,
             anchor='ls')
        save(im, f'card-sys-{step}')


RULES = ['1. number → calculator tool, check the call', '2. letter count → spell it out first',
         '3. date → put it in the system prompt', '4. recent facts → paste the source',
         '5. citation → open the DOI at doi.org']
SUB1 = 'no call → do the math in code'


def rule_card(name, title, n, cur_k, sub):
    im, d = canvas(title)
    y = 220
    for k in range(n):
        cur = k == cur_k
        h = 250 if (k == 0 and sub) else 170
        d.rounded_rectangle([160, y, 2400, y + h], 24, fill=(BLUEFILL if cur else DONEFILL),
                            outline=(BLUE if cur else DONE), width=6)
        text(d, (220, y + 112), RULES[k], 68, fill=(INK if cur else GREY), path=M, anchor='ls')
        if k == 0 and sub:
            text(d, (300, y + 205), SUB1, 56, fill=(BLUE if cur else GREY), path=M, anchor='ls')
        y += h + 30
    save(im, name)


def card_rules():
    for n in (1, 2):
        rule_card(f'card-rule13-{n}', 'So far: two failures, two fixes', n, n - 1, False)
    for n in range(1, 6):          # lines 1-2 come back at once; the current line is blue, the others grey
        rule_card(f'card-rule-{n}', 'Check it yourself', max(n, 2), n - 1, True)


def card_end():
    im, d = canvas('Not stupid: it just started today')
    x0, x1, dy = intern(d, 560, 420)
    calculator(d, 1000, dy - 290)
    calendar(d, 1450, dy - 250)
    laptop(d, 1960, dy - 260, signal=True)
    text(d, (1500, 330), 'give it the tools', 72, fill=GREEN, anchor='ms')
    save(im, 'card-end-1')
    im, d = canvas()
    text(d, (160, 200), 'Gemma Series · Part 14', 96)
    text(d, (160, 300), 'Ollama 0.40.16 · RTX 4060 8 GB · gemma4:e4b-it-q4_K_M, gemma4:12b-it-qat', 52, fill=GREY, path=R)
    d.rounded_rectangle([160, 460, 1200, 1100], 30, fill=BLUEFILL, outline=BLUE, width=8)
    text(d, (220, 600), 'Next: Part 15', 80, fill=BLUE)
    text(d, (220, 760), 'what the same models', 64)
    text(d, (220, 850), 'can do, each claim', 64)
    text(d, (220, 940), 'scored by code', 64)
    text(d, (160, 1250), 'Five failures, five fixes: check it yourself.', 64, fill=INK, path=R)
    save(im, 'card-end')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    card_f0(); card_intern(); card_think(); card_tool(); card_token(); card_sys(); card_rules(); card_end()
    d13.ov_sub()
    print('cards:', sorted(os.listdir(OUT)))
    if d13.PROBLEMS:
        raise SystemExit('PROBLEMS: ' + '; '.join(d13.PROBLEMS))
