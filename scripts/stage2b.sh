#!/usr/bin/env bash
# Stage 2b: the rest of stage 2 after the RAM watcher stopped Ollama at 00:58 local (Windows 0.98 GB free during the
# 12B thinking section; Chrome + Firefox were then closed): P15 12b-qat thinking + json, P14 runs, tokenizer dump.
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
L=scripts/lab.sh
$L sampler start stage2b
sleep 3
$L up f16
$L run p15 can --models 12b-qat --sections thinking,json
$L run p14 run --models e4b --t1reps 5
$L run p14 run --models 12b-qat --t1reps 0
BLOB=$(docker exec gemma4-limits-ollama sh -c 'cat /root/.ollama/models/manifests/registry.ollama.ai/library/gemma4/e4b-it-q4_K_M' | python -c "import sys,json;print([l['digest'] for l in json.load(sys.stdin)['layers'] if l['mediaType'].endswith('.model')][0].replace(':','-'))")
docker rm -f gemma4-limits-tok >/dev/null 2>&1
docker run -d --name gemma4-limits-tok --network gemma4-moe-lab_default --memory 8g --gpus all -v gemma-lab-models:/models:ro \
  ghcr.io/ggml-org/llama.cpp:server-cuda-b11706@sha256:b01e2d9a95a4d2d27b1d74e0b6668da9cff2e050b9ea53b2b549652d6098c6f0 \
  -m "/models/models/blobs/$BLOB" --host 0.0.0.0 --port 8080 -ngl 0 -c 512 --no-warmup
for _ in $(seq 1 120); do docker logs gemma4-limits-tok 2>&1 | grep -q "server is listening" && break; sleep 2; done
docker logs gemma4-limits-tok 2>&1 | tail -3 > out/logs/tokenizer-server.log
$L run p14 tokens --url http://gemma4-limits-tok:8080
docker rm -f gemma4-limits-tok >/dev/null 2>&1
$L sampler stop
echo STAGE2-DONE
