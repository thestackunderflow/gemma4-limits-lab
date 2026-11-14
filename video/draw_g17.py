"""g17 cards (SCRIPT-g17 rev 2 §4; HANDOVER-g17-render §3-4), the draw_p15.py pattern (draw_p13 helpers + P14's figure):
light, 2560 x 1440, clean line diagrams; the pen pal (F3, reused grey in F16) is the only illustrated art. 44 columns,
7 sentence lines or fewer per build (diagram tags apart), text inside the 5% safe area, highlight boxes thin outlines
(4 px at 1440p = 3 px at 1080p, never filled). Every number is read from out/g17 (results.json, requests.jsonl,
tools.jsonl) here, never typed; tests/test_draw_g17.py loads the files on its own and checks each card.
  card-penpal-1..3     F3: letters re-sent; Part 13's notepad; tokens, context window = num_ctx
  card-notepad-8k-1..5 F6: one 8,192 bar: menu; system + turn 1; turn 1's six requests (the tool loop); turns 2-4; turn 5
  card-tearout-1..3    F7 / Short S1: the full notepad; oldest whole messages torn out; instructions + newest kept
  card-ranges-1..3     F8 (replacing): temperature 0; temp-0 turns; Google sampling ranges
  card-test-1..2       F9: the turn-20 test (no result numbers); right part + the rule
  card-32k-1..3        F10: the lab temp-0 chat; 5 sampled chats; tokens per turn
  card-pin-1..2        F12: the spec pinned on the instructions page; the counts
  card-summary-1..3    F14: 8/8 summary vs pin; right parts; tokens per turn
  card-scoreboard-1..2 F15 (replacing): the five rows + "met by: none"; the two problems + the build counts
  card-penpal-recap    F16: the pen pal grey + the three checks
  card-yourturn        F17: the question (no answer anywhere)
  card-end             F18: Part 13 tile + the series tile (room for the end screen); the AI label is burnt in later
  ov-sub               F11: Like + Subscribe lower-third (no Next)
Run in the draw image:  docker run --rm -v "<lab>:/lab" -w /lab cad3way-draw:1 python3 video/draw_g17.py"""
import importlib.util
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('draw_p14', os.path.join(HERE, 'draw_p14.py'))
d14 = importlib.util.module_from_spec(_s)
_s.loader.exec_module(d14)
d13 = d14.d13
LAB = d13.LAB
G17 = os.path.join(LAB, 'out', 'g17')
OUT = os.path.join(LAB, 'video', 'frames-g17')
B, R, M = d13.B, d13.R, d13.M
INK, GREY, DONE, DONEFILL = d13.INK, d13.GREY, d13.DONE, d13.DONEFILL
BLUE, BLUEFILL, ORANGE, ORANGEFILL = d13.BLUE, d13.BLUEFILL, d13.ORANGE, d13.ORANGEFILL
PAPER, BG, W, H = d13.PAPER, d13.BG, d13.W, d13.H
RED = (200, 30, 30)
SAFE = (128, 72, W - 128, H - 72)
PROBLEMS = d13.PROBLEMS
TEXTS, HIGHLIGHTS, GREEN_USED, ART = {}, {}, {}, set()
_cur = [None]


def set_out(p):
    global OUT
    OUT = p


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


def load():
    r = json.load(open(os.path.join(G17, 'results.json')))
    by = {}
    for q in jl(os.path.join(G17, 'chats', 'drop-8k-t0', 'requests.jsonl')):
        by.setdefault(q['turn'], []).append(q['prompt_eval_count'])
    tc = lambda c: sum(x['result_chars'] for x in jl(os.path.join(G17, 'chats', c, 'tools.jsonl')))  # noqa: E731
    base = tc('drop-32k-t0')
    xs = [tc('fix-ctx32k-g%d' % k) for k in range(1, 6)]
    f = r['fix']
    chats = []
    for k in ('a_pin_8k', 'a_pin_16k', 'b_ctx_32k', 'c_summary_8k', 'c_summary_16k'):
        chats += [f[k]['t0']] + f[k]['reps']
    full = [c for c in chats if c['recall'] == 8]
    return {'r': r, 'by': by, 'x_lo': round(min(xs) / base, 1), 'x_hi': round(max(xs) / base, 1),
            'n_chats': len(chats), 'full': len(full), 'passed': sum(c['checker_pass'] is True for c in full),
            'nofile': sum(not c['stl'] for c in full),
            'wrong': sum(bool(c['stl']) and c['checker_pass'] is not True for c in full)}


