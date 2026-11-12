#!/usr/bin/env bash
# Started by Windows Task Scheduler (task "gemma4-lab-tonight"), NOT by Claude Code, so Claude Code's low-memory
# reaper cannot stop it. Closes Chrome/Firefox first (owner GO 11 Nov: "GO lab tonight"), then runs the night chain.
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
echo "TONIGHT start $(date '+%F %T')" >> out/logs/night.out
docker info >/dev/null 2>&1 || { "/c/Program Files/Docker/Docker/Docker Desktop.exe" & for i in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 5; done; }
powershell -NoProfile -Command "foreach (\$n in 'chrome','firefox') { Get-Process -Name \$n -ErrorAction SilentlyContinue | ForEach-Object { [void]\$_.CloseMainWindow() } }; Start-Sleep 20; [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" > out/logs/browsers-closed-start.txt 2>&1
echo "$(date '+%F %T') tonight.sh: closed chrome+firefox at start; Windows free GB: $(tail -1 out/logs/browsers-closed-start.txt)" >> out/logs/safety.log
scripts/night.sh >> out/logs/night.out 2>&1
