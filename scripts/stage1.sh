#!/usr/bin/env bash
# Stage 1 (Part 13), small models + 12B: P-DEF, P-TRUNC (f16 server), P-FIT f16 then q8_0 (server restarted per KV
# type), back to f16. The 26B rows run in stage1b (needs a larger container memory cap).
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
L=scripts/lab.sh
$L sampler start stage1
sleep 3
$L up f16 || exit 1
$L run p13 def --models e2b,e4b,12b-qat || exit 1
$L run p13 trunc --reps 3 || exit 1
$L run p_fit --kv f16 --models e2b,e4b,12b-qat || exit 1
$L up q8_0 || exit 1
$L run p_fit --kv q8_0 --models e2b,e4b,12b-qat || exit 1
$L up f16
$L sampler stop
echo STAGE1-DONE
