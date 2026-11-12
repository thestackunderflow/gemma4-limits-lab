# Part 13 filming takes (12 Nov 2026, owner GO)

Shot list: `Refream-Canvas/inputs/video-plans/2026-11-10-gemma-4x/SHOTLIST-13.md` rev 2. Every take: `film13:1`
(`docker/film13/Dockerfile` = screen-lab-base:1 + jq + Firefox ESR 153.7.0esr + the Ollama 0.40.16 client from the
pinned image), screen-lab kit recorder, Xvfb 1920x1080, 30 fps, CRF 14, T0 from `-debug_ts`; xterm DejaVu Sans Mono 30
(K2/K10b 24, K12 22, K7b 20) running tmux; prompt `$ `; full window 2.5 s before the first command. Takes are run
by `scripts/film13/run.sh <shot>` (drops the WSL page cache as `lab/common.py fresh()` does, checks free RAM >= 4 GB,
foreground). Server: the running `gemma4-limits-ollama` (0.40.16 digest 910d0d81, flash attention 1, KV f16,
KEEP_ALIVE 0, NUM_PARALLEL 1, DEBUG 1; mem_limit 16g as left by the 26B rows, not the default 12g). memwatch.sh was
not run (no background chains); free RAM was checked before every take and never under 6 GB at a load.

