# LAB-STATUS: gemma4-limits-lab (Gemma Series Parts 13-16), lab night 10-11 Nov 2026

Lab stage only (measurements). No filming, no render, nothing pushed. Numbers below are copied from
`out/<part>/results.json` / `RESULTS.md`; those files win if anything here disagrees.

## Setup as run
- Ollama `0.40.16@sha256:910d0d81...` (pulled by digest; every row reports 0.40.16). Models from the existing volume
  `gemma-lab-models` (nothing deleted); pulled only `gemma4:e2b-it-q4_K_M` (4.59 GB manifest, digest b37049369adf).
- Tags: e2b `b37049369adf` (MTP draft), e4b `dc35e8d9c606` (draft), 12b-it-qat `38044be4f923` (no draft),
  12b-it-q4_K_M `6114515d63c1` (draft), 26b `001e5dafc3c7` (draft). `/api/show` capabilities: e2b/e4b/12b both tags =
  completion, vision, audio, tools, thinking; 26b = completion, vision, tools, thinking (no audio).
- Containers stopped for the lab: `mcp-canvas-mcp-server-1` and `katha-kokoro` (memory). `scripts/night.sh` restarts
  both at the end. Also closed (gracefully) on the host: Media Player, Photoshop Express, WhatsApp (memory); before the
  26B stage `night.sh` closes Chrome and Firefox gracefully (owner allowed closing apps; both restore tabs).
- Docker had no free network address pool: the lab reuses the idle Part 12 network `gemma4-moe-lab_default`.
- C: free: 24 GB at start -> 11 GB after the image + e2b pull (stop rule 8 GB was not hit).

## Problems hit and what was done
1. First run: a 12B load with mem_limit 16g took Windows free RAM to 0.72 GB; the RAM watcher stopped the container
   (out/logs/safety.log). Fix: container cap 12g (16g only for the 26B stage), VM page-cache drop + "Windows >= 2 GB
   free" wait before every load (lab/common.py fresh()).
2. Ollama 0.40.16 logs `disabling mmap for llama-server load due to host memory pressure` on this host: loads read the
   whole file (recorded per row as `mmap_disabled`).
3. The RAM sampler loop died once mid stage 1 (inherited `set -e` + a failing `docker stats` during a server
   recreate): about 3 minutes of e2b q8_0 rows have no container-RAM value. Restarted (`scripts/memwatch.sh`), loops
   now `set +e`.
4. The VRAM baseline: ~3.0 GB of the 8 GB card is held by the Windows desktop (explorer, browsers, Office), NOT by the
   render server: stopping `mcp-canvas-mcp-server-1` freed nothing (3,024 MiB before and after). Ollama saw
   "available 6.5 GiB". Every "fits" number here is for a card with ~5 GB really free. **Plan §2 said the 2.9 GB was the
   render server: wrong.**

## Part 13 (DONE for e2b, e4b, 12b-qat; 26B: one row, see "26B")
- **P-DEF:** fresh load, no options: `/api/ps` context_length = **4096** for e2b, e4b, 12b-qat; server log at start:
  `msg="vram-based default context" total_vram="8.0 GiB" default_num_ctx=4096`.
- **P-TRUNC (e4b, 3 fresh-load reps; 12b-qat once):** a 9,644-token prompt at the default: HTTP **200** on
  `/api/chat`, `/api/generate` and `/v1/chat/completions`; `prompt_eval_count` = **2,051**; server log
  `level=WARN msg="truncating input prompt" limit=2051 prompt=9644 keep=5 new=2051` (first 5 tokens + the tail).
  Fact in line 1: answered **0/3** on all three endpoints ("I do not have access to any information about a vault or an
  access code in the text you provided."); fact in the last line: 3/3. The reply has **no truncation field** (keys:
  created_at, done, done_reason, eval_count, eval_duration, load_duration, message, model, prompt_eval_cached_count,
  prompt_eval_count, prompt_eval_duration, total_duration). `"truncate": false` -> HTTP 400 "request (9644 tokens)
  exceeds the available context size (4096 tokens), try increasing it" (chat and generate); `"shift": false` -> HTTP 400
  "the prompt is longer than the context length currently available to the model; ...". Fix control num_ctx 16384:
  prompt_eval_count 9,644, 3/3 right (fact at start and end). Temp 1.0 (5 runs): default 0/5, num_ctx 16384 5/5.
  12b-qat: the same (2,051 of 9,648; 0/1 start, 1/1 end; 16384 fixes it).
