#!/usr/bin/env bash
# Task Scheduler entry (task gemma4-g18-lab): one battery file, log to out/logs/g18-<name>.log, then G18-DONE.
cd "$(dirname "$0")/.."
B=$1; N=$(basename "$B" .txt)
bash scripts/g18.sh battery "$B" >> "out/logs/g18-$N.log" 2>&1
echo "$(date +%H:%M:%S) G18-DONE $N" >> "out/logs/g18-$N.log"