D = load()
F = D['r']['fix']


def n(v):
    return f'{round(v):,}'


# --- recording helpers ---------------------------------------------------------------------------------------------
def start(name, title=None, art=False):
    _cur[0] = name
    TEXTS[name], HIGHLIGHTS[name] = [], []
    if art:
        ART.add(name)
    im = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(im)
    if title:
        t(d, (160, 110), title, 76, kind='title')
    return im, d


def t(d, xy, s, size=62, fill=INK, path=B, anchor='la', kind='line'):
    bb = d13.text(d, xy, s, size, fill=fill, path=path, anchor=anchor)
    TEXTS[_cur[0]].append({'s': s, 'bbox': bb, 'kind': kind})
    if len(s) > 44:
        PROBLEMS.append(f'{s!r}: over 44 columns')
    if bb[0] < SAFE[0] or bb[1] < SAFE[1] or bb[2] > SAFE[2] or bb[3] > SAFE[3]:
        PROBLEMS.append(f'{_cur[0]} {s!r}: outside the safe area {bb}')
    return bb


def hl(d, box, c=ORANGE, width=4):
    """A highlight: a thin outline, never filled."""
    d.rectangle(box, outline=c, width=width)
    HIGHLIGHTS[_cur[0]].append({'box': box, 'fill': None, 'width': width})


def lines(d, ls, y=1060, x=160, size=62, step=92, cur=None):
    """Sentence lines; those before index `cur` are grey (earlier steps)."""
    for k, s in enumerate(ls):
        t(d, (x, y + k * step), s, size, fill=(GREY if cur is not None and k < cur else INK))


def save(im):
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, _cur[0] + '.png'))


def arrow(d, a, b, c=INK, w=8):
    d.line([a, b], fill=c, width=w)
    import math
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for s in (2.6, -2.6):
        d.line([b, (b[0] + 34 * math.cos(ang + s), b[1] + 34 * math.sin(ang + s))], fill=c, width=w)


# --- the pen pal (F3, F16) -----------------------------------------------------------------------------------------
def envelope(d, x, y, w=300, h=180, c=INK, fill=PAPER):
    d.rectangle([x, y, x + w, y + h], fill=fill, outline=c, width=6)
    d.line([x, y, x + w / 2, y + h * 0.55, x + w, y], fill=c, width=5)


def penpal_scene(d, step, grey=False):
    c = DONE if grey else INK
    x0, x1, dy = d14.intern(d, 470, 330, grey=grey)                  # the pen pal at a desk; desk top y 790
    for k in range(5):                                                # the pile of every earlier letter
        envelope(d, 900 + k * 14, dy - 210 - k * 34, 300, 170, c=c, fill=(DONEFILL if grey else PAPER))
    if not grey and step == 1:
        envelope(d, 1720, 260, 300, 170, c=BLUE, fill=BLUEFILL)      # the new letter arriving
        arrow(d, (1700, 380), (1300, 520), BLUE)
    if step >= 2:
        d13.notepad(d, 1820, 300, 560, 7, grey=grey, nums=False)      # Part 13's notepad, fixed size
        if not grey:
            arrow(d, (1270, 560), (1790, 560), ORANGE if step == 2 else DONE)
    if step >= 3:
        d.rectangle([1730, 370, 1785, 804], fill=(DONEFILL if grey else ORANGEFILL), outline=c, width=5)
        for k in range(15):                                           # the ruler's ticks
            yy = 380 + k * 28
            d.line([1730, yy, 1730 + (34 if k % 5 == 0 else 18), yy], fill=c, width=4)


def card_penpal():
    labs = ['every earlier letter, sent again', "Part 13's notepad · fixed size",
            'counted in tokens (word pieces)', 'size = context window = num_ctx']
    upto = {1: 1, 2: 2, 3: 4}
    for step in (1, 2, 3):
        im, d = start(f'card-penpal-{step}', 'A pen pal with no memory', art=True)
        penpal_scene(d, step)
        cur = {1: 0, 2: 1, 3: 2}[step]
        lines(d, labs[:upto[step]], x=280, y=990, step=88, cur=cur)
        save(im)


