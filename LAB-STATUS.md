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

## Part 13 (DONE for e2b, e4b, 12b-qat; 26B rows in stage 4)
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

## Part 14, Part 15, Part 16, 26B: see "Resume from here"

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

## Resume from here
`scripts/night.sh` (started ~05:45 UTC 11 Nov) runs unattended: waits for stage 2 (P15 temp 0 + P-AUD + P14), then
closes Chrome/Firefox and runs stage 4 (26B: DEF, FIT f16/q8_0, tools, needle short set) only if it is still before
07:00 local, then stage 3 (P15 temp-1.0 x5, P16 needle e4b + 12b-qat), regenerates every `out/pNN/RESULTS.md` + `results.json`, archives logs to
`E:\2026-SomaPersonal\StackUnderflow-archive\gemma4-limits-lab\logs`, commits locally, restarts
`mcp-canvas-mcp-server-1` and `katha-kokoro`, and writes `NIGHT-DONE` to `out/logs/night.out`.
To check: `tail -3 out/logs/night.out; grep -a -E "^[0-9]{2}:" out/logs/stage{2,3,4}.out | tail`. If a stage failed,
re-run that stage script alone (each is idempotent apart from appending rows; delete its jsonl first for a clean set).
Still to write by hand after the night: the P14/P15/P16 findings and title N values in this file.
