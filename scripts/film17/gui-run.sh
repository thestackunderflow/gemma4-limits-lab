#!/usr/bin/env bash
# g17 GUI takes: scripts/film17/gui-run.sh TAKE CHAT_ID CTX FIX   (SolidCraft window + terminal strip, sc5-l5:0.28.0)
set -eu
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/../.."
LAB=$(pwd -W); CL=$(cd ../solidcraft-course-lab && pwd -W); SC=$(cd ../local-model-solidcraft-lab && pwd -W)
[ -e "out/g17/chats/$2/summary.json" ] && { echo "refusing: chat $2 exists"; exit 1; }
[ -d "out/g17/chats/$2" ] && mv "out/g17/chats/$2" "out/g17/partial/$2-$(date +%Y%m%dT%H%M%S)"
docker run --rm --privileged --network none gemma4-limits-lab-runner:1 sh -c "sync; echo 3 > /proc/sys/vm/drop_caches"; sleep 3
free=$(powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" | tr -d '\r')
echo "free RAM ${free} GB"; awk -v x="$free" 'BEGIN{exit !(x<3.0)}' && { echo "STOP: under 3 GB free"; exit 3; }
docker run --rm --name "g17-$1" --memory 4g --shm-size 1g --network container:gemma4-limits-ollama \
  -v "$CL:/work:ro" -v "$LAB:/g" -v "$SC:/sc:ro" sc5-l5:0.28.0 bash /g/scripts/film17/gui.sh "$@"
