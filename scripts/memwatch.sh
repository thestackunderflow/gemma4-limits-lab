#!/usr/bin/env bash
# Stand-alone copy of the sampler's RAM loop (used to restart it mid-stage).
set +e
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
name="$(cat out/samples/CURRENT)"
low=0
while [ ! -f out/samples/STOP ]; do
  m="$(docker stats --no-stream --format '{{.MemUsage}}' gemma4-limits-ollama 2>/dev/null | cut -d/ -f1 | tr -d ' ')"
  w="$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r')"
  echo "$(date +%s),${m:-NA},$w" >> "out/samples/${name}.mem.csv"
  if awk -v x="$w" 'BEGIN{exit !(x<1.0)}'; then low=$((low+1)); else low=0; fi
  if [ "$low" -ge 3 ]; then echo "$(date '+%F %T') STOP low RAM $w" >> out/logs/safety.log; docker stop gemma4-limits-ollama >/dev/null 2>&1; low=0; fi
  sleep 1
done
