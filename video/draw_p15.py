"""Gemma Series Part 15 cards (SCRIPT-15.md rev 3), the draw_p14.py pattern (draw_p13 helpers + P14's intern): light,
2560 x 1440, line diagrams only (the F0 flash and the F2 CV analogy are clean line drawings, no illustrated art), each
step adds, earlier steps stay and turn grey. Text 44 px+. Numbers only from SCRIPT-15.md section 5 (NUMBERS).
  card-f0            F0 flash (2.5 s): the intern's CV on a desk, a pen ticking the first line; 9 listed, 7 tested
  card-cv-1..4       F2: the intern (fast, sure); + the CV (4 lines); + a test sheet per line (one half tick);
                     the model card = Gemma 4's CV
  card-mc-1..2       F3: the model card's nine lines; seven ticked "tested", long context / video grey
  card-loop-0..4     F8: the tool-call loop (P14's), 4 steps, six functions offered
  card-board-1..6    F13b: the scoreboard, rows 1-6 one at a time (so far, E4B); room for the lower-third
  card-board19-0..6  F19: rows 1-6 back (row 6 + the 12B), then highlighted with the words, row 7 audio, 2 grey lines
  card-audio-1..3    F15: what the card says; the 2 clips; the 2 ways in
  card-check-1..3    F20: want.txt, ollama run --think=false into got.txt, diff -wB (+ Windows fc /w)
  card-end-1         F21: the intern's CV, mostly ticked
  card-end           F21: Gemma Series Part 15, the Part 16 tile (Next only here), room for the end screen
  ov-sub             F13b: the small Like + Subscribe lower-third (P13 cut 3's, no Next)
Run in the draw image:  docker run --rm -v "<lab>:/lab" -w /lab cad3way-draw:1 python3 video/draw_p15.py"""
import importlib.util
import os

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('draw_p14', os.path.join(HERE, 'draw_p14.py'))
d14 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d14)
d13 = d14.d13
d13.OUT = os.path.join(d13.LAB, 'video', 'frames-p15')
OUT = d13.OUT
text, canvas, save = d13.text, d13.canvas, d13.save
B, R, M = d13.B, d13.R, d13.M
INK, GREY, DONE, DONEFILL = d13.INK, d13.GREY, d13.DONE, d13.DONEFILL
BLUE, BLUEFILL, ORANGE, ORANGEFILL, GREEN, GREENFILL = (d13.BLUE, d13.BLUEFILL, d13.ORANGE, d13.ORANGEFILL, d13.GREEN,
                                                        d13.GREENFILL)
PAPER = d13.PAPER
intern, flow_box, arrow = d14.intern, d14.flow_box, d14.arrow


def tick(d, x, y, s=44, c=GREEN, half=False):
    """A tick mark with its corner at (x, y); half = only the short stroke + a dash (a half tick)."""
    d.line([x - s, y - s * 0.8, x, y], fill=c, width=12)
    if half:
        d.line([x + 14, y - s * 0.5, x + s * 1.2, y - s * 0.5], fill=c, width=12)
    else:
        d.line([x, y, x + s * 1.8, y - s * 2.2], fill=c, width=12)


def cross(d, x, y, s=36, c=ORANGE):
    d.line([x - s, y - s, x + s, y + s], fill=c, width=12)
    d.line([x - s, y + s, x + s, y - s], fill=c, width=12)


CV_LINES = ['reads documents', 'uses tools', 'writes code', 'speaks languages']


def cv_sheet(d, x, y, w=900, grey=False, ticks=0, half=None, title='CV'):
    c = DONE if grey else INK
    d.rectangle([x, y, x + w, y + 640], fill=(DONEFILL if grey else PAPER), outline=c, width=6)
    text(d, (x + 50, y + 100), title, 72, fill=c)
    for k, s in enumerate(CV_LINES):
        yy = y + 210 + k * 115
        text(d, (x + 50, yy), s, 58, fill=(GREY if grey else INK))
        if k < ticks:
            tick(d, x + w - 90, yy + 50, 34, c=(ORANGE if k == half else GREEN), half=(k == half))
    return x + w


