# Part 15 filming takes (13 Nov 2026, owner GO)

Shot list: `Refream-Canvas/inputs/video-plans/2026-11-10-gemma-4x/SHOTLIST-15.md` rev 2 (19 shots after the F18 cut; V15
and V15b not filmed). Same kit and method as Part 14 (`out/p14-film/TAKES.md`): `film13:1` image, `scripts/film13/lib.sh`
helpers, Xvfb 1920x1080, 30 fps, CRF 14; xterm DejaVu Sans Mono 30 running tmux; prompt `$ `; full window 2.5 s before
the first command, browser 3 s+. Takes run by `scripts/film15/run.sh <shot>` (copy of `scripts/film14/run.sh` writing to
`out/p15-film`, container `film15`): drops the WSL page cache, checks Windows free RAM >= 4 GB, foreground, one take per
call, server log read ONCE after the take (`docker logs --since/--until`, no follower left running).
`scripts/film15/ff.sh` = film14 Firefox prelude plus `f_term` (the film13 xterm opened over the browser in the same
recording, used by V1 and V5) and `r` (types a command read from a quoted heredoc, so jq quoting stays literal).

Server: `gemma4-limits-ollama` as left by the lab, checked before the shoot: memory cap **12g** (12884901888, the
`lab.sh up f16` default; not 16g), 0.40.16, FLASH_ATTENTION 1, KV f16, KEEP_ALIVE 0, MAX_LOADED_MODELS 1,
NUM_PARALLEL 1, DEBUG 1. No 12B loaded; every model take E4B. Free RAM at each model take (after the cache drop):
V1 8.81, V5 4.66 (E4B still warm from V1), V8 7.27, V13 7.23, V16 7.01 GB; after: 4.16, 7.03, 6.95, 3.56, 3.59 GB.
After V13 (3.56 GB, E4B warm for its 2 m keep_alive) the shoot waited until the model unloaded (3.82 GB at 08:11:31,
6.98 GB at 08:13:31) before V16. No browser or owner app closed.

