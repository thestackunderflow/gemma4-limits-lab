# T2 (F4, F6): turn 2 WITH the list (the lab's 16K chat), tokens sent vs reused per turn; the 8K drop turn + the cut line.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start
cd /lab/out/g17/chats
f_rec
r <<'X'
jq -c 'select(.turn==2)|.tool_calls[0].arguments' drop-16k-t0/requests.jsonl | head -1
X
r <<'X'
jq -r '.reuse["drop-16k-t0"].all.reused_pct' ../results.json
X
r <<'X'
jq -c 'select(.turn<=4)|[.turn,.prompt_eval_count,.prompt_eval_cached_count]' drop-16k-t0/requests.jsonl | tail -4
X
f_clear 0
r <<'X'
jq .drop["8k"].turn1_gone_turn ../results.json
X
r <<'X'
jq -c 'select(.cuts!=[])|[.turn,.cuts[0].kind]' drop-8k-t0/requests.jsonl | head -1
X
r <<'X'
jq -c '[.status,.done_reason]' drop-8k-t0/requests.jsonl | sort | uniq -c
X
f_end