def card_f0():
    im, d = canvas()
    x0, x1, dy = intern(d, 520, 380)
    d.rectangle([1000, dy - 560, 2200, dy - 20], fill=PAPER, outline=INK, width=6)
    text(d, (1050, dy - 470), 'Gemma 4 · CV', 72)
    for k, s in enumerate(['reads text in images', 'reads charts', 'uses tools', '… 9 skills listed']):
        yy = dy - 380 + k * 95
        text(d, (1050, yy), s, 56, fill=(INK if k < 3 else GREY))
    tick(d, 2080, dy - 330, 34)
    d.line([2150, dy - 360, 2320, dy - 560], fill=ORANGE, width=16)            # the pen, on line 1
    text(d, (1280, 1380), 'Google lists 9 skills · 7 tested, scored by code', 60, fill=ORANGE, anchor='ms')
    save(im, 'card-f0')


def card_cv():
    for step in (1, 2, 3, 4):
        im, d = canvas('Checking the intern\'s CV' if step < 4 else "Gemma 4's CV = its model card")
        x0, x1, dy = intern(d, 520, 420, grey=(step == 4))
        if step == 1:
            text(d, (1100, 520), 'brilliant, fast, sure', 72)
            text(d, (1100, 620), 'but: no tools (Part 14)', 64, fill=GREY, path=R)
        if step >= 2:
            g = step == 4
            cv_sheet(d, 1060, 230, 880, grey=g, ticks=(4 if step >= 3 else 0), half=0)
        if step >= 3:
            for k in range(4):
                yy = 230 + 210 + k * 115
                d.rectangle([2000, yy - 10, 2440, yy + 80], fill=(DONEFILL if step == 4 else (255, 255, 255)),
                            outline=(DONE if step == 4 else BLUE), width=5)
                text(d, (2030, yy + 58), 'test · key', 50, fill=(DONE if step == 4 else BLUE), path=R, anchor='ls')
            text(d, (2200, 1000), 'one test per line', 56, fill=(DONE if step == 4 else BLUE), anchor='ms')
            text(d, (2200, 1080), 'answer known first', 56, fill=(DONE if step == 4 else BLUE), anchor='ms')
        if step == 4:
            d.rounded_rectangle([960, 1150, 2500, 1330], 26, fill=ORANGEFILL, outline=ORANGE, width=7)
            text(d, (1730, 1268), 'model card: the page that lists what it can do', 54, fill=ORANGE, anchor='ms')
        save(im, f'card-cv-{step}')


MC = [('Thinking', 1), ('Long context', 0), ('Image understanding', 1), ('Video', 0), ('Interleaved input', 1),
      ('Function calling', 1), ('Coding', 1), ('Multilingual', 1), ('Audio', 1)]
MC_NOTE = {'Long context': '→ Part 16', 'Video': '= frames as images'}


def card_mc():
    for step in (1, 2):
        im, d = canvas('Gemma 4 model card: Core Capabilities')
        y = 220
        for name, tested in MC:
            on = step == 1 or tested
            d.rounded_rectangle([160, y, 1500, y + 112], 20, fill=(BLUEFILL if on else DONEFILL),
                                outline=(BLUE if on else DONE), width=5)
            text(d, (210, y + 80), name, 62, fill=(INK if on else DONE), anchor='ls')
            if step == 2 and tested:
                tick(d, 1600, y + 86, 30)
                text(d, (1720, y + 80), 'tested', 56, fill=GREEN, anchor='ls')
            if step == 2 and not tested:
                text(d, (1580, y + 80), MC_NOTE[name], 56, fill=DONE, anchor='ls')
            y += 126
        text(d, (2400, 200), '9 lines' if step == 1 else '7 tested', 72, fill=(INK if step == 1 else GREEN), anchor='ra')
        save(im, f'card-mc-{step}')