- **P-FIT (3 fresh loads per cell, medians; KV type read back from the log every row):**
  - e2b: every num_ctx 4K-128K loads 36/36 layers on the GPU (f16 and q8_0). 128K full prompt (125,125 tokens): prefill
    4,748 tok/s (26 s), write 61.6 tok/s.
  - e4b: 4K-64K 43/43 on the GPU; **128K f16: 40/43 layers on the GPU** (3 in system RAM) while `ollama ps` PROCESSOR
    says "100% GPU"; 128K q8_0: 43/43. 128K full prompt: f16 prefill 2,392 tok/s (52 s), write 35.5 tok/s;
    q8_0 prefill 1,578 tok/s (79 s), write 23.4 tok/s. 16K-token prompt at 128K: f16 3,767 vs q8_0 2,166 prefill tok/s.
  - 12b-qat: 64K f16 31/49 layers on GPU (write 12.8 tok/s), 128K 26/49 (11.0), 256K 19/49 (8.4); q8_0 35/30/23 of 49.
    256K full prompt (251,709 tokens): f16 prefill 301 tok/s = **836 s (14 min)**, write 1.4 tok/s; q8_0 323 tok/s
    (780 s), write 4.2 tok/s.
  - **`ollama ps` PROCESSOR is not a layer split on 0.40.16:** e.g. 12b-qat 256K "13%/87% CPU/GPU" with 19 of 49 layers
    on the GPU; `/api/ps` `size` for e4b reads 349 MB. Use the log's `offloaded N/M layers to GPU` for "fits".

## Night 2 (11-12 Nov, `scripts/tonight.sh`)
Stage 2 (P14 + P15 rest), stage 4 (26B), stage 3 (P15 temp 1.0, P16) ran 23:00 -> 04:35 local; NIGHT-DONE 04:35:55,
auto commit e68b90f. Row times below are UTC (local = UTC-5). Generated tables: `out/p14|p15|p16/RESULTS.md`.

## Part 14 (DONE for e4b + 12b-qat; temp 0 seed 42, num_ctx 8192, fresh load per section)
e4b has temp 0 + 5 runs at temp 1.0 (range = per-run counts). **12b-qat was run at temp 0 only** (`--t1reps 0` in
stage2.sh): by the plan's own rule its counts are "one run at temp 0", never a headline.
- **Multiply (20 4x4-digit):** e4b think off **1/20** right (temp 1: 0-1 of 20, 1/100 in all); think on **12/20**
  (temp 1: 10-13; 55/100). 12b-qat think off **0/20**, think on **6/20**, but 14 of its 20 think-on rows wrote ~8,100
  tokens and hit the 8,192 window with no answer (0 of those 14 right; median 443 s per item) -> on 12B the honest
  line is "thinking ran out of room", not "thinking got it wrong". The wrong products look right: e4b think off,
  20/20 same digit count, 19/20 first two digits right, 14/20 last two right (e.g. 3,978,816 for 3,979,016).
- **Calculator tool fix:** 12b-qat **20/20** (called the tool 20/20). **e4b called the tool 0/120 times** (temp 0 and
  all 5 temp-1 runs) and answered from its head: 0/20, same wrong products as no tool. e4b does call tools in P15
  (10/10 every run), so it is this prompt/task, not "e4b has no tools". Not investigated further.
- **Letters (20 words):** e4b 14/20 (temp 1: 14-14), spell first **20/20** (19-20). 12b-qat 14/20 -> 20/20.
  Tokenizer dump (`out/p14/tokenizer-dump.json`): "strawberry" = 1 token, "mississippi" = miss|issippi,
  "hippopotamus" = hipp|opot|amus (word pieces).
- **Weekday / date (10):** e4b 0/10 (0-0), date in system prompt **9/10** (9-9). 12b-qat 0/10 -> 9/10. How they fail
  differs (simple phrase match on the replies): e4b **declined** 9/10 ("I do not have access to the current date");
  12b-qat declined 6/10 and **made up** 4 (year 2025, "next Friday 2025-05-23", "911 days to new year").
- **After the cutoff (6, answers from release pages fetched 11 Nov):** e4b 0/6 (0-0), paste the source **6/6** (6-6).
  e4b declined 4/6 and gave 2 stale answers (Rust 1.78.0, newest Gemma = "Gemma 2"); 12b-qat answered all 6 stale and
  confident (Ollama 0.5.7 vs 0.40.16, Node 22.11.0 vs 26.13.0, Kubernetes 1.31 vs 1.37.2, "Gemma 2").
- **Citations (10 asked):** e4b listed 10, **9 DOIs resolve at doi.org but only 1 points to the paper it named**
  (temp 1: 7-10 resolve, 0-2 title match). 12b-qat 10 resolve, 1 title match. So "real-looking DOI, wrong paper".
- **On camera:** "19 of 20 wrong" (e4b, think off, temp 0; temp 1: 19-20 wrong per run); thinking 12/20; spell first
  14 -> 20; date in the prompt 0 -> 9; paste the source 0 -> 6; 9 of 10 DOIs real, 1 of 10 the right paper; the
  calculator fix shown on **12B** (20/20), with e4b ignoring the tool said plainly.
