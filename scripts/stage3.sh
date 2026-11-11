#!/usr/bin/env bash
# Stage 3: Part 15 headline counts at temp 1.0 (5 runs), then Part 16 needle data (e4b full range; 12b-qat to 128K).
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
L=scripts/lab.sh
$L sampler start stage3
sleep 3
docker ps --filter name=gemma4-limits-ollama -q | grep -q . || $L up f16
$L run p15 can --models e4b --temp 1.0 --reps 5
# 12B thinking at temp 0 alone took over 20 min (up to 8,192 thinking tokens at ~18 tok/s): its temp-1 runs skip it
$L run p15 can --models 12b-qat --temp 1.0 --reps 5 --sections ocr,charts,pairs,tools,coding,multilingual,json
$L run p16 run --models e4b --lengths 4096,8192,16384,32768,65536,131072
$L run p16 run --models 12b-qat --lengths 4096,16384,32768,65536,131072 --extras 0
$L sampler stop
echo STAGE3-DONE
