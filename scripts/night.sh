#!/usr/bin/env bash
# Unattended rest of the 10-11 Nov lab night: after stage 2, free Windows RAM for the 26B stage (Part 13 rows first),
# (owner allowed closing apps: Chrome and Firefox are closed gracefully, both restore their tabs on the next start),
# run stage 4, then stage 3 (Part 15 temp-1 runs, Part 16 needle), write the reports, archive large logs to E:, commit locally, restart the containers stopped for the lab.
set -u
export MSYS_NO_PATHCONV=1
cd "$(dirname "$0")/.."
scripts/stage2b.sh > out/logs/stage2.out 2>&1
# The 26B stage needs the browsers closed; only do that while the owner is asleep (local time before 07:00).
if [ "$(date +%H)" -lt 7 ]; then
  powershell -NoProfile -Command "foreach (\$n in 'chrome','firefox') { Get-Process -Name \$n -ErrorAction SilentlyContinue | ForEach-Object { [void]\$_.CloseMainWindow() } }; Start-Sleep 20; [math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1MB,2)" > out/logs/browsers-closed.txt 2>&1
  echo "closed chrome+firefox gracefully at $(date '+%F %T'); Windows free GB after: $(tail -1 out/logs/browsers-closed.txt)" >> out/logs/safety.log
  scripts/stage4.sh > out/logs/stage4.out 2>&1
else
  echo "stage 4 (26B) skipped: stage 2 ended at $(date '+%F %T') local, after 07:00 (browsers not closed while the owner may be using the PC)" | tee out/logs/stage4.out >> out/logs/safety.log
fi
scripts/stage3.sh > out/logs/stage3.out 2>&1
docker compose --profile tools run --rm -T runner python -m lab.report > out/logs/report.out 2>&1
# archive: every server log goes to E:, logs over 5 MB leave the repo (a pointer file stays)
A="/e/2026-SomaPersonal/StackUnderflow-archive/gemma4-limits-lab"
mkdir -p "$A/logs" && cp -f out/logs/*.log "$A/logs/" 2>/dev/null
for f in out/logs/server*.log; do
  if [ "$(stat -c %s "$f")" -gt 5000000 ]; then
    echo "$(basename "$f") $(sha256sum "$f" | cut -c1-64) $(stat -c %s "$f") bytes -> E:\2026-SomaPersonal\StackUnderflow-archive\gemma4-limits-lab\logs\\" >> out/logs/ARCHIVED.txt
    rm -f "$f"
  fi
done
git add -A && git commit -qm "Lab night 10-11 Nov: stages 1-4 rows, reports (automatic commit by scripts/night.sh)"
docker start mcp-canvas-mcp-server-1 katha-kokoro >/dev/null 2>&1
echo "NIGHT-DONE $(date '+%F %T')" >> out/logs/night.out
