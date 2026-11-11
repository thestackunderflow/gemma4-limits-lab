#!/usr/bin/env bash
# Host-side driver (Git Bash on Windows). Everything heavy runs in containers; the host only runs docker and
# nvidia-smi (VRAM sampler: under WSL the per-process GPU view is unsupported, so VRAM is read on the Windows side).
#   scripts/lab.sh up [f16|q8_0]           (re)create the Ollama container (KV cache type is a server-wide setting)
#   scripts/lab.sh sampler start|stop      nvidia-smi + docker stats every ~2 s -> out/samples/<run>.csv
#   scripts/lab.sh test <name> [args]      pytest in the runner, tee to out/<name>.log
#   scripts/lab.sh run <module> [args]     python -m lab.<module> in the runner, tee to out/logs/<module>.log
set -euo pipefail
export MSYS_NO_PATHCONV=1
LAB="$(cd "$(dirname "$0")/.." && pwd)"
cd "$LAB"
RUN=(docker compose --profile tools run --rm -T runner)
OLLAMA=gemma4-limits-ollama
mkdir -p out/logs out/samples

wait_ready() {
  for _ in $(seq 1 120); do
    if docker exec "$OLLAMA" /bin/ollama ps >/dev/null 2>&1; then return 0; fi
    sleep 1
  done
  echo "ollama did not become ready" >&2; return 1
}

windows_free_gb() {
  powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r'
}

case "${1:-}" in
  up)
    kv="${2:-f16}"
    # keep the previous server log under its own name, start a fresh one
    if [ -f out/logs/server.log ]; then mv out/logs/server.log "out/logs/server-$(date -u +%Y%m%dT%H%M%SZ).log"; fi
    OLLAMA_KV_CACHE_TYPE="$kv" docker compose up -d --force-recreate ollama
    wait_ready
    echo "$kv" > out/logs/KV_TYPE_SET
    ;;
  sampler)
    case "${2:-}" in
      start)
        # two loops: GPU every ~1 s (nvidia-smi is fast), container RAM + Windows free every ~4 s (slow commands)
        name="${3:-run}"
        rm -f out/samples/STOP
        echo "epoch,gpu_mem_used_mib,gpu_util_pct" > "out/samples/${name}.gpu.csv"
        echo "epoch,ollama_mem,windows_free_gb" > "out/samples/${name}.mem.csv"
        (
          while [ ! -f out/samples/STOP ]; do
            echo "$(date +%s),$(nvidia-smi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits | tr -d ' \r' | head -1)" >> "out/samples/${name}.gpu.csv"
            sleep 1
          done
        ) > /dev/null 2>&1 &
        (
          low=0
          while [ ! -f out/samples/STOP ]; do
            m="$(docker stats --no-stream --format '{{.MemUsage}}' "$OLLAMA" 2>/dev/null | cut -d/ -f1 | tr -d ' ')"
            w="$(windows_free_gb)"
            echo "$(date +%s),${m:-NA},$w" >> "out/samples/${name}.mem.csv"
            # owner rule: keep Windows above 1 GB free; stop the lab container if it stays under for 3 samples
            if awk -v x="$w" 'BEGIN{exit !(x<1.0)}'; then low=$((low+1)); else low=0; fi
            if [ "$low" -ge 3 ]; then echo "$(date '+%F %T') STOP low RAM $w" >> out/logs/safety.log; docker stop "$OLLAMA" >/dev/null 2>&1; low=0; fi
            sleep 1
          done
        ) > /dev/null 2>&1 &
        echo "$name" > out/samples/CURRENT
        ;;
      stop) touch out/samples/STOP ;;
    esac
    ;;
  test)
    name="$2"; shift 2
    "${RUN[@]}" python -m pytest -q "$@" 2>&1 | tee "out/${name}.log"
    ;;
  run)
    mod="$2"; shift 2
    "${RUN[@]}" python -m "lab.$mod" "$@" 2>&1 | tee -a "out/logs/${mod}.log"
    ;;
  *) echo "usage: see header" >&2; exit 2 ;;
esac
