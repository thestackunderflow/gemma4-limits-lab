#!/usr/bin/env bash
# g17 terminal takes (copy of scripts/film15/run.sh: film13:1 image + scripts/film13/lib.sh, output out/g17-film).
#   scripts/film17/run.sh T1          GUI takes: scripts/film17/gui-run.sh
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/../.."
LAB=$(pwd -W); KIT=$(cd ../screen-lab-kit && pwd -W)
docker run --rm --privileged --network none gemma4-limits-lab-runner:1 sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"; sleep 3
free=$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r')
echo "free RAM ${free} GB"
awk -v x="$free" 'BEGIN{exit !(x<3.0)}' && { echo "STOP: under 3 GB free"; exit 3; }
mkdir -p out/g17-film
S=$(date +%s)
docker run --rm --name film17 --network gemma4-moe-lab_default --gpus all --shm-size 1g \
  -e OLLAMA_HOST=http://gemma4-limits-ollama:11434 \
  -v "$KIT:/kit:ro" -v "$LAB:/lab:ro" -v "$LAB/out/g17-film:/film" \
  film13:1 bash "/lab/scripts/film17/$1.sh" "$1"
docker logs --since "$S" --until "$(date +%s)" gemma4-limits-ollama > "out/g17-film/server-live-$1.log" 2>&1 || true
