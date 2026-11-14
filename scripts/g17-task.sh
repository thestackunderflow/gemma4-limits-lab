#!/usr/bin/env bash
# Task Scheduler entry (task gemma4-g17-lab): one battery file, log to out/logs/g17-<name>.log, then G17-DONE.
cd "$(dirname "$0")/.."
B=$1; N=$(basename "$B" .txt)
bash scripts/g17.sh battery "$B" >> "out/logs/g17-$N.log" 2>&1
echo "$(date +%H:%M:%S) G17-DONE $N" >> "out/logs/g17-$N.log"
