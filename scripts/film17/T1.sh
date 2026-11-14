# T1 (F1, F2, F5): GPU line; turn 2 sent ALONE, live (lab body); the menu's share from results.json.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu
f_start
f_run 0 "cd /lab/out/g17"
f_run 0 "clear"
f_rec
r <<'X'
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader
X
r <<'X'
jq -r '.messages[1].content' /film/turn2-alone.json
X
r 300 <<'X'
curl -s $OLLAMA_HOST/api/chat -d @/film/turn2-alone.json | tee /tmp/o.json | jq -r .message.content | head -4 | cut -c1-44
X
cp /tmp/o.json "$O/reply.json"
sl_nap 3
f_clear 0
r <<'X'
jq .size.cube_no_tools results.json
X
r <<'X'
jq .size.cube_with_tools results.json
X
r <<'X'
jq .size.menu_tokens results.json
X
f_end
