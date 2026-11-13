#!/usr/bin/env bash
# Part 15: copy of scripts/film14/run.sh (output out/p15-film, takes scripts/film15/Vn.sh; same film13:1 image + lib.sh)
# Host side (Git Bash): free-RAM check, then one take in film13:1, foreground. Usage: scripts/film15/run.sh V1
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/../.."
LAB=$(pwd -W); KIT=$(cd ../screen-lab-kit && pwd -W)
# same as lab/common.py fresh(): drop the WSL VM page cache left by the last model read
docker run --rm --privileged --network none gemma4-limits-lab-runner:1 sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"; sleep 3
free=$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r')
echo "free RAM ${free} GB"
awk -v x="$free" 'BEGIN{exit !(x<4.0)}' && { echo "STOP: under 4 GB free"; exit 3; }
mkdir -p out/p15-film
# server lines for this take: read once after the take. (P13 followed with `docker logs -f &` + kill, but under Git Bash
# the kill does not reach docker.exe, so every follower kept appending until the container went away.)
S=$(date +%s)
docker run --rm --name film15 --network gemma4-moe-lab_default --gpus all --shm-size 1g \
  -e OLLAMA_HOST=http://gemma4-limits-ollama:11434 \
  -v "$KIT:/kit:ro" -v "$LAB:/lab:ro" -v "$LAB/out/p15-film:/film" \
  film13:1 bash "/lab/scripts/film15/$1.sh" "$1"
docker logs --since "$S" --until "$(date +%s)" gemma4-limits-ollama > "out/p15-film/server-live-$1.log" 2>&1 || true
echo "free RAM after: $(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r') GB"