def card_penpal_recap():
    im, d = start('card-penpal-recap', 'Three checks', art=True)
    penpal_scene(d, 3, grey=True)
    lines(d, ["count your menu's tokens first", "turn on Ollama's debug log to see drops",
              'check the part, not the reply'], x=280, y=990, step=100, size=66)
    save(im)


# --- the 8K notepad bar (F6) ---------------------------------------------------------------------------------------
BX0, BX1, BY0, BY1 = 160, 2400, 330, 470


def px(v, ctx=8192):
    return BX0 + (BX1 - BX0) * v / ctx


def card_notepad():
    s = D['r']['size']
    by = D['by']
    menu, t1, t1end = s['menu_tokens'], s['system_tools_turn1'], by[1][-1]
    t2, t3, t4, t5a = by[2][-1], by[3][-1], by[4][-1], by[5][0]
    segs = [(0, menu, BLUE, BLUEFILL), (menu, t1, ORANGE, ORANGEFILL), (t1, t1end, BLUE, BLUEFILL),
            (t1end, t4, BLUE, BLUEFILL)]
    texts = {1: [f'menu: {n(menu)} of 8,192 tokens', 'over half, before I type'],
             2: [f'system + menu + turn 1 = {n(t1)}'],
             3: [f'turn 1: {len(by[1])} requests, ends at {n(t1end)}',
                 'each tool result goes back with the list'],
             4: [f'turns 2, 3, 4: {n(t2)} → {n(t3)} → {n(t4)}', 'each small edit adds a few hundred'],
             5: [f'turn 5: first request {n(t5a)} still fits', 'then a tool result: no room',
                 'turn 1 torn out']}
    for step in range(1, 6):
        im, d = start(f'card-notepad-8k-{step}', 'An 8K notepad: 8,192 tokens')
        d.rectangle([BX0, BY0, BX1, BY1], fill=PAPER, outline=INK, width=6)
        for k, (a, b, c, fill) in enumerate(segs[:min(step, 4)]):
            curk = k == min(step, 4) - 1 and step < 5
            d.rectangle([px(a), BY0 + 6, px(b), BY1 - 6], fill=(fill if curk else DONEFILL),
                        outline=(c if curk else DONE), width=4)
        if step >= 4:
            for v in (t2, t3):
                d.line([px(v), BY0 + 6, px(v), BY1 - 6], fill=(BLUE if step == 4 else DONE), width=4)
        t(d, (BX0, BY1 + 20), '0', 48, fill=GREY, kind='tag')
        t(d, (BX1, BY1 + 20), '8,192', 48, fill=GREY, anchor='ra', kind='tag')
        if step == 3:                                     # the tool loop: Gemma ⇄ SolidCraft, the whole list each time
            for x, s_ in ((420, 'Gemma'), (1500, 'SolidCraft')):
                d.rounded_rectangle([x, 640, x + 560, 800], 24, fill=BLUEFILL, outline=BLUE, width=6)
                t(d, (x + 280, 745), s_, 60, fill=BLUE, anchor='ms', kind='tag')
            arrow(d, (990, 670), (1490, 670))
            t(d, (1240, 650), 'command', 50, fill=INK, anchor='ms', kind='tag')
            arrow(d, (1490, 780), (990, 780))
            t(d, (1240, 870), 'tool result + whole list', 50, fill=INK, anchor='ms', kind='tag')
        if step == 5:
            d.rectangle([px(t4), BY0 + 6, BX1 - 6, BY1 - 6], fill=(255, 226, 226), outline=RED, width=4)
            t(d, (BX1 - 20, BY0 - 20), 'no room', 56, fill=RED, anchor='rs', kind='tag')
            hl(d, [px(menu) - 4, BY0 - 4, px(t1end) + 4, BY1 + 4], c=RED)
            d.line([px(menu), BY0, px(t1end), BY1], fill=RED, width=4)
            d.line([px(menu), BY1, px(t1end), BY0], fill=RED, width=4)
        lines(d, texts[step], y=(1000 if step == 3 else 760), step=92)
        save(im)


# --- the tear-out (F7, Short S1) -----------------------------------------------------------------------------------
STRIPS = ['instructions page (system)', 'turn 1: the spec', "turn 1's tool results", 'turn 2', '…',
          'newest message']


