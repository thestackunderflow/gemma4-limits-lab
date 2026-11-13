# Part 14 filming takes (12 Nov 2026, owner GO)

Shot list: `Refream-Canvas/inputs/video-plans/2026-11-10-gemma-4x/SHOTLIST-14.md` rev 2. Same kit and method as Part 13
(`out/p13-film/TAKES.md`): `film13:1` image, `scripts/film13/lib.sh` helpers, Xvfb 1920x1080, 30 fps, CRF 14, T0 from
`-debug_ts`; xterm DejaVu Sans Mono 30 (C11, C14 at 24) running tmux; prompt `$ `; full window 2.5 s before the first
command (browser takes 3 s). Takes run by `scripts/film14/run.sh <shot>` (a copy of `scripts/film13/run.sh` writing to
`out/p14-film`): drops the WSL page cache, checks Windows free RAM >= 4 GB, foreground, one take per call.

Server: `gemma4-limits-ollama` recreated before the shoot with `scripts/lab.sh up f16` so the cap is the default
**12g** (it had been left at 16g by the 26B rows); 0.40.16 digest 910d0d81, flash attention 1, KV f16, KEEP_ALIVE 0,
MAX_LOADED_MODELS 1, NUM_PARALLEL 1, DEBUG 1. Free RAM at each model take: 15.0, 9.05, 9.48, 11.43, 11.36, 11.22 GB
(E4B), 11.34, 4.61, 7.42 GB (12B); lowest after a take 4.22 GB (after C6, 12B still loaded for its 2 m keep_alive).
memwatch.sh not run (no background chains, as P13). No browser or owner app was closed.

Per take folder: `screen.mp4` (not committed; sha256 below), `pane-N.txt` / `pane-N.before-clear-K.txt` (terminal text,
the verification copy), `events.jsonl`, `record.json`, `cursor.jsonl`, `end.png`, `nvidia-start.txt` (model takes),
`reply.json` (C4) / `reply1.json` (C6, the step-1 reply). `server-live-<shot>.log` = `docker logs --since <record t0> --until <t0 + duration + 3 s>` (re-cut after the shoot:
the P13-style `docker logs -f &` follower was never killed under Git Bash, so each live log kept every later take's
lines, and the 8 P13 server-live logs had picked up 10 lines each from the container restart; those were reverted to
their committed state. `run.sh` now reads the log once after the take). Empty for the no-model takes. Model load
metadata in these logs carries the publisher's build path (`/Users/...` imatrix keys); not on screen in any take.

## C0 (no camera): request files

Built by `scripts/film14/c0.py` in the runner image from `lab/tasks.py` and `lab/p14.py`. sha256 (16):
mul00.json 2a5b4573097c63e3; mul00-think.json 7906f6d62dd98de8; tool-12b.json 89f453dd4a2b9cce; tool-e4b.json
8307314e1f4e33f7; let-bookkeeper-spell.json 39849b01088cc886; date-none.json 57a8232e774e040b; date-sys.json
5cb8d9c2ea45ae66; cut-ollama.json 668dd63cadf626a4; cut-ollama-paste.json d76b098b332542fc; send-result.sh
4553fa8dfc8fed7c.

**Differs from the shot list (on purpose, to repeat the lab exactly):** the shot list says `think` is "not sent" for the
letters / dates / cutoff files. The lab's `Session.chat` (lab/p15.py l.28-38) always sends `"think"`, `false` unless
the think rows, so every file carries `"think": false` (mul00-think.json `true`). Options are the lab's
(`temperature 0, seed 42, num_predict` per row, `num_ctx 8192`); keep_alive is `2m` (lab `15m`, no effect on the reply).
`send-result.sh` writes the tool message as the lab's `json.dumps` does (`{"result": 3979016}`, with the space).

## Takes