def card_loop():
    """P14's loop: your app (left), the model (right), your code (under the app); six functions offered."""
    for step in range(0, 5):
        im, d = canvas('A tool call: the model asks, your code runs it')
        flow_box(d, 160, 300, 460, 220, 'your app', True)
        flow_box(d, 1940, 300, 460, 220, 'model', True)
        flow_box(d, 160, 960, 460, 220, 'your code', step >= 3)
        for k in range(min(step, 4)):
            cur = k == step - 1
            c = INK if cur else DONE
            if k == 0:
                arrow(d, (640, 370), (1920, 370), cur, '1  these functions exist:', (1280, 340))
                text(d, (1280, 250), 'get_weather, multiply, convert_currency, +3', 50, fill=c, path=M, anchor='ms')
            elif k == 1:
                arrow(d, (1920, 470), (640, 470), cur, '2  call multiply(4821, 7293)', (1280, 560))
            elif k == 2:
                arrow(d, (390, 540), (390, 940), cur)
                text(d, (160, 1290), '3  4821 × 7293 = 35159553 → back', 60, fill=c, path=M, anchor='ls')
                arrow(d, (640, 1070), (1990, 540), cur)
            else:
                d.rounded_rectangle([1840, 640, 2420, 860], 24, fill=(GREENFILL if cur else DONEFILL),
                                    outline=(GREEN if cur else DONE), width=6)
                text(d, (2130, 780), '35,159,553', 64, fill=(GREEN if cur else DONE), path=M, anchor='ms')
                text(d, (2130, 920), '4  the answer', 56, fill=c, anchor='ms')
        save(im, f'card-loop-{step}')


ROWS = [('text in images', '✓'), ('charts: close, not exact', '~'), ('two images at once', '✓'), ('tool calls', '✓'),
        ('code', '✓'), ('three languages', '✓'), ('thinking (E4B)', '✓')]
ROW_H, ROW_GAP, ROW_Y = 112, 16, 220


def board_row(d, y, s, mark, cur, grey=False):
    fill = DONEFILL if (grey or not cur) else BLUEFILL
    d.rounded_rectangle([160, y, 2400, y + ROW_H], 20, fill=fill, outline=(BLUE if cur and not grey else DONE), width=5)
    mc = {'✓': GREEN, '~': ORANGE, '✗': ORANGE}.get(mark, DONE)
    if grey:
        mc = DONE
    if mark == '✓':
        tick(d, 250, y + 86, 26, c=mc)
    elif mark == '~':
        text(d, (250, y + 92), '~', 90, fill=mc, anchor='ms')
    elif mark == '✗':
        cross(d, 250, y + 56, 26, c=mc)
    text(d, (340, y + 80), s, 62, fill=(INK if cur and not grey else GREY), anchor='ls')


def card_board():
    """F13b: rows 1-6 = the six claims so far (row 1 holds text + charts); the bottom fifth stays empty (lower-third)."""
    six = [('images: text ✓ · charts ~ close, not exact', '~'), ('two images at once', '✓'), ('tool calls', '✓'),
           ('code', '✓'), ('three languages', '✓'), ('thinking (E4B)', '✓')]
    for n in range(1, 7):
        im, d = canvas('So far, E4B: six claims')
        for k in range(n):
            board_row(d, ROW_Y + k * (ROW_H + ROW_GAP), *six[k], cur=(k == n - 1))
        save(im, f'card-board-{n}')
    seven = six[:5] + [('thinking: E4B ✓ · 12B ran out of room (one run)', '~'),
                       ('audio: E2B/E4B ✓ · 12B tags ✗ (one run)', '~')]
    greys = [('long context → Part 16', ''), ('video: frames as images, not tested', '')]
    # F19: 0 = rows 1-6 back (none current); 1 row 1 (text); 2 row 1 (charts); 3 rows 2-5; 4 row 6; 5 + row 7; 6 + greys
    cur_of = {0: (), 1: (0,), 2: (0,), 3: (1, 2, 3, 4), 4: (5,), 5: (6,), 6: (7, 8)}
    for st in range(7):
        im, d = canvas('The CV check: seven claims, scored')
        rows = seven[:6] + ([seven[6]] if st >= 5 else []) + (greys if st >= 6 else [])
        for k, (s, mark) in enumerate(rows):
            board_row(d, ROW_Y + k * (ROW_H + ROW_GAP), s, mark, cur=(k in cur_of[st]), grey=(k >= 7))
        save(im, f'card-board19-{st}')