def card_tearout():
    labs = {1: ['the notepad is full'], 2: ['oldest whole messages torn out'],
            3: ['instructions kept while they fit', 'newest message kept']}
    for step in (1, 2, 3):
        im, d = start(f'card-tearout-{step}', 'When the notepad is full')
        d.rounded_rectangle([160, 230, 1260, 1000], 18, fill=PAPER, outline=INK, width=6)
        for k, s in enumerate(STRIPS):
            torn = step >= 2 and k in (1, 2)
            x = 1460 if torn else 210
            y = 260 + k * 122
            fill = DONEFILL if torn else (BLUEFILL if step == 3 and k in (0, 5) else (255, 255, 255))
            d.rectangle([x, y, x + 1000, y + 100], fill=fill, outline=(DONE if torn else INK), width=5)
            if torn:                                                   # the ragged torn edge
                pts = [(x + j * 1000 / 12, y + 100 + (10 if j % 2 else -6)) for j in range(13)]
                d.line(pts, fill=DONE, width=5)
            t(d, (x + 30, y + 72), s, 54, fill=(DONE if torn else INK), anchor='ls', kind='tag')
            if step == 3 and k in (0, 5):
                hl(d, [x - 8, y - 8, x + 1008, y + 108])
        if step >= 2:
            arrow(d, (1230, 470), (1440, 470), ORANGE)
        ls = labs[1] + (labs[2] if step >= 2 else []) + (labs[3] if step >= 3 else [])
        lines(d, ls, y=1040, step=80, cur=len(ls) - len(labs[step]))
        save(im)


# --- ranges (F8, replacing builds) ---------------------------------------------------------------------------------
def card_ranges():
    dr = D['r']['drop']
    r8, r16 = F['baseline_8k']['reps_turn1_gone'], F['baseline_16k']['reps_turn1_gone']
    builds = {1: ['temperature 0 = always the likeliest word', 'same inputs, same chat'],
              2: ['temperature 0 · turn 1 gone at turn:', f"8K (8,192): {dr['8k']['turn1_gone_turn']}",
                  f"16K (16,384): {dr['16k']['turn1_gone_turn']}", '32K (32,768): not by turn 20'],
              3: ["Google's sampling (1.0 / 0.95 / 64)", '5 runs each · turn 1 gone at turns:',
                  f'8K: {min(r8)}-{max(r8)}', f'16K: {min(r16)}-{max(r16)}']}
    for step in (1, 2, 3):
        im, d = start(f'card-ranges-{step}', 'When does turn 1 leave?')
        lines(d, builds[step], y=300, step=130, size=72)
        save(im)


# --- the turn-20 test (F9) -----------------------------------------------------------------------------------------
def card_test():
    a = ['turn 20: rebuild my first spec,', 'export it, list it', '8 facts: BRK-17 · PETG · 60 · 40 · 5',
         'two holes · 4.5 mm · 36 apart']
    b = ['right part = checker passes + all 8 facts', 'a fix must be right at temp 0', 'and in 4 of 5 sampled runs']
    for step in (1, 2):
        im, d = start(f'card-test-{step}', 'The turn-20 test')
        ls = a + (b if step == 2 else [])
        lines(d, ls, y=280, step=128, size=68, cur=(len(a) if step == 2 else None))
        save(im)


# --- 32K (F10) -----------------------------------------------------------------------------------------------------
def card_32k():
    f = F['b_ctx_32k']
    reps = f['reps_turn1_gone']
    lost = sum(x is not None for x in reps)
    builds = [['lab temp-0 chat: right part', 'not the filmed one'],
              [f'sampled: {lost} of {len(reps)} lost turn 1', 'each filled 32K',
               f"{D['x_lo']}x to {D['x_hi']}x the tool output"],
              [f"{n(f['mean_tokens_per_turn_all'])} tokens sent per turn",
               f"8K, no fix: {n(F['baseline_8k']['mean_tokens_per_turn_all'])}"]]
    for step in (1, 2, 3):
        im, d = start(f'card-32k-{step}', 'Fix one: 32K, six lab chats')
        ls = sum(builds[:step], [])
        lines(d, ls, y=300, step=128, size=68, cur=len(ls) - len(builds[step - 1]))
        save(im)


