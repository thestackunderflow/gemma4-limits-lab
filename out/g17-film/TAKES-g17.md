# g17 filming takes (14 Nov 2026)

All numbers on screen are printed by code from `out/g17/` rows. Videos/images stay local (not committed); sha256 prefix
and length below were printed by `sha256sum` / `ffprobe` after the takes.

GUI takes (`scripts/film17/gui-run.sh` -> `gui.sh`, image `sc5-l5:0.28.0`, the course lab's fx15 split layout reused
read-only: SolidCraft 0.28.0 window on top at UI scale 1.8, terminal strip below; 2880x1620, 30 fps, cursor log +
events.jsonl for footage.py). Each is a FRESH temp-0 chat, Gemma 4 E4B driving the open SolidCraft window through
`solidcraft-cli mcp`; one line per request (`G17_LIVE`), then `scripts/film17/show.py` prints the turn-20 result.
The window shows SolidCraft's own "Update to 0.41.0" button (the pin is 0.28.0; the latest release on 14 Nov is 0.41.0).

| take | storyboard | chat | sha256 | seconds |
|---|---|---|---|---|
| V1 | F0/F6 (spare) | film-v1-8k: result lines failed (no jq in the image); the chat part is usable | a6057ade47e327fb | 105.6 |
| V1b | F0, F6, Short S0/S1 | film-v1b-8k (8K, no fix) | 522448e3f5a1abad | 120.1 |
| V2 | F9 (bigger window) | film-v2-32k (32K) | 7f45d2710582a944 | 90.6 |
| V3 | F10 (running summary) | film-v3-sum16k (16K, summary) | df35aa420f85e00f | 124.6 |

Terminal takes (`scripts/film17/run.sh`, `film13:1` + `scripts/film13/lib.sh`, xterm DejaVu Sans Mono 30, tmux):

| take | storyboard | content | sha256 | seconds |
|---|---|---|---|---|
| T1 | F1, F2, F5 | nvidia-smi one line; turn 2 sent alone (live, lab body `turn2-alone.json`), reply asks what to change; menu tokens with / without tools | fe05479d980f1d1f | 37.7 |
| T2 | F4, F6 | turn 2 inside the 16K chat (tool call on the plate); reuse %; sent vs reused per request; 8K first drop + status/done_reason counts | 20119711811fcc39 | 36.9 |
| T3 | F9, F10, F11 | fix lines from results.json (8K arms + 32K; written before the 16K arms existed), winner arm, the 15-line check script in 5-line chunks, run live on E4B | e1e0e0761b1a05e1 | 82.1 |
| T4 | F0, F9, F10, F12, F13, F14, Short S3/S4 | pickup (14 Nov, render agent): jq lines on lab files only, no model call; V1b stale values, V2/V3 hole spacing 34.5 / 24.0, V3 reply line (grep `[^.]*` + `fold -s -w 44`: the handover's `.*` and `fold -w 44` printed past the sentence and split "requested"; re-filmed), 32K reps, pin/summary 16K `[right, 8/8]`; all 8 lines checked against HANDOVER §1.2 | d028a084516b09f5 | 42.7 |

Known limits: `check/g17_reuse.py` lines 2-4 and 7-14 are wider than 44 columns (cut on screen in T3); T3 does not show
the 16K fix arms; fresh GUI runs differ from the lab rows (GUI app vs headless MCP, see RESULTS-g17.md last section).