| Shot | Folder | Dur s | sha256 (16) | Command(s) | Visible / verified vs lab row |
|---|---|---|---|---|---|
| C1 | C1 | 26.2 | 5afd277ad3d31865 | `jq -r '.model, .messages[0].content'`; `curl .../api/chat -d @/film/mul00.json \| jq -r .message.content`; `echo $((2824 * 1409))` | gemma4:e4b-it-q4_K_M; the question; **3978816** (lab 3978816, match); 3979016. VRAM before 1187 MiB |
| C2 | (P13 K1-K3) | - | a96ddb08159f2f8e | reused, not refilmed | - |
| C3 | C3 | 64.1 | 4f806aab633f713b | mul rows `[.answer,.want,.passed] @tsv`; clear; summary `{think,fix,temp,passed}` for e4b mul; clear; median `seconds` by think; e4b tool rows; p15 mul1/mul2 rows; clear; e4b temp-0 count lines for letters/dates/cutoff | 20 rows, one `true` (2261760, mul05); temp 0 think off 1, think on 12, tool 0; temp 1 think off 1,0,0,0,0, think on 13,10,11,10,11, tool 0 x5; median 0.2 s (off) / 2.6 s (on); `{"rows":120,"used":0}`; `{"rows":12,"multiply":12}`; letters 14 / 20, dates 0 / 9, cutoff 0 / 6 (of 6) |
| C4 | C4 | 21.4 | 011ba49e8ea370ed | `curl ... mul00-think.json \| tee /tmp/t.json \| jq -r .message.thinking \| head -3`; `... \| wc -l`; `jq -r '.message.content, .eval_count'` | `thinking` field present: "The user wants me to calculate the product of 2824 and 1409.", blank, "$2824 \times 1409$"; 42 lines; **3979016** and **eval_count 488** (lab 3979016 / 488, match); 3.3 s total |
| C5 | C5 | 33.9 | 6e0068b188ddfaa7 | 12b-qat think rows `[.item,.eval_count,.passed,.seconds] @tsv`; clear; count of eval_count 8156; 12b tool rows `{rows,used,right}` | 14 rows 8156 false (441.4-451.9 s), 6 true (mul00 960, mul01 597, mul05 754, mul09 2405, mul17 1137, mul19 2389); `14`; `{"rows":20,"used":20,"right":20}` |
| C6 | C6 | 39.8 | 634e5882594cbff8 | `jq -c '.model, .tools[0].function.name'`; `curl ... tool-12b.json \| tee /tmp/r1.json \| jq -c '.message.tool_calls[0].function'`; `echo $((2824 * 1409))`; clear; `cat /film/send-result.sh`; `/film/send-result.sh 3979016` | "gemma4:12b-it-qat", "multiply"; **`{"index":0,"name":"multiply","arguments":{"a":2824,"b":1409}}`** (lab call multiply a 2824 b 1409, match; the literal text includes `"index":0`); 3979016; the 6-line script; final reply **3979016** (lab, match) |
| C7 | C7 | 18.5 | 847515c7aba2a0b8 | `jq -r .model`; `jq -r '.messages[0].content' \| fold -w 44`; `curl ... tool-e4b.json \| jq -c '.message.tool_calls, .message.content'` | prompt ends "...Answer with the number / only." (fold splits "number" and "only."); **null** and **"3978816"** (lab: no call, 3978816, match) |
| C8 + C9a | C8 | 41.6 | 0449b57d71a414ca | three `jq -r 'first(.items[] \| select(.text==W)) \| .text + " → " + ([.tokens[].piece] \| join(" · "))'` (bookkeeper, strawberry, 4821 × 7293); clear; C9a e4b let_bookkeeper temp-0 row `{answer,want,passed}` | "bookkeeper → book · keeper"; "strawberry → strawberry"; "4821 × 7293 → 4 · 8 · 2 · 1 ·  × ·   · 7 · 2 · 9 · 3" (a " ×" piece and a separate space piece); `{"answer":"4","want":3,"passed":false}`. C9a filmed in the same take as C8 |
| C9 | C9 | 14.8 | 119139fabb737eab | `jq -r '.messages[0].content' \| fold -w 44`; `curl ... let-bookkeeper-spell.json \| jq -r .message.content` | 1. b ... 10. r, "There are 3 letters that are "e".", **"Answer: 3"** (lab text identical, match) |
| C10 | C10 | 14.6 | bef05788cce958eb | `jq -r '.messages[-1].content' \| fold -w 44`; `curl ... date-none.json \| jq -r .message.content \| fold -w 44` | **"I do not have access to the current date, so I cannot tell you what day of the week it is today."** (lab text identical, match) |
| C10b | C10b | 14.0 | 9113ad7424a8aa63 | `jq -c '.messages[0]' \| fold -w 44`; `curl ... date-sys.json \| jq -r .message.content` | the system message "Today's date is Tuesday, 10 November 2026 (2026-11-10)."; **"Tuesday"** (lab, match) |
| C11 + C11b + C12a | C11 | 42.5 | e9eeead8790f5c06 | 12b-qat dates rows `[.item, .answer[-24:]] @tsv`; e4b year row; clear; 12b-qat cutoff rows `[.item, .answer[-20:], .want] @tsv`; clear; C12a `jq -r '.ollama.tag, .ollama.fetched' sources/releases.json` | all 10 date rows (crop to year 2025, minus30_date 2025-04-23, next_friday 2025-05-23, days_to_new_year 911); e4b year 2024; cutoff 0.5.7 / 0.40.16, 22.11.0 / 26.13.0, 1.31 / 1.37.2, 1.84.1 / 1.99.1, 1.93.3 / 1.145.3, Gemma 2 / gemma 4; "v0.40.16", "2026-11-11T05:58:14Z". Font 24 |
| C12 | C12 | 14.9 | 2cfd1a80947184ed | `jq -r '.messages[0].content' \| fold -w 44`; `curl ... cut-ollama.json \| jq -r .message.content` | the question; **"0.5.7"** (lab, match) |
| C12b | C12b | 19.6 | 0fd2667ea0f636c2 | `jq -r '.messages[0].content' \| head -3`; same `\| wc -l`; `curl ... cut-ollama-paste.json \| jq -r .message.content` | "Use the source below to answer.", blank, "Source:"; **25** lines; **"v0.40.16"** (lab, match) |
| C13 | C13 | 11.5 | 7e57ca23dd3f8ca3 | Firefox ESR, ai.google.dev/gemma/docs/core/model_card_4; full window 3 s; Ctrl+F "cutoff date", Enter | "Our pre-training dataset ... with a **cutoff date of January 2025**." highlighted, "1 of 1 match" (page unchanged on this sentence). Firefox "updated Privacy Notice" bar at the top, as P13 K7 |
| C14 | C14 | 38.5 | 9a279e3090d6dd14 | e4b temp-0 cite rows `.citations[] \| [(.line[:24]), .doi_resolves, .title_matches] @tsv`; clear; `.citations[1] \| .line, .doi_title`; clear; `{model, temperature, n_listed, n_doi_resolves, n_title_matches}` per cite row | 10 rows, 9 resolve (row 1 "Sparse Attention: A Surv" false), 1 title match (Transformer-XL); "Reformer: The Efficient Transformer \| 10.48550/arXiv.2001.01210" → "Examples of varieties with index one on $C_1$-fields"; temp 1 resolves 9,7,8,10,9 / matches 0,0,2,1,0; 12b-qat 10 / 1. Font 24 |
| C15 | C15 | 22.2 | 1d74325b0f74a358 | Firefox ESR on https://doi.org (full window 3 s), Ctrl+L, typed `doi.org/10.48550/arXiv.2001.01210`, Enter | lands on arxiv.org/abs/2001.01210: **"Examples of varieties with index one on C1-fields"** (Ananyo Dan, Inder Kaur; public paper authors, nothing masked). **Differs from the shot list:** doi.org's home page has no resolver box (probe screenshot, 12 Nov), so the DOI was typed into the address bar after `doi.org/` instead of into a box on the page |

Count: 19 of 19 shots covered, 16 take folders (C0 no camera; C2 reused from P13; C9a in the C8 take; C11b and C12a in the
C11 take). FRESH: 11 of 11. **Gate (§1): every fresh model take repeated its lab row** (C1 3978816; C4 3979016, 488;
C6 multiply 2824 x 1409 then 3979016; C7 null + 3978816; C9 Answer: 3; C10 the decline, word for word; C10b Tuesday;
C12 0.5.7; C12b v0.40.16; C15 lands on the C1-fields paper). One attempt per shot, no re-takes. Not done here: no
render, no footage.py clips, no accuracy review.