# --- pin (F12) -----------------------------------------------------------------------------------------------------
def card_pin():
    a8, a16 = F['a_pin_8k'], F['a_pin_16k']
    for step in (1, 2):
        im, d = start(f'card-pin-{step}', 'Fix two: pin the spec')
        g = step == 2
        x, y = (160, 260) if g else (700, 260)
        d.rectangle([x, y, x + 1060, y + 640], fill=(DONEFILL if g else PAPER), outline=(DONE if g else INK), width=6)
        t(d, (x + 40, y + 90), 'system instructions', 60, fill=(DONE if g else INK), kind='tag')
        d.rectangle([x + 120, y + 200, x + 960, y + 520], fill=(DONEFILL if g else ORANGEFILL),
                    outline=(DONE if g else ORANGE), width=6)
        d.ellipse([x + 520, y + 170, x + 560, y + 210], fill=(DONE if g else RED))
        t(d, (x + 160, y + 310), 'spec: BRK-17 · PETG', 54, fill=(DONE if g else INK), kind='tag')
        t(d, (x + 160, y + 410), '60 x 40 x 5 · 2 holes', 54, fill=(DONE if g else INK), kind='tag')
        if step == 1:
            lines(d, ['the spec, pinned on the instructions page'], y=1060)
        else:
            right = a8['right_total'] + a16['right_total']
            lines(d, [f"8K: {a8['recall8_chats']} of 6 with 8/8", f"{a8['length_stops']} replies stopped short",
                      '(6 chats)', f"16K: {a16['recall8_chats']} of 6 with 8/8", f'right parts: {right} of 12'],
                  x=1320, y=330, step=120, size=60)
        save(im)


# --- summary (F14) -------------------------------------------------------------------------------------------------
def card_summary():
    s16, p16 = F['c_summary_16k'], F['a_pin_16k']
    right = F['c_summary_8k']['right_total'] + s16['right_total']
    builds = [['8/8 at turn 20 (16K):', f"summary {s16['recall8_chats']} of 6 · pin {p16['recall8_chats']} of 6",
               'one chat apart'],
              [f'right parts: {right} of 12'],
              [f"tokens sent per turn (16K): {n(s16['mean_tokens_per_turn_all'])}",
               f"32K: {n(F['b_ctx_32k']['mean_tokens_per_turn_all'])}"]]
    for step in (1, 2, 3):
        im, d = start(f'card-summary-{step}', 'Fix three: a summary every 5 turns')
        ls = sum(builds[:step], [])
        lines(d, ls, y=300, step=128, size=68, cur=len(ls) - len(builds[step - 1]))
        save(im)


# --- scoreboard (F15, replacing builds) ----------------------------------------------------------------------------
ROWS = [('pin, 8K', 'a_pin_8k'), ('pin, 16K', 'a_pin_16k'), ('bigger window, 32K', 'b_ctx_32k'),
        ('summary, 8K', 'c_summary_8k'), ('summary, 16K', 'c_summary_16k')]
COLS = [160, 1000, 1500, 1980]


def card_scoreboard():
    im, d = start('card-scoreboard-1', 'Judged at turn 20 · 6 chats each')
    for x, h in zip(COLS, ('fix', 'right parts', '8/8 facts', 'tokens/turn')):
        t(d, (x, 270), h, 54, fill=GREY, kind='tag')
    for k, (name, key) in enumerate(ROWS):
        y = 340 + k * 128
        d.rounded_rectangle([140, y, 2420, y + 110], 18, fill=(255, 255, 255), outline=DONE, width=4)
        f = F[key]
        for x, s in zip(COLS, (name, f"{f['right_total']} of 6", f"{f['recall8_chats']} of 6",
                               n(f['mean_tokens_per_turn_all']))):
            t(d, (x + 20, y + 78), s, 58, anchor='ls', kind='tag')
    t(d, (160, 1100), 'my rule · met by: none', 66)
    save(im)
    im, d = start('card-scoreboard-2', 'Two problems')
    lines(d, ['memory: the notepad size sets the turn',
              f"build: {D['full']} of {D['n_chats']} listed every fact",
              f"{D['passed']} passed · {D['nofile']} no file · {D['wrong']} wrong"], y=330, step=150, size=74)
    t(d, (160, 1150), 'counted by code from results.json', 54, fill=GREY)
    save(im)


