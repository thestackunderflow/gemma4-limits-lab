"""Gemma Series Part 13 cards (SCRIPT-13.md rev 3), the draw_fx10.py pattern: light, 2560 x 1440, line diagrams only
(no cartoon art: the F0 flash and the F3 desk are drawn as clean diagrams), each step adds, earlier steps stay and turn
grey. Text 44 px+. Numbers only from SCRIPT-13.md section 5 (NUMBERS).
  card-f0          F0 flash: the notepad, the lines just under its first few torn out, the last lines intact
  card-sizes-1..2  F2: the four sizes, then 7,584 words -> 9,644 tokens
  card-desk-1..4   F3: desk = graphics card memory, books = layers; the notepad; tokens written; "KV cache"
  card-window-1..3 F4: numbered lines; the bracket "context window = num_ctx"; the torn-out lines (front), end kept
  card-bar-1..2    F6: a bar of 9,644 tokens; the first 5 + the end lit (2,051), the middle grey with K-77 inside
  card-fix-1..3    F8: API options.num_ctx; OLLAMA_CONTEXT_LENGTH; (grey) or fail loudly: next
  ov-like          F10: RGBA lower-fifth band: like + subscribe for Part 14
  card-recap-1..2  F12: the desk again: a bigger notepad, books to the cabinet (system memory), the speed dial drops
  card-q8          F13: 16-bit -> 8-bit numbers (the notepad's handwriting smaller)
  card-rule-1..3   F15: the three rule lines, one at a time
  card-end         F16: Gemma Series Part 13, the Part 14 tile, the playlist (room left for the end screen)
Run in the draw image:  docker run --rm -v "<lab>:/lab" -w /lab cad3way-draw:1 python3 video/draw_p13.py"""
import os

from PIL import Image, ImageDraw, ImageFont

LAB = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(LAB, 'video', 'frames-p13')
FD = '/usr/share/fonts/truetype/dejavu/'
B, R, M = FD + 'DejaVuSans-Bold.ttf', FD + 'DejaVuSans.ttf', FD + 'DejaVuSansMono-Bold.ttf'
W, H = 2560, 1440
BG = (236, 239, 244)
INK, GREY = (31, 41, 55), (110, 120, 138)
DONE, DONEFILL = (160, 167, 178), (244, 246, 248)
BLUE, BLUEFILL = (37, 99, 235), (219, 234, 254)
ORANGE, ORANGEFILL = (234, 88, 12), (255, 237, 213)
GREEN, GREENFILL = (22, 128, 61), (220, 252, 231)
PAPER, PAPERLINE = (255, 253, 240), (203, 213, 225)
WOOD, WOODLINE = (222, 196, 160), (150, 110, 70)
MIN_PX = 44
PROBLEMS = []


def font(p, s):
    return ImageFont.truetype(p, s)


def text(d, xy, s, size=64, fill=INK, path=B, anchor='la'):
    if size < MIN_PX:
        PROBLEMS.append(f'{s!r}: {size} px')
    f = font(path, size)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)
    bb = d.textbbox(xy, s, font=f, anchor=anchor)
    if bb[0] < 0 or bb[2] > W or bb[1] < 0 or bb[3] > H:
        PROBLEMS.append(f'{s!r}: off the frame {bb}')
    return bb


def canvas(title=None):
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    if title:
        text(d, (120, 90), title, 76)
    return im, d


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, name + '.png'))


