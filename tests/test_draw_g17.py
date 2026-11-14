"""g17 cards (video/draw_g17.py, SCRIPT-g17 rev 2 §4, HANDOVER-g17-render §3-4): light theme, 44 columns, 7 lines or
fewer per build, text inside the 5% safe area, highlight boxes thin outlines (no fill), every number on a card equals
results.json / requests.jsonl / tools.jsonl (loaded here, independently of the module), no "winner" / "best" / "works".
Run: docker run --rm -v <lab>:/lab -w /lab cad3way-draw:1 python3 -m pytest -q tests/test_draw_g17.py"""
import importlib.util
import json
import os
import re

import pytest

LAB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
G17 = os.path.join(LAB, 'out', 'g17')


def jl(p):
    return [json.loads(x) for x in open(p) if x.strip()]


@pytest.fixture(scope='module')
def mod(tmp_path_factory):
    spec = importlib.util.spec_from_file_location('draw_g17', os.path.join(LAB, 'video', 'draw_g17.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.set_out(str(tmp_path_factory.mktemp('frames-g17')))
    m.build_all()
    return m


@pytest.fixture(scope='module')
def res():
    return json.load(open(os.path.join(G17, 'results.json')))


EXPECTED = (['card-penpal-%d' % k for k in (1, 2, 3)] + ['card-notepad-8k-%d' % k for k in range(1, 6)] +
            ['card-tearout-%d' % k for k in (1, 2, 3)] + ['card-ranges-%d' % k for k in (1, 2, 3)] +
            ['card-test-1', 'card-test-2'] + ['card-32k-%d' % k for k in (1, 2, 3)] + ['card-pin-1', 'card-pin-2'] +
            ['card-summary-%d' % k for k in (1, 2, 3)] + ['card-scoreboard-1', 'card-scoreboard-2'] +
            ['card-penpal-recap', 'card-yourturn', 'card-end', 'ov-sub'])


def test_every_card_exists_and_is_light(mod):
    from PIL import Image
    for n in EXPECTED:
        p = os.path.join(mod.OUT, n + '.png')
        assert os.path.exists(p), n
        im = Image.open(p).convert('RGB')
        assert im.size == (2560, 1440)
        if n != 'ov-sub':
            assert sum(im.getpixel((20, 20))) / 3 > 200, n + ' not light'


def test_no_problems(mod):
    assert mod.PROBLEMS == []


def test_44_columns_safe_area_and_7_lines(mod):
    for n, items in mod.TEXTS.items():
        lines = [t for t in items if t['kind'] == 'line']
        assert len(lines) <= 7, (n, len(lines))
        for t in items:
            assert len(t['s']) <= 44, (n, t['s'])
            x0, y0, x1, y1 = t['bbox']
            assert x0 >= 128 and x1 <= 2560 - 128 and y0 >= 72 and y1 <= 1440 - 72, (n, t['s'], t['bbox'])


def test_highlights_are_thin_outlines(mod):
    for n, hs in mod.HIGHLIGHTS.items():
        for h in hs:
            assert h['fill'] is None and h['width'] <= 5, (n, h)


def test_no_banned_words(mod):
    for n, items in mod.TEXTS.items():
        for t in items:
            assert not re.search(r'\b(winner|winning|best|works?)\b', t['s'], re.I), (n, t['s'])


def allowed(res):
    a = set()

    def walk(v):
        if isinstance(v, bool):
            return
        if isinstance(v, (int, float)):
            a.add(round(float(v), 1))
            a.add(float(round(v)))     # a mean shown as a whole number (17,192.8 -> 17,193)
        elif isinstance(v, str) and re.fullmatch(r'\d+', v):
            a.add(float(v))
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)
    walk(res)
    for q in jl(os.path.join(G17, 'chats', 'drop-8k-t0', 'requests.jsonl')):
        a.add(float(q['prompt_eval_count']))
    a |= {8.0, 16.0, 32.0}                      # 8K / 16K / 32K window names (num_ctx 8192 / 16384 / 32768)
    a |= {17.0, 60.0, 40.0, 5.0, 4.5, 36.0}      # the spec facts: BRK-17, 60 x 40 x 5, 4.5 mm holes, 36 apart
    a |= {1.0, 0.95, 64.0}                       # lab/g17run.py SAMPLING google: temperature 1.0, top_p 0.95, top_k 64
    a |= {13.0, 30.0, 12.0}                      # Part 13; 30 fix chats (5 arms x 6); 12 = 2 window sizes x 6 chats
    t = lambda c: sum(x['result_chars'] for x in jl(os.path.join(G17, 'chats', c, 'tools.jsonl')))  # noqa: E731
    b = t('drop-32k-t0')
    xs = [t('fix-ctx32k-g%d' % k) for k in range(1, 6)]
    a |= {round(min(xs) / b, 1), round(max(xs) / b, 1)}
    return a


def test_every_number_comes_from_the_lab(mod, res):
    ok = allowed(res)
    for n, items in mod.TEXTS.items():
        for t in items:
            for m in re.findall(r'\d[\d,]*(?:\.\d+)?', t['s']):
                v = float(m.replace(',', ''))
                assert round(v, 1) in ok, (n, t['s'], m)


def fix_rows(res):
    f = res['fix']
    return [(k, f[k]['right_total'], f[k]['recall8_chats'], round(f[k]['mean_tokens_per_turn_all']))
            for k in ('a_pin_8k', 'a_pin_16k', 'b_ctx_32k', 'c_summary_8k', 'c_summary_16k')]


def test_scoreboard_rows_equal_results(mod, res):
    s = ' | '.join(t['s'] for t in mod.TEXTS['card-scoreboard-1'])
    for k, right, r8, tok in fix_rows(res):
        assert f'{right} of 6' in s and f'{r8} of 6' in s and f'{tok:,}' in s, k


def test_build_counts_equal_results(mod, res):
    f = res['fix']
    chats = []
    for k in ('a_pin_8k', 'a_pin_16k', 'b_ctx_32k', 'c_summary_8k', 'c_summary_16k'):
        chats += [f[k]['t0']] + f[k]['reps']
    assert len(chats) == 30
    full = [c for c in chats if c['recall'] == 8]
    passed = [c for c in full if c['checker_pass'] is True]
    nofile = [c for c in full if not c['stl']]
    wrong = [c for c in full if c['stl'] and c['checker_pass'] is not True]
    s = ' '.join(t['s'] for t in mod.TEXTS['card-scoreboard-2'])
    assert f'{len(full)} of 30' in s and f'{len(passed)} passed' in s
    assert f'{len(nofile)} no file' in s and f'{len(wrong)} wrong' in s


def test_notepad_numbers_equal_requests(mod, res):
    by = {}
    for q in jl(os.path.join(G17, 'chats', 'drop-8k-t0', 'requests.jsonl')):
        by.setdefault(q['turn'], []).append(q['prompt_eval_count'])
    s = ' '.join(t['s'] for n in mod.TEXTS if n.startswith('card-notepad') for t in mod.TEXTS[n])
    for v in [res['size']['menu_tokens'], res['size']['system_tools_turn1'], by[1][-1], by[2][-1], by[3][-1],
              by[4][-1], by[5][0]]:
        assert f'{v:,}' in s, v
    assert f'{len(by[1])}' in s or 'six requests' in s


def test_the_fix_cards_say_what_results_say(mod, res):
    f = res['fix']
    pin = ' '.join(t['s'] for t in mod.TEXTS['card-pin-2'])
    assert f"{f['a_pin_8k']['recall8_chats']} of 6 with 8/8" in pin and f"{f['a_pin_8k']['length_stops']} replies" in pin
    assert f"{f['a_pin_16k']['recall8_chats']} of 6 with 8/8" in pin and '0 of 12' in pin
    summ = ' '.join(t['s'] for n in ('card-summary-1', 'card-summary-2', 'card-summary-3') for t in mod.TEXTS[n])
    assert f"summary {f['c_summary_16k']['recall8_chats']} of 6" in summ and f"pin {f['a_pin_16k']['recall8_chats']} of 6" in summ
    assert f"{round(f['c_summary_16k']['mean_tokens_per_turn_all']):,}" in summ
    k32 = ' '.join(t['s'] for n in ('card-32k-1', 'card-32k-2', 'card-32k-3') for t in mod.TEXTS[n])
    assert f"{round(f['b_ctx_32k']['mean_tokens_per_turn_all']):,}" in k32
    assert f"{round(f['baseline_8k']['mean_tokens_per_turn_all']):,}" in k32
    rng = ' '.join(t['s'] for n in ('card-ranges-2', 'card-ranges-3') for t in mod.TEXTS[n])
    d = res['drop']
    assert f"{d['8k']['turn1_gone_turn']}" in rng and f"{d['16k']['turn1_gone_turn']}" in rng
    r8, r16 = f['baseline_8k']['reps_turn1_gone'], f['baseline_16k']['reps_turn1_gone']
    assert f'{min(r8)}-{max(r8)}' in rng and f'{min(r16)}-{max(r16)}' in rng


def test_card_test_carries_no_result_numbers(mod):
    s = ' '.join(t['s'] for n in ('card-test-1', 'card-test-2') for t in mod.TEXTS[n])
    for bad in ('34.5', '24.0', '7 of 8', '8 of 8', '68,259'):
        assert bad not in s


def test_scoreboard_has_no_green_and_says_none(mod):
    s = ' '.join(t['s'] for t in mod.TEXTS['card-scoreboard-1'])
    assert 'met by: none' in s
    assert mod.GREEN_USED.get('card-scoreboard-1', 0) == 0


def test_only_the_penpal_is_illustrated(mod):
    assert mod.ART == {'card-penpal-1', 'card-penpal-2', 'card-penpal-3', 'card-penpal-recap'}