- **Not on camera:** "the calculator tool fixes e4b"; "it confidently made up today's date" for e4b (it declined);
  any 12B count as a range; "9 of 10 citations real" (only the DOI resolves); "thinking makes 12B worse" (window cap).

## Part 15 (DONE; e4b + 12b-qat at temp 0 + 5 temp-1 runs, except 12b thinking; P-AUD one run per cell)
| claim | e4b temp 0 | e4b temp 1 (5 runs) | 12b-qat temp 0 | 12b-qat temp 1 (5 runs) |
|---|---|---|---|---|
| OCR, exact text (10) | 10/10 | 9-10 | 10/10 | 10-10 |
| charts, all 4 values exact (5) | **2/5** | 1-2 | 3/5 | 3-5 |
| two-image prompt (5) | 5/5 | 5-5 | 5/5 | 5-5 |
| function calling (10) | 10/10 | 10-10 | 10/10 | 10-10 |
| coding, unit tests (10) | 10/10 | 9-10 | 10/10 | 10-10 |
| multilingual ES/HI/JA (10) | 10/10 | 10-10 | 10/10 | 10-10 |
| `format` JSON, values right (10) | 9/10 | 9-10 | 9/10 | 9-9 |
| thinking off / on (10) | 9 (34 s) / 10 (46 s) | off 8-10, on 10-10 | 10 (164 s) / **7 (1,817 s)** | **not run** |
- Charts: every value of every chart was within +-5 (5/5 both models, all 60 rows); misses are reading 95 as 93, 50 as
  51. Say "close, not exact", not "can't read charts".
- 12b-qat thinking on: the 3 misses each wrote ~8,130 tokens into the 8,192 window (~450 s each) and never answered;
  30 min for 10 puzzles vs 2.7 min off. **Complete at temp 0 (10 off + 10 on, as planned), but the plan's temp-1 range
  is missing**: 12B thinking at temp 1 was skipped on purpose (b23bf92: 3 attempts died to RAM stop / Windows Update
  reboot / host reap; their 19-row partials `can-12b-thinking-partial-*.jsonl` are NOT scored). Say "one run at temp 0".
- Audio (P-AUD, Ollama 0.40.16, WER vs the reference text, one run each): e2b and e4b transcribe on both routes
  (LibriVox WER 0.18-0.22, eSpeak 0.22-0.28; no-clip control: both say there is no audio). 12b-q4_K_M: eSpeak WER 1.0
  on both routes (unrelated text), LibriVox 0.18 via `/v1/audio/transcriptions`. 12b-qat: LibriVox 0.07 via
  `/v1/audio/transcriptions`, eSpeak 0.50-0.56. **Both 12B tags on the `images` field "transcribe" LibriVox as the
  opening line of Pride and Prejudice (WER 0.62): recited from memory, not heard.**
- **On camera:** OCR 10/10, tools 10/10, coding 10/10, multilingual 10/10 (3 languages), two images 5/5, charts 2/5
  exact but all within 5, JSON values 9/10, thinking (e4b) 9 -> 10 for +12 s; audio works in e2b/e4b on 0.40.16.
- **Not on camera:** "12B thinking is worse" as a range; "audio works in Gemma 4" (say: these tags, this version); the
  12B images-field "transcript" as a transcript; any P-AUD number as a range (one run).

## Part 16 (DONE for e4b + 12b-qat, f16 KV, temp 0; 26B rows NOT run)
Every row arrived whole (prompt_eval_count = control, no truncation WARN, 222/222 HTTP 200).
- **Single needle:** **3/3 at every depth and every length** for both models (e4b 4K-128K, 12b-qat 4K-128K; depths
  0/10/25/50/75/90/100% to 32K, 10/50/90% at 64K and 128K). No depth effect at all.
- **Eight facts:** e4b **8/8 in 3/3 runs at every length incl. 128K**. 12b-qat 8/8 x3 at 4K, 16K, 64K; 32K 8, 7, 8
  (one "no code for the Fjord room"); **128K 8, 5, 8**: run 2 wrote "Z-89" four times (copy loop), not "forgot".