def card_audio():
    lines = [('the card: audio for E2B, E4B, 12B', 'up to 30 seconds of speech'),
             ('2 clips: a robot voice, script known (18 words)', 'and an audiobook, its first 30 s'),
             ('2 ways in: a chat message with the clip attached', "and Ollama's transcription address (for speech)")]
    for step in (1, 2, 3):
        im, d = canvas('Claim seven: audio')
        for k in range(step):
            cur = k == step - 1
            y = 240 + k * 360
            d.rounded_rectangle([160, y, 2400, y + 300], 24, fill=(BLUEFILL if cur else DONEFILL),
                                outline=(BLUE if cur else DONE), width=6)
            text(d, (220, y + 120), lines[k][0], 66, fill=(INK if cur else GREY), anchor='ls')
            text(d, (220, y + 230), lines[k][1], 58, fill=(GREY if cur else DONE), path=R, anchor='ls')
        save(im, f'card-audio-{step}')


def card_check():
    steps = [('1  the real text, typed by you', 'want.txt'),
             ('2  the model, thinking off, text only', 'ollama run --think=false TAG "… Output only the text. my.png" > got.txt'),
             ('3  compare: no output = every character matches', 'diff -wB want.txt got.txt')]
    for step in (1, 2, 3):
        im, d = canvas('Check it yourself')
        for k in range(step):
            cur = k == step - 1
            y = 220 + k * 330
            h = 290 if k < 2 else 400
            d.rounded_rectangle([120, y, 2440, y + h], 24, fill=(BLUEFILL if cur else DONEFILL),
                                outline=(BLUE if cur else DONE), width=6)
            text(d, (170, y + 100), steps[k][0], 64, fill=(INK if cur else GREY), anchor='ls')
            text(d, (170, y + 210), steps[k][1], (44 if k == 1 else 60), fill=(BLUE if cur else DONE), path=M,
                 anchor='ls')
            if k == 2:
                text(d, (170, y + 320), 'Windows: the same line, then  fc /w want.txt got.txt', 52,
                     fill=(GREY if cur else DONE), path=M, anchor='ls')
        save(im, f'card-check-{step}')


def card_end():
    im, d = canvas('The CV mostly holds up')
    x0, x1, dy = intern(d, 520, 420)
    d.rectangle([1060, 230, 2300, 900], fill=PAPER, outline=INK, width=6)
    text(d, (1110, 330), 'Gemma 4 · CV', 72)
    for k, (s, mark) in enumerate([('text in images', '✓'), ('charts', '~'), ('tools · code · languages', '✓'),
                                   ('audio (small tags)', '✓')]):
        yy = 440 + k * 110
        text(d, (1110, yy + 56), s, 58, anchor='ls')
        if mark == '✓':
            tick(d, 2160, yy + 56, 28)
        else:
            text(d, (2180, yy + 66), '~', 90, fill=ORANGE, anchor='ms')
    text(d, (1680, 1360), 'check the lines you depend on', 64, fill=BLUE, anchor='ms')
    save(im, 'card-end-1')
    im, d = canvas()
    text(d, (160, 200), 'Gemma Series · Part 15', 96)
    text(d, (160, 300), 'Ollama 0.40.16 · RTX 4060 8 GB · gemma4:e4b-it-q4_K_M, gemma4:12b-it-qat', 52, fill=GREY, path=R)
    d.rounded_rectangle([160, 460, 1200, 1100], 30, fill=BLUEFILL, outline=BLUE, width=8)
    text(d, (220, 600), 'Next: Part 16', 80, fill=BLUE)
    text(d, (220, 760), 'the small Gemma 4', 64)
    text(d, (220, 850), 'holds 128K tokens:', 64)
    text(d, (220, 940), 'can it find one fact?', 64)
    text(d, (160, 1250), 'Seven claims, scored by code: check it yourself.', 64, fill=INK, path=R)
    save(im, 'card-end')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    card_f0(); card_cv(); card_mc(); card_loop(); card_board(); card_audio(); card_check(); card_end()
    d13.ov_sub()
    print('cards:', len(os.listdir(OUT)))
    if d13.PROBLEMS:
        raise SystemExit('PROBLEMS: ' + '; '.join(d13.PROBLEMS))
