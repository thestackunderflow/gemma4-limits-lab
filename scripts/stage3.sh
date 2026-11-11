#!/usr/bin/env bash
# Stage 3: Part 16 needle data (e4b full range; 12b-qat to 128K).
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
L=scripts/lab.sh
$L sampler start stage3
sleep 3
docker ps --filter name=gemma4-limits-ollama -q | grep -q . || $L up f16
$L run p16 run --models e4b --lengths 4096,8192,16384,32768,65536,131072
$L run p16 run --models 12b-qat --lengths 4096,16384,32768,65536,131072 --extras 0
$L sampler stop
echo STAGE3-DONE
