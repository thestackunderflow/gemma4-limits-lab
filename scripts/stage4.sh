#!/usr/bin/env bash
# Stage 4: the 26B rows (P-DEF, P-FIT f16 + q8_0, P-CAN tools, P-NEEDLE short set). Its CPU-side part needs more than
# the 12g cap, so the container gets 16g (OLLAMA_MEM_LIMIT) and the RAM watcher stays on.
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
L=scripts/lab.sh
export OLLAMA_MEM_LIMIT=16g
$L sampler start stage4
sleep 3
$L up f16
$L run p13 def --models 26b
$L run p_fit --kv f16 --models 26b
$L run p15 can --models 26b --sections tools
$L run p16 run --models 26b --lengths 4096,32768,131072 --extras 0
$L up q8_0
$L run p_fit --kv q8_0 --models 26b
$L up f16
$L sampler stop
echo STAGE4-DONE