# --- your turn (F17), end (F18), the lower-third (F11) -------------------------------------------------------------
def card_yourturn():
    im, d = start('card-yourturn', 'Your turn')
    lines(d, ['Guess first:', 'will turn 3 SEND more tokens', 'than turn 2?', 'And why?'], y=330, step=170,
          size=96)
    save(im)


def card_end():
    im, d = start('card-end', 'Gemma Series')
    t(d, (160, 210), 'Gemma 4 E4B · Ollama · SolidCraft · 8 GB', 52, fill=GREY, path=R, kind='tag')
    for x, a, b, c in ((160, 'Part 13', 'the notepad fills up', 'and gets cut'),
                       (1340, 'The Gemma series', 'every part, in order', 'one playlist')):
        d.rounded_rectangle([x, 380, x + 1060, 1000], 30, fill=BLUEFILL, outline=BLUE, width=8)
        t(d, (x + 60, 520), a, 80, fill=BLUE, kind='tag')
        t(d, (x + 60, 680), b, 62, kind='tag')
        t(d, (x + 60, 780), c, 62, kind='tag')
    save(im)


def ov_sub():
    _cur[0] = 'ov-sub'
    TEXTS['ov-sub'], HIGHLIGHTS['ov-sub'] = [], []
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([140, 1186, 1700, 1346], 28, fill=(255, 255, 255, 236), outline=BLUE + (255,), width=5)
    d.rounded_rectangle([170, 1210, 470, 1322], 22, fill=BLUEFILL + (255,), outline=BLUE + (255,), width=5)
    t(d, (320, 1290), 'Like', 60, fill=BLUE, anchor='ms', kind='tag')
    d.rounded_rectangle([500, 1210, 1010, 1322], 22, fill=(204, 0, 0, 255))
    t(d, (755, 1290), 'Subscribe', 60, fill=(255, 255, 255), anchor='ms', kind='tag')
    t(d, (1040, 1290), 'local models, measured', 50, fill=INK, anchor='ls', kind='tag')
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, 'ov-sub.png'))


def short_tearout():
    """Short S1: the tear-out at the Short's view aspect (1.125; 2160 x 1920, shown at 1080 x 960): the notepad's
    strips on the left, the two oldest torn out whole on the right, two lines. No numbers."""
    _t2 = lambda d_, xy, s_, size, fill=INK, anchor='la': d_.text(xy, s_, font=d13.font(B, size), fill=fill, anchor=anchor)  # noqa: E731,E501  (its own 2160 x 1920 frame)
    im = Image.new('RGB', (2160, 1920), BG)
    d = ImageDraw.Draw(im)
    _cur[0] = 'short-tearout'
    TEXTS['short-tearout'], HIGHLIGHTS['short-tearout'] = [], []
    d.rounded_rectangle([60, 120, 1160, 1020], 18, fill=PAPER, outline=INK, width=8)
    for k, s_ in enumerate(STRIPS):
        torn = k in (1, 2)
        x, y = (1220 if torn else 100), 160 + k * 140
        d.rectangle([x, y, x + 880 if torn else x + 1020, y + 116], fill=(DONEFILL if torn else (255, 255, 255)),
                    outline=(DONE if torn else INK), width=6)
        if torn:
            d.line([(x + j * 880 / 10, y + 116 + (12 if j % 2 else -8)) for j in range(11)], fill=DONE, width=6)
        _t2(d, (x + 30, y + 84), s_, 56, fill=(DONE if torn else INK), anchor='ls')
    arrow(d, (1130, 440), (1210, 440), ORANGE)
    _t2(d, (1080, 1300), 'oldest whole messages torn out', 84, anchor='ms')
    _t2(d, (1080, 1440), 'instructions + newest kept', 84, fill=GREY, anchor='ms')
    os.makedirs(OUT, exist_ok=True)
    im.save(os.path.join(OUT, 'short-tearout.png'))


def build_all():
    card_penpal(); card_notepad(); card_tearout(); card_ranges(); card_test(); card_32k(); card_pin()
    card_summary(); card_scoreboard(); card_penpal_recap(); card_yourturn(); card_end(); ov_sub()
    short_tearout()


if __name__ == '__main__':
    build_all()
    print('cards:', len(os.listdir(OUT)))
    if PROBLEMS:
        raise SystemExit('PROBLEMS: ' + '; '.join(PROBLEMS))