- **Cost (prefill, 125K tokens):** e4b **54 s**, 12b-qat **266 s (4.4 min)**; at 32K 6.5 s vs 38 s. 12b-qat writes
  3.6 tok/s at 128K. (e4b's needle write speed 81-87 tok/s is a short code-list reply with the MTP draft on; do not
  compare it with P13's 35.5 tok/s.)
- Controls: question-first 3/3 and think-on 3/3 (e4b, 32K, depth 50%).
- **Not run vs the plan:** 26B rows (stage 4 died, below), the one q8_0 row (every needle row is f16), 256K (12b-qat
  loads it in P-FIT but prefill is 14 min), the "retrieve the chunks" measure.
- **On camera:** "3/3 at every depth", "8 of 8 at 128K, three times" (e4b), "8, 5, 8" (12b-qat at 128K) with the loop
  shown, 54 s vs 4.4 min to read 125K tokens.
- **Not on camera:** "lost in the middle" (strips show nothing), percentages, anything about 26B recall, "q8_0 recall".

## 26B (stage 4, 12 Nov 01:51-01:55 local): reported as is (owner, 12 Nov: no re-run)
- PC: 32 GB RAM, WSL 24 GB, container cap 16g; Chrome + Firefox closed first (Windows free 9.54 GB after).
- Loading 26B took Windows free RAM to **0.56 GB**; the lab guard stopped Ollama 01:52:07, 01:52:28, 01:55:13 (0.56 /
  0.61 / 0.75 GB, `out/logs/safety.log`). P-DEF, P-FIT f16, P-CAN tools and P-NEEDLE for 26B got connection errors only
  (`out/logs/stage4.out`): **no 26B row for any of them.**
- **The one result** (`out/p13/fit.jsonl`, 01:54:28): q8_0 KV, num_ctx 65,536, fresh load 32 s, 16,216-token prompt
  prefill 285 tok/s (57 s), write **17.6 tok/s**, `ollama ps` **21%/79% CPU/GPU**, log offload (31, 31), GPU 7,587 MiB,
  container RAM 15.0 GB. Rep 2 at 01:55 died with the guard stop. n = 1.
- **Say:** "26B does not fit beside an 8 GB card on this PC (32 GB RAM): it ran once at 64K with a q8_0 cache, 17.6
  tokens/s, then RAM ran out." **Do not say:** any 26B context limit, recall, tool or f16 number; "26B needs N GB".

## Title N values and contradictions (accuracy wins)
- **P13 title:** the lab shows the prompt cut with HTTP 200, no field in the reply, only a log WARN -> by the plan's
  own rule use **"Ollama Cut My Prompt: Gemma 4 num_ctx Fix on an 8GB GPU"**. Thumbnail "128K? GOT 4K" is wrong for
  what the model read: it read **2,051 of 9,644 tokens** (window 4,096; Ollama keeps about half for the answer) ->
  suggest "128K? READ 2K" or "SENT 9,644, READ 2,051".
- Plan §4 "Verify the split under PROCESSOR using ollama ps" (Ollama docs S4.4): on 0.40.16 PROCESSOR said 100% GPU
  at e4b 128K f16 while the log said 40/43 layers -> the script must use the log line (or say PROCESSOR is wrong).
- q8_0 is not free: at 128K it moves e4b fully onto the GPU but prefill drops (2,392 -> 1,578 tok/s on the full
  prompt) and write drops (35.5 -> 23.4 tok/s). Its needle row is still pending.
- Line 1 of P13 ("my 10K-token prompt lost its first line") holds: 9,644 tokens, line 1 lost.
- **P14 title:** "Gemma 4 Got N/20 Math Wrong in Ollama: 5 Failures + Fixes" -> **N = 19** (e4b, think off, temp 0;
  temp 1: 19-20 wrong per run). The calculator-fix beat must use 12b-qat (20/20) or show e4b ignoring the tool.
  Thumbnail "WRONG, CONFIDENTLY" fits multiply + citations; e4b mostly declined the date/cutoff questions.
- **P15 title:** audio did not fail (e2b/e4b transcribe) -> the plan's second title **"Gemma 4 Vision, Function
  Calling, Audio in Ollama: 7 Claims Tested"**. The claim that did not fully hold for the hook = charts (2/5 exact,
  all within 5).
- **P16 title:** recall is near-perfect (e4b 8/8 x3 at 128K, 12b-qat 8/5/8) -> the plan's fallback **"Gemma 4 128K
  Context in Ollama: It Finds the Fact. It Takes N Minutes"**, **N = 4** (12b-qat, 266 s = 4.4 min; e4b is 54 s, so
  name the model on screen). If the primary title is kept: "It Found 8" (e4b) / thumbnail "FOUND 8 OF 8".
- **26B:** one row only; no title uses it.

## Resume from here
Lab measurements are finished; 26B is reported as is (owner, 12 Nov). Findings above + `out/pNN/RESULTS.md`. Plan
overrides are logged in `Refream-Canvas/inputs/video-plans/2026-11-10-gemma-4x/PLAN.md` §0 "lab results (12 Nov)".
Open (none blocks the scripts): why e4b never called the multiply tool in P14 (it does in P15); 12b thinking temp-1
range (P15) and 12b temp-1 ranges (P14) were never run; P16 q8_0 row, 256K and the retrieve-chunks measure were not
run. Next step: script stage for Part 13 (Part 16 waits for Part 13's 7-day check per the plan).
