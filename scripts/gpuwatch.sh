#!/usr/bin/env bash
# Stand-alone copy of the sampler's GPU loop (used to restart it mid-stage).
set +e
cd "$(dirname "$0")/.."
name="$(cat out/samples/CURRENT)"
while [ ! -f out/samples/STOP ]; do
  echo "$(date +%s),$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ' \r' | head -1)" >> "out/samples/${name}.gpu.csv"
  sleep 1
done