Per take folder: `screen.mp4` (not committed; sha256 below), `pane-N.txt` (the terminal text, the verification copy),
`events.jsonl` (typed commands with t from frame 0), `record.json`, `cursor.jsonl`, `end.png`, `nvidia-start.txt`
(model takes). `server-live-<shot>.log` = `docker logs` of the server during that take (the container's tee target
`out/logs/server.log` had been renamed on the host while the server ran, so its live lines exist only in docker logs;
K5's was exported afterwards for 19:43:30-19:45:30Z). Model metadata in those logs contains the publisher's build
path (`/Users/daniel/...` imatrix keys); it is not on screen in any take.

| Shot | Folder | Dur s | sha256 (16) | Command(s) | Visible / verified |
|---|---|---|---|---|---|
| K1+K3 | K1-K3 | 24.3 | a96ddb08159f2f8e | `ollama --version`; `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader`; clear; `ollama list`; `ollama list \| grep gemma4` | "ollama version is 0.40.16"; "NVIDIA GeForce RTX 4060, 8188 MiB"; e2b-it-q4_K_M 4.6 GB, 26b 18 GB, 12b-it-qat 7.2 GB, e4b-it-q4_K_M 6.6 GB (also 12b-nvfp4, 12b-it-q4_K_M, gemma3:12b-it-qat listed) |
| K2 | K2 | 34.3 | 94de7b8bb1d625c1 | left `ollama show gemma4:e4b-it-q4_K_M`, then `\| grep -i context`; right `ollama run gemma4:e4b-it-q4_K_M --keepalive 2m --think=false "Say OK."`, `ollama ps` | context length 131072; reply "OK."; ps: 100% GPU, CONTEXT 4096, RUNNER llamacpp, SIZE "349 MB" (sic). ps line wraps in the half pane |
| K4 | (no camera) | - | 7dfce9e08648bb04 vault-start.txt; d6b96011752b4f0d req-trunc-false.json | `lab.p13.prompt('start')` in the runner image; request file as the shot list (+ `req-16k.json` 56b696d14d812ab6 = same with num_ctx 16384, no truncate, written by K10) | `wc -w` = 7584 |
| K5 | K5 | 37.4 | 6ba6b8cd4cc6d1b9 | `wc -w`, `head -c 40`, `tail -1` on the file; `ollama run gemma4:e4b-it-q4_K_M --verbose --think=false < /film/vault-start.txt` | **GATE: prompt eval count 2051** (match). Reply: "I am sorry, but there is no mention of a vault or an access code in the text you provided." load 13.2 s, prompt eval 1450 tok/s, eval 113.7 tok/s. VRAM before 2308 MiB |
| K6 | K6 | 29.0 | 198adb55a1415831 | `grep -m1` "vram-based default context" and "truncating input prompt" on `server-20261111T040329Z.log`, `fold -w 44`; clear; the WARN from `server-live-K5.log` | total_vram="8.0 GiB" default_num_ctx=4096; limit=2051 prompt=9644 keep=5 new=2051 (lab, 04:01:07Z) and the same from this shoot's K5 (19:44:34Z). Attempt 1 lacked the K5 log file (grep error on screen), refilmed once |
| K6b | K6b | 13.7 | 455928bf0674b21c | `jq` chat/start row of trunc.jsonl -> `{status, reply_keys}` | 200 and the key list, no truncation field |
| K7 | K7 | 8.3 | dd28d52e5ec49e58 | Firefox ESR, docs.ollama.com/context-length, no scroll needed | Note box: "< 24 GiB VRAM: 4k context", "24-48 GiB VRAM: 32k context", ">= 48 GiB VRAM: 256k context" (page text checked by curl the same hour). A Firefox "updated Privacy Notice" bar shows at the top. Attempt 1 (`K7-attempt1-welcome-modal`) was covered by the first-run modal |
| K7b | K7b | 14.4 | 12120d07c23bd507 | `ollama ps` (empty); `nvidia-smi` | 2321MiB / 8188MiB with no model (about 2.3 GB, not the "about 3 GB" in the plan) |
| K8 | K8 | 27.3 | 81aca6859d85bbfc | `ollama run gemma4:e4b-it-q4_K_M --think=false`; `/set parameter num_ctx 16384`; `/save gemma4-e4b-16k`; `/bye` | "Set parameter 'num_ctx' to '16384'"; then **/save FAILED**: "Error: pull model manifest: file does not exist", and the CLI exited (the typed `/bye` went to bash: "No such file or directory"). Server log: `create model from model name from=gemma4-validation-20260929:e4b-imatrix-attention-q6-q8-draft2` (the tag's embedded source name), /api/create 200. No model was created. Fallback §3 used for K10/K10b |
| K9 | K9 | 28.1 | a3c5fac2151a8797 | `jq -c '.options, .truncate'`; `curl -s -o /tmp/r.json -w '%{http_code}\n' .../api/chat -d @req-trunc-false.json`; `jq -r .error /tmp/r.json` (one request, not two) | false; 400; "request (9644 tokens) exceeds the available context size (4096 tokens), try increasing it" |
| K10 | K10 | 40.7 | 6ee6255ac46b12b3 | FALLBACK: `jq -c .options /film/req-16k.json`; twice `curl -s .../api/chat -d @/film/req-16k.json \| jq '.prompt_eval_count, .message.content'` (clear between) | **GATE: 9644 and "K-77", both runs** (fresh load each, KEEP_ALIVE 0) |
| K10b | K10b | 25.6 | 8c842b292e352772 | FALLBACK: `curl .../api/generate` "Say OK." keep_alive 2m, options num_ctx 16384, `\| jq -r .response`; `ollama ps` | "OK."; NAME gemma4:e4b-it-q4_K_M (not gemma4-e4b-16k), 100% GPU, CONTEXT 16384, SIZE "362 MB" |
| K11 | K11 | 26.3 | e6c64917bf73ad58 | `jq` speed rows e2b, clear, e4b | e2b [36,36] every row; e4b [43,43] to 65536, [40,43] at 131072 f16 (q8_0 131072 [43,43]) |
| K12 | K12 | 38.1 | be03594e8f19bfab | 3 panes: top-left curl generate num_ctx 131072 then `grep offloaded /film/server-live-K12.log \| tail -2`; top-right `ollama ps`; bottom `nvidia-smi ... -l 1` | live "offloaded 40/43 layers to GPU" (+ "offloaded 5/5 layers to GPU", the second loader) beside ps "100% GPU", CONTEXT 131072, SIZE "458 MB"; VRAM 2355 -> 7728 MiB. Log path differs from the shot list (docker-logs copy, see top) |
| K13 | K13 | 33.9 | 335116cfa6df2c36 | `jq` 12b-qat f16 speed rows; clear; max-fill rows; def.jsonl row | [31,49] 12.9/12.8/12.4 at 65536; [26,49] 11.0/10.8/11.1 at 131072; [19,49] 8.1/8.4/8.6 at 262144; max-fill f16 262144 [19,49] prefill 836.42 s, 1.4 tok/s (q8_0 [23,49] 779.55 s, 4.2); def offload [38,49] |
| K14 | K14 | 40.7 | bda998416876bbc8 | `grep -n` env lines in compose.yaml; `grep -m1 'K (q8_0)'` 052301Z log `\| fold -w 44`; clear; e4b 131072 max-fill and speed rows | lines 23/24 FLASH_ATTENTION, KV_CACHE_TYPE; "K (q8_0): 6.38 MiB, V (q8_0): 6.38 MiB" (a 4096-cell load); max-fill f16 52.32 s 35.5 tok/s [40,43] vs q8_0 79.28 s 23.4 [43,43]; speed write 61.1/59.1/63.2 vs 61.5/63.0/69.2, prefill 3844/3767/3751 vs 2164/2166/2194 |
| K15 | K15 | 20.0 | dad728e5238d3ff9 | `jq -c` 26b rows; `grep STOP safety.log \| tail -3` | q8_0 65536 17.6; second row ConnectionError(...RemoteDisconnected...); STOP 01:52:07 0.56, 01:52:28 0.61, 01:55:13 0.75 |

Count: 17 of 17 shot ids covered (K4 no camera; K8 shows the real /save failure; K10/K10b on the §3 API fallback).
Gate: K5 2051 and K10 9644 both match the lab. Not done here: no render, no footage.py clips, no accuracy review.