Dry run (no recording, `--network none`, a stand-in lib that evals each typed command and skips the model calls):
every jq / grep command of every take ran first; all outputs matched the shot list's "Must be visible" values; no
command needed a fix (V6's worst-off one-liner prints 3).

Per take folder: `screen.mp4` (not committed; sha256 below), `pane-0.txt` / `pane-0.before-clear-K.txt` (terminal
text, the verification copy), `events.jsonl`, `record.json`, `cursor.jsonl`, `end.png`, `probe-loaded.png` (browser
takes), `nvidia-start.txt` (model takes), `reply.json` (V1, V5), `reply1.json` (V8 step 1), `got.txt` (V16).
`server-live-<shot>.log` = the server lines of that take's window (empty for no-model takes). Model load metadata carries the publisher's build path (`/Users/...` imatrix keys), as P14; not on screen.

Paths: the reuse takes `cd /lab/out/p15` first (as P14 C3) and then name `can.jsonl` etc. without the folder; the
filters are the shot list's. Small additions: V5 shows the drawn values with
`jq -c 'select(.model=="e4b" and .item=="chart04" and .temperature==0) | .want'`; V10's 12B count line is
`select(.section=="coding") | [.model, .seed, .result]` from can-summary; V11's count line the same for multilingual;
V12's seconds line is `select(.model=="e4b" and .section=="thinking" and .temperature==0) | .result`; V14b's e4b tail
is the `/api/chat images field` row's `.answer[-60:]`.

## C0 (no camera): request files

Built by `scripts/film15/c0.py` in the runner image from `lab/tasks.py` and `lab/images.py` (prompt text, chart keys and
OCR text from the lab code, called on a scratch folder; the image bytes are the saved `out/p15/images/ocr_00.png` and
`chart_04.png`, never re-drawn; `git status out/p15/images` clean after). Body = `lab/p15.py Session.chat`:
`stream false`, `think false`, `options {temperature 0, seed 42, num_predict 1024, num_ctx 8192}`, keep_alive `2m` (lab
`15m`). tools-e4b.json carries all 6 `tasks.TOOLS`. json-person.json not built (F18 cut). sha256 (16):
ocr00.json d1ba8fce0c204456; chart04.json 0dc5a3db5e765f28; tools-e4b.json 59ad913c21a29724; want-ocr00.txt
03ecc44d3b3765cb; send-result.sh 5c6c5fefa760ad28 (P14's script with /film/tools-e4b.json).

## Takes

| Shot | Folder | Dur s | sha256 (16) | Visible / verified vs lab row |
|---|---|---|---|---|
| V0 | (P13 K1-K3) | - | a96ddb08159f2f8e | reused, not refilmed |
| V1 | V1 | 27.6 | c6eb85fa076a4b54 | Firefox ocr_00.png (Privacy Notice bar at top, as P14 C13); `gemma4:e4b-it-q4_K_M`; reply **"$ docker compose up -d" / "Error response from daemon: port 8080 is already allocated"**, byte-identical to the lab ocr00 row (cmp). Fresh load 9.1 s, eval_count 22. VRAM before 1490 MiB |
| V2 | V2 | 25.7 | 4b0d26b2730509a6 | want = answer (folded at 44), `"passed":true`; 6 lines: seed 42 [10,10], 1001-1004 [10,10], 1005 [9,10] |
| V3 | V3 | 37.2 | 5145a534dc6c631f | ocr00-ocr09 `true` (10); `{"seed":1005,"want":" (OOMKilled)","answer":" (00MKilled)"}`; 12b-qat six [10,10] |
| V5 | V5 | 22.9 | 6033dc2a5df5844b | Firefox chart_04.png "Tickets closed" Q1-Q4; reply ```json {"Q1": 10, "Q2": **93**, "Q3": 40, "Q4": **92**}```, byte-identical to the lab chart04 row (warm model, as the lab row); drawn values `{"Q1":10,"Q2":95,"Q3":40,"Q4":95}` |
| V6 | V6 | 37.7 | e2908a25a4954a46 | e4b [2,5] then 2,2,1,2,1; 12b-qat [3,5] then 4,3,4,5,4; `{"rows":60,"within5":60}`; worst **3** |
| V7 | V7 | 12.1 | 6d0d5f5a47dc83d5 | Firefox pair_01_a.png "24" (4 s, Privacy Notice bar), Ctrl+L, typed pair_01_b.png URL, "MAPLE" (4.5 s) |
| V7b | V7b | 33.7 | 63e08278121fb09a | MAPLE-24 / MAPLE-24; images.py l.97 and l.100 (both question forms; l.100 = second-image word, first-image number); pairs all [5,5] |
| V8 | V8 | 22.5 | bc5b1a9f02b601b0 | 6 tool names; **`{"index":0,"name":"multiply","arguments":{"a":4821,"b":7293}}`**; 35159553; final **"The result of multiplying 4821 by 7293 is 35,159,553."** (lab text identical; `fold -w 44` splits it as "...is 35" / ",159,553.") |
| V8b | V8b | 17.1 | 7a89ae8ddcb2378e | all [10,10], both models, 6 seeds each |
| V9 | (P14 C7) | - | 847515c7aba2a0b8 | reused, not refilmed |
| V9b | V9b | 39.1 | acdb2a46085ef781 | "Multiply 4821 by 7293."; 6; 1; `{"rows":12,"multiply":12}`; `{"rows":120,"used":0}` |
| V10 | V10 | 48.1 | ff9285fcd3deb003 | 8 lines from ```python / def merge_intervals; 10 items all n/n (36 tests); `{"model":"e4b","seed":1004,"item":"code_roman_to_int","tests_passed":1,"tests_total":3,"last_error":"AssertionError"}`; e4b 1004 [9,10], rest [10,10] |
| V11 | V11 | 43.1 | ce66de122d2671b2 | es/hi/ja codes with 42/36/210/56/27/54/75/41/40/63, all true; tasks.py l.140 Spanish prompt; es2 answer 36; all [10,10]. No hi/ja text on screen |
| V12 | V12 | 42.9 | 2a8a13f1cfa60050 | 20 lines (remainder false false 6.4); `{"eval_count":1024,"passed":false}`; off 9 / 33.7 s, on 10 / 45.6 s; temp 1 off 10,8,10,9,9 on 10 x5 |
| V12b | V12b | 28.5 | 16c3915c31564f4d | sevens / remainder / weekday think true 8139 / 8126 / 8129 false, 448.4 / 453.0 / 449.1 s; off 10 / 163.9 s, on 7 / 1816.6 s |
| V13 | V13 | 31.8 | e595633b06d43077 | `["completion","vision","audio","tools","thinking"]`; p15.py l.241 ESPEAK_TEXT; transcription **"A quick brown fox jumps over the lazy dog. Almera runs Gemma 4 on an 8 gigabyte card."** (lab /v1/audio/transcriptions row identical) |
| V14 | V14 | 29.4 | b7bc05fea7d939b2 | 4 lines ending "a good fortune" (e4b images field with a final "."); two "no audio" replies |
| V14b | V14b | 38.6 | 130eeee9481255f3 | 12b-q4 and 12b-qat images field ending "must be in want of a wife."; 12b-qat transcription also; 12b-q4 transcription ends "a good fortune"; e4b images-field tail ends "a good fortune."; 12b eSpeak lines incl. 12b-q4 "write 1.7 and not point seven. write 3 instead of three." |
| V15, V15b | - | - | - | CUT (F18), not filmed |
| V16 | V16 | 40.3 | febd72da8964818d | see below: **differs from the script** |

### V16 differs (quote as filmed, not re-taken)
`ollama run gemma4:e4b-it-q4_K_M "... Output only the text. /tmp/my.png" | tee /tmp/got.txt` on the 0.40.16 client:
stderr "Added image '/tmp/my.png'"; then, because the CLI's default turns **thinking on** for this model and prints it to
stdout when piped, `got.txt` holds a "Thinking..." block (15 lines: "Thinking Process:", 4 numbered steps, "...done
thinking.", blank) **before** the two transcribed lines, which are exactly right ("$ docker compose up -d" / "Error
response from daemon: port 8080 is already allocated"). `diff -wB /film/want-ocr00.txt /tmp/got.txt` prints
**`0a1,15`** and 15 `>` lines (the thinking block); no line of the transcription differs. The model's thinking also says
"There is also some stray characters/artifacts visible after the second line" (none are drawn on the card).
So F20's "this run: N lines differ" would be **15**, all from the thinking text, not the transcription. Recipe fix to
consider (not filmed, needs the script gate): `ollama run --think=false ...` or `--hidethinking`; the Windows card's
`fc /w` would show the same 15 extra lines with the current recipe.

Count: 19 of 19 shots covered (V0, V9 reused takes; 17 take folders). FRESH: 6 of 6 (V1, V5, V7, V8, V13, V16). **Gate
(§1): V1, V5, V8, V13 repeated their lab rows exactly; V16 (at-home recipe) differs from the script's expectation as
above.** One attempt per shot, no re-takes. Not done here: no render, no footage.py clips, no accuracy review.