# --- the notepad (F0, F3, F4, F12, F13) -----------------------------------------------------------------------------
def notepad(d, x, y, w, rows, rh=62, torn=(), grey=False, nums=True, ink=INK, scribble=None, small=False):
    """A notepad with `rows` numbered lines. `torn`: line indexes torn out (drawn as a ragged gap, grey)."""
    edge = DONE if grey else INK
    d.rounded_rectangle([x, y, x + w, y + 70 + rows * rh + 30], 18, fill=PAPER, outline=edge, width=5)
    d.rectangle([x, y, x + w, y + 60], fill=(BLUEFILL if not grey else DONEFILL), outline=edge, width=5)
    for k in range(8):                                     # spiral rings
        cx = x + 60 + k * (w - 120) / 7
        d.ellipse([cx - 12, y - 18, cx + 12, y + 18], outline=edge, width=5)
    for i in range(rows):
        ly = y + 70 + i * rh + rh - 10
        if i in torn:
            d.rectangle([x + 4, ly - rh + 14, x + w - 4, ly + 2], fill=BG)
            pts = [(x + 4 + j * (w - 8) / 16, ly - rh + 14 + (8 if j % 2 else -6)) for j in range(17)]
            d.line(pts, fill=DONE, width=4)
            continue
        d.line([x + 30, ly, x + w - 30, ly], fill=PAPERLINE, width=3)
        if nums:
            text(d, (x + 30, ly - 8), f'{i + 1}', 44, fill=GREY, path=R, anchor='ls')
        if scribble and i < scribble:
            sw = (w - 180) * (0.55 if small else 1.0)
            for j in range(int(sw // 70)):
                d.line([x + 120 + j * 70, ly - 18, x + 120 + j * 70 + 46, ly - 18], fill=ink, width=8 if not small else 5)


def card_f0():
    im, d = canvas()
    notepad(d, 760, 160, 1040, 16, rh=66, torn=set(range(2, 11)), nums=False, scribble=16)
    text(d, (1280, 1395), 'the front of the prompt: torn out', 60, fill=ORANGE, anchor='ms')
    save(im, 'card-f0')


def card_sizes():
    for step in (1, 2):
        im, d = canvas('Gemma 4 sizes, and what context is counted in')
        g = INK if step == 1 else DONE
        rows = [('E2B, E4B', 'small', BLUE), ('12B', 'middle', BLUE), ('26B', 'big (Part 12)', BLUE)]
        for k, (a, b, c) in enumerate(rows):
            y = 260 + k * 150
            d.rounded_rectangle([200, y, 1500, y + 120], 20, fill=(BLUEFILL if step == 1 else DONEFILL),
                                outline=(c if step == 1 else DONE), width=5)
            text(d, (240, y + 82), a, 64, fill=g, anchor='ls')
            text(d, (760, y + 82), '= ' + b, 64, fill=g, anchor='ls')
        if step == 2:
            d.rounded_rectangle([200, 820, 2360, 1260], 24, fill=ORANGEFILL, outline=ORANGE, width=6)
            text(d, (260, 940), 'our test prompt: a novel + one line with a code', 56, fill=INK, path=R, anchor='ls')
            text(d, (260, 1080), '7,584 words (wc -w)', 80, anchor='ls')
            text(d, (1180, 1080), '→', 90, fill=ORANGE, anchor='ls')
            text(d, (1320, 1080), '9,644 tokens', 80, fill=ORANGE, anchor='ls')
            text(d, (260, 1200), 'token = a word piece', 56, fill=GREY, path=R, anchor='ls')
        save(im, f'card-sizes-{step}')


def desk(d, grey=False, books=6, notepad_rows=0, cabinet=False, scribble=0, label=False, bigpad=False):
    edge = DONE if grey else WOODLINE
    d.rectangle([160, 860, 1900, 940], fill=(WOOD if not grey else DONEFILL), outline=edge, width=6)
    d.line([240, 940, 240, 1320], fill=edge, width=14)
    d.line([1820, 940, 1820, 1320], fill=edge, width=14)
    text(d, (1030, 1010), 'desk = graphics card memory (8 GB)', 56, fill=(INK if not grey else DONE), anchor='ms')
    for k in range(books):                                         # books = layers, standing on the desk
        bx = 220 + k * 120
        d.rectangle([bx, 560, bx + 96, 860], fill=(BLUEFILL if not grey else DONEFILL),
                    outline=(BLUE if not grey else DONE), width=5)
    text(d, (220, 460), 'books = layers', 56, fill=(BLUE if not grey else DONE))
    if notepad_rows:
        w = 820 if bigpad else 560
        x = 1900 - w - 40
        notepad(d, x, 860 - 70 - notepad_rows * 52 - 30 - 10, w, notepad_rows, rh=52, nums=False, scribble=scribble,
                ink=ORANGE)
        if label:
            text(d, (x + w / 2, 860 - 70 - notepad_rows * 52 - 30 - 50), 'notepad = KV cache', 64, fill=ORANGE,
                 anchor='ms')
    if cabinet:
        d.rectangle([2040, 380, 2440, 1320], fill=DONEFILL, outline=INK, width=6)
        for k in range(4):
            d.rectangle([2080, 420 + k * 220, 2400, 600 + k * 220], outline=INK, width=4)
        text(d, (2240, 340), 'cabinet =', 52, fill=INK, anchor='ms')
        text(d, (2240, 1390), 'system memory', 52, fill=INK, anchor='ms')


def card_desk():
    for step in range(1, 5):
        im, d = canvas('Picture the desk (Parts 11 and 12)')
        desk(d, books=8 if step < 2 else 6, notepad_rows=(0 if step == 1 else 6), scribble=(0 if step < 3 else 5),
             label=(step == 4))
        if step == 3:
            text(d, (1500, 300), 'every token read is written down', 56, fill=ORANGE, path=R, anchor='ms')
        save(im, f'card-desk-{step}')


def card_window():
    for step in (1, 2, 3):
        im, d = canvas('The notepad has a fixed number of lines')
        torn = set(range(2, 9)) if step == 3 else set()
        notepad(d, 300, 220, 1100, 14, rh=70, torn=torn, scribble=14)
        if step >= 2:
            c = INK if step == 2 else DONE
            d.line([1480, 230, 1530, 230, 1530, 1300, 1480, 1300], fill=c, width=8)
            text(d, (1580, 700), 'context window', 72, fill=c)
            text(d, (1580, 800), '= num_ctx', 72, fill=(BLUE if step == 2 else DONE), path=M)
            text(d, (1580, 900), 'set when the model loads', 52, fill=(GREY if step == 2 else DONE), path=R)
        if step == 3:
            d.rounded_rectangle([1840, 400, 2480, 640], 20, fill=ORANGEFILL, outline=ORANGE, width=6)
            text(d, (1870, 495), 'not on the notepad', 52, fill=ORANGE, anchor='ls')
            text(d, (1870, 600), '= never seen', 60, fill=ORANGE, anchor='ls')
            text(d, (1460, 520), '← torn out', 56, fill=ORANGE, anchor='ls')
            text(d, (1460, 1240), '← the end stays', 52, fill=GREEN, anchor='ls')
        save(im, f'card-window-{step}')


def card_bar():
    for step in (1, 2):
        im, d = canvas('The prompt: 9,644 tokens')
        x0, x1, y0, y1 = 160, 2400, 560, 760
        d.rectangle([x0, y0, x1, y1], fill=(BLUEFILL if step == 1 else DONEFILL), outline=(BLUE if step == 1 else DONE),
                    width=6)
        text(d, (x0, y0 - 40), 'token 1', 52, fill=GREY, path=R, anchor='ls')
        text(d, (x1, y0 - 40), 'token 9,644', 52, fill=GREY, path=R, anchor='rs')
        k77 = (x0 + 30, y0 + 40)
        if step == 1:
            text(d, (x0 + 40, y1 + 110), 'line one: "The access code for the vault is K-77."', 52, fill=INK, path=R,
                 anchor='ls')
            text(d, (x1, y1 + 110), 'the question: last line', 52, fill=INK, path=R, anchor='rs')
        else:
            keep_end = x1 - (x1 - x0) * 2046 / 9644
            d.rectangle([x0, y0, x0 + 22, y1], fill=GREENFILL, outline=GREEN, width=5)
            d.rectangle([keep_end, y0, x1, y1], fill=GREENFILL, outline=GREEN, width=6)
            text(d, (x0 + 70, y0 + 125), 'K-77', 64, fill=DONE, anchor='ls')
            text(d, ((x0 + keep_end) / 2, y0 + 125), 'thrown away', 64, fill=DONE, anchor='ms')
            text(d, (x0, y1 + 110), 'kept: first 5', 56, fill=GREEN, anchor='ls')
            text(d, ((keep_end + x1) / 2, y1 + 110), 'kept: the end', 56, fill=GREEN, anchor='ms')
            d.rounded_rectangle([560, 1020, 2000, 1220], 20, fill=GREENFILL, outline=GREEN, width=6)
            text(d, (1280, 1150), 'read: 2,051 tokens in all', 72, fill=GREEN, anchor='ms')
        del k77
        save(im, f'card-bar-{step}')


def card_fix():
    lines = [('API', '"options": {"num_ctx": 16384}'), ('server', 'OLLAMA_CONTEXT_LENGTH=16384'),
             ('or', 'fail loudly: next')]
    for step in (1, 2, 3):
        im, d = canvas('The lasting fixes')
        for k in range(step):
            y = 300 + k * 300
            grey = (k == 2)
            d.rounded_rectangle([160, y, 2400, y + 220], 24, fill=(DONEFILL if grey else BLUEFILL),
                                outline=(DONE if grey else BLUE), width=6)
            text(d, (220, y + 140), lines[k][0], 64, fill=(DONE if grey else INK), anchor='ls')
            text(d, (620, y + 140), lines[k][1], 66, fill=(DONE if grey else BLUE), path=(R if grey else M),
                 anchor='ls')
        save(im, f'card-fix-{step}')


def ov_like():
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 1152, W, H], fill=(255, 255, 255, 236))
    d.line([0, 1152, W, 1152], fill=BLUE + (255,), width=6)
    d.rounded_rectangle([140, 1210, 640, 1380], 24, fill=BLUEFILL + (255,), outline=BLUE + (255,), width=6)
    text(d, (390, 1320), '👍 Like' if False else 'Like', 72, fill=BLUE, anchor='ms')
    d.rounded_rectangle([720, 1210, 1340, 1380], 24, fill=(204, 0, 0, 255))
    text(d, (1030, 1320), 'Subscribe', 72, fill=(255, 255, 255), anchor='ms')
    text(d, (1420, 1272), 'Next: Part 14', 56, fill=INK)
    text(d, (1420, 1350), 'five things Gemma 4 still gets wrong', 48, fill=GREY, path=R)
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, 'ov-like.png'))


