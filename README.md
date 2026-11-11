# Gemma 4 limits on an 8 GB GPU: context, can't, can, recall (a measured, test-first lab)

**Lab snapshot: 10-11 Nov 2026.** Ollama 0.40.16 (`ollama/ollama:0.40.16@sha256:910d0d81…`, pinned by tag and
digest), NVIDIA driver 610.88, RTX 4060 8 GB (about 3 GB of it held by the Windows desktop during the runs), Docker
Desktop on WSL 2. Everything runs in Docker; nothing is installed on the host. Companion lab of the Gemma Series
Parts 13-16 on The Stack Underflow.

## The questions

| Part | Question | Runner | Results |
|---|---|---|---|
| 13 | What context does Ollama give Gemma 4 on an 8 GB card, what happens to a longer prompt, and what `num_ctx` really fits per size and KV type? | `lab/p13.py` (P-DEF, P-TRUNC), `lab/p_fit.py` (P-FIT) | `out/p13/` |
| 14 | Five failures (4-digit multiplication, letter counts, today's date, after the cutoff, citations) and the fix for each | `lab/p14.py` | `out/p14/` |
| 15 | The model card's capability lines, each scored by code (OCR, charts, two images, tools, coding, multilingual, thinking, Ollama's JSON output, audio) | `lab/p15.py` | `out/p15/` |
| 16 | Needle recall by length and depth, 8-fact recall, prefill time | `lab/p16.py` | `out/p16/` |

Each `out/<part>/RESULTS.md` lists the exact commands, versions and digests; `*.jsonl` are the raw rows; the server log
of every run is in `out/logs/` (large logs are archived, see LAB-STATUS.md).

## Rules the code enforces

- Every row carries tag, digest, num_ctx, the KV cache type read back from the server log, MTP draft on/off,
  temperature, Ollama version and whether the model was freshly loaded (`lab/rows.py`; a row without them is not
  written).
- Every pass/fail is decided by a grader in `lab/graders.py` (exact text, values in JSON, unit tests, DOI resolve +
  title match, WER), all unit-tested in `tests/`.
- Counts that go on screen come from fresh loads; lab rows use temperature 0, seed 42; headline counts are also run at
  Google's recommended sampling (temperature 1.0, 5 runs, reported as a range).

## Run it

```bash
docker compose --profile tools build runner
scripts/lab.sh test offline tests/            # offline tests (no GPU)
scripts/stage1.sh                             # Part 13 (P-DEF, P-TRUNC, P-FIT f16 + q8_0)
scripts/stage2.sh                             # Parts 15 and 14
scripts/stage3.sh                             # Part 16
```

The model volume is external (`MODELS_VOLUME`, default `gemma-lab-models`); create it or point it at your own.
Haystack: Project Gutenberg #1342, fetched into `data/` (see `data/SOURCES.md`).

## Licence

Apache 2.0 (code). Gemma 4 is under its own licence (Apache 2.0 per Google's model card); the haystack and the
LibriVox clip are public domain.
