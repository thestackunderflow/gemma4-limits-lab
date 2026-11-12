#!/usr/bin/env bash
# Host side (Git Bash): free-RAM check, then one take in film13:1, foreground. Usage: scripts/film13/run.sh K5
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/../.."
LAB=$(pwd -W); KIT=$(cd ../screen-lab-kit && pwd -W)
# same as lab/common.py fresh(): drop the WSL VM page cache left by the last model read
docker run --rm --privileged --network none gemma4-limits-lab-runner:1 sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"; sleep 3
free=$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r')
echo "free RAM ${free} GB"
awk -v x="$free" 'BEGIN{exit !(x<4.0)}' && { echo "STOP: under 4 GB free"; exit 3; }
mkdir -p out/p13-film
# the running server tees to a server.log that was renamed on the host, so its live lines are read from docker logs
docker logs --since 1s -f gemma4-limits-ollama > "out/p13-film/server-live-$1.log" 2>&1 & LP=$!
docker run --rm --name film13 --network gemma4-moe-lab_default --gpus all --shm-size 1g \
  -e OLLAMA_HOST=http://gemma4-limits-ollama:11434 \
  -v "$KIT:/kit:ro" -v "$LAB:/lab:ro" -v "$LAB/out/p13-film:/film" \
  film13:1 bash "/lab/scripts/film13/$1.sh" "$1"
kill $LP 2>/dev/null || true
echo "free RAM after: $(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r') GB"