def card_recap():
    for step in (1, 2):
        im, d = canvas('The desk again: a bigger notepad')
        desk(d, books=(8 if step == 1 else 5), notepad_rows=(6 if step == 1 else 8), scribble=(5 if step == 1 else 8),
             label=True, bigpad=(step == 2), cabinet=True)
        if step == 2:
            for k in range(3):                                         # the books that moved, in the cabinet
                d.rectangle([2100 + k * 100, 470, 2180 + k * 100, 580], fill=BLUEFILL, outline=BLUE, width=4)
            text(d, (2440, 200), 'books move to the cabinet →', 52, fill=ORANGE, anchor='rs')
            cx, cy, r = 640, 300, 110                                 # the speed dial
            d.arc([cx - r, cy - r, cx + r, cy + r], 180, 360, fill=INK, width=8)
            d.line([cx, cy, cx - 100, cy - 30], fill=ORANGE, width=10)
            text(d, (cx, cy + 70), 'slower', 52, fill=ORANGE, anchor='ms')
        save(im, f'card-recap-{step}')


def card_q8():
    im, d = canvas('q8_0: smaller handwriting on the notepad')
    notepad(d, 200, 300, 900, 10, rh=70, nums=False, scribble=10)
    notepad(d, 1460, 300, 900, 10, rh=70, nums=False, scribble=10, small=True)
    text(d, (650, 1200), '16-bit numbers (f16)', 64, anchor='ms')
    text(d, (1910, 1200), '8-bit numbers (q8_0)', 64, fill=BLUE, anchor='ms')
    text(d, (1280, 750), '→', 120, fill=ORANGE, anchor='ms')
    save(im, 'card-q8')


