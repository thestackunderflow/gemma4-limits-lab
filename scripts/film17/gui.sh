#!/bin/bash
# g17 GUI take (inside sc5-l5:0.28.0): SolidCraft 0.28.0 window on top, a terminal strip below (the course lab's fx15
# split layout, reused read-only from /work = solidcraft-course-lab), a FRESH design chat run live in the strip:
# Gemma 4 E4B on gemma4-limits-ollama drives the open SolidCraft window through `solidcraft-cli mcp`.
#   bash /g/scripts/film17/gui.sh TAKE CHAT_ID CTX FIX     (probe: TAKE=probe, no recording, one MCP call)
# Writes /g/out/g17-film/TAKE/{screen.mp4,events.jsonl,events.txt,cursor.jsonl,pane.txt,*.png}; the chat rows go to
# /g/out/g17/chats/CHAT_ID (same runner as the lab rows).
set -u
TAKE=$1; CID=${2:-}; CTX=${3:-}; FIX=${4:-none}
export O=/g/out/g17-film/$TAKE
[ -s "$O/events.txt" ] && { echo "refusing: $O/events.txt exists"; exit 1; }
mkdir -p "$O" /lab/out
. /work/lab/fx15lib.sh
O=/g/out/g17-film/$TAKE
setup split
sleep 2
if [ "$TAKE" = probe ]; then
  python3 - > "$O/probe.txt" 2>&1 <<'PY'
import sys; sys.path.insert(0, '/sc/harness')
from mcp_client import McpClient
m = McpClient(['solidcraft-cli', 'mcp', '--allow-path', '/lab/out']); m.start()
print(McpClient.text(m.call_tool('running', {}))[:600])
print(McpClient.text(m.call_tool('inspect_design', {}))[:400])
m.close()
PY
  shot "$O/probe.png"; cat "$O/probe.txt"; exit 0
fi
tmux send-keys -t t "cd /g && export G17_ROOT=/g G17_LIVE=1 OLLAMA=http://127.0.0.1:11434 SC_VERSION=0.28.0" Enter
tmux send-keys -t t "export OLLAMA_NUM_PARALLEL=1 OLLAMA_KV_CACHE_TYPE=f16; clear" Enter; sleep 1
rec_start
ev "recording started: full window (SolidCraft + terminal), hold 3 s"
nap 3.0
ev "chat starts: $CID num_ctx $CTX fix $FIX"
tt "python3 -m lab.g17run chat $CID $CTX $FIX false t0 42 5m | cut -c1-44"
ev "chat done"
nap 2.0; cp_shot after-chat
tt "clear"
tt "python3 scripts/film17/show.py $CID"
ev "results shown, hold 4 s"; nap 4.0; cp_shot results
pane
rec_stop
ev "recording stopped"
