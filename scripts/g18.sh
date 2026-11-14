#!/usr/bin/env bash
# g18 host driver (Git Bash). Each step runs in a fresh sc5-app:0.28.0 container (SolidCraft 0.28.0 + python3) on the
# Ollama container's network. Nothing is installed on the host.
#   scripts/g18.sh job ID ARM JOB SAMPLING SEED
#   scripts/g18.sh battery FILE          one job run per line (same 5 fields, lab/g18jobs.battery); done runs
#                                        (summary.json) are skipped, a partial run folder goes to out/g18/partial/
# Guards: out/STOP stops; Windows free RAM >= 3 GB (plan stop rule: 2 GB) (after a VM page-cache drop) and C: >= 8 GB before every step.
set -uo pipefail
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
LAB=$(pwd -W); SC=$(cd ../local-model-solidcraft-lab && pwd -W)
OLLAMA_CT=gemma4-limits-ollama
mkdir -p out/g18/runs out/g18/partial out/logs
# one driver at a time (14 Nov: `schtasks /end` left a first battery alive and two ran at once)
mkdir out/g18/LOCK 2>/dev/null || { echo "out/g18/LOCK exists: another g18 driver runs"; exit 7; }
trap 'rmdir out/g18/LOCK' EXIT

say() { echo "$(date +%H:%M:%S) $*"; }
free_gb() { powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r'; }
cfree_gb() { df -BG /c | awk 'NR==2{gsub("G","",$4); print $4}'; }
guard() {
  [ -e out/STOP ] && { say "out/STOP: stopped"; exit 4; }
  docker run --rm --privileged --network none gemma4-limits-lab-runner:1 sh -c "sync; echo 3 > /proc/sys/vm/drop_caches" >/dev/null 2>&1
  for _ in $(seq 1 20); do
    f=$(free_gb); awk -v x="$f" 'BEGIN{exit !(x>=3.0)}' && break
    say "free RAM $f GB under 3: waiting"; sleep 30
  done
  awk -v x="$(free_gb)" 'BEGIN{exit !(x>=3.0)}' || { say "STOP: free RAM stayed under 3 GB"; exit 5; }
  for _ in $(seq 1 20); do [ "$(cfree_gb)" -ge 8 ] && break; say "C: $(cfree_gb) GB under 8: waiting"; sleep 30; done
  [ "$(cfree_gb)" -ge 8 ] || { say "STOP: C: stayed under 8 GB"; exit 6; }
}
NP=$(docker inspect "$OLLAMA_CT" -f '{{range .Config.Env}}{{println .}}{{end}}' | grep OLLAMA_NUM_PARALLEL | cut -d= -f2)
KV=$(docker inspect "$OLLAMA_CT" -f '{{range .Config.Env}}{{println .}}{{end}}' | grep OLLAMA_KV_CACHE_TYPE | cut -d= -f2)

run() {   # $1 = /lab/out host folder, rest = g18run args
  local files=$1; shift
  mkdir -p "$files"
  docker run --rm --network "container:$OLLAMA_CT" --memory 2g --memory-swap 2g \
    -e OLLAMA=http://127.0.0.1:11434 -e OLLAMA_NUM_PARALLEL="$NP" -e OLLAMA_KV_CACHE_TYPE="$KV" -e SC_VERSION=0.28.0 \
    -e PYTHONDONTWRITEBYTECODE=1 -v "$LAB:/work" -v "$SC:/sc:ro" -v "$(cd "$files" && pwd -W):/lab/out" -w /work \
    sc5-app:0.28.0 python3 -m lab.g18run "$@"
}

job() {
  local id=$1 d=out/g18/runs/$1
  [ -e "$d/summary.json" ] && { say "skip $id (done)"; return 0; }
  [ -d "$d" ] && { mv "$d" "out/g18/partial/$id-$(date +%Y%m%dT%H%M%S)"; say "partial $id set aside"; }
  guard
  say "job $*"
  run "$d/files" job "$@" | tail -1
}

case "${1:-}" in
  job) shift; job "$@" ;;
  battery)
    while read -r id rest; do
      [ -z "$id" ] || [ "${id:0:1}" = "#" ] && continue
      job "$id" $rest
    done < "$2"
    say "BATTERY-DONE $2" ;;
  *) echo "usage: see the header"; exit 2 ;;
esac