def card_rule():
    lines = ['1. raise num_ctx: eval count grows = cut', '2. num_ctx bigger than the prompt',
             '3. log: offloaded N/M (E2B, E4B, 12B)']
    for step in (1, 2, 3):
        im, d = canvas('Check it yourself')
        for k in range(step):
            y = 300 + k * 300
            cur = (k == step - 1)
            d.rounded_rectangle([160, y, 2400, y + 220], 24, fill=(BLUEFILL if cur else DONEFILL),
                                outline=(BLUE if cur else DONE), width=6)
            text(d, (220, y + 140), lines[k], 76, fill=(INK if cur else GREY), path=M, anchor='ls')
        save(im, f'card-rule-{step}')


def card_end():
    im, d = canvas()
    text(d, (160, 200), 'Gemma Series · Part 13', 96)
    text(d, (160, 300), 'Ollama 0.40.16 · RTX 4060 8 GB · gemma4:e4b-it-q4_K_M', 52, fill=GREY, path=R)
    d.rounded_rectangle([160, 460, 1200, 1100], 30, fill=BLUEFILL, outline=BLUE, width=8)
    text(d, (220, 600), 'Next: Part 14', 80, fill=BLUE)
    text(d, (220, 760), 'five things Gemma 4', 64)
    text(d, (220, 850), 'still gets wrong,', 64)
    text(d, (220, 940), 'and the fix for each', 64)
    text(d, (160, 1250), 'The notepad decides what the model sees.', 64, fill=INK, path=R)
    save(im, 'card-end')


if __name__ == '__main__':
    card_f0(); card_sizes(); card_desk(); card_window(); card_bar(); card_fix(); ov_like(); card_recap(); card_q8()
    card_rule(); card_end()
    print('cards:', sorted(os.listdir(OUT)))
    if PROBLEMS:
        raise SystemExit('PROBLEMS: ' + '; '.join(PROBLEMS))
