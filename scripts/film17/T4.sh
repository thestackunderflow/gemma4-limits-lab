# T4 (pickup, F0/F9/F10/F12/F13/F14, Short S3/S4): jq lines on lab files only, no model call (HANDOVER-g17-render §1.2).
# Line 4 uses '[^.]*' (not '.*': the reply says "36mm" twice) and fold -s (word wrap, not mid-word).
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start
f_run 0 "cd /lab/out/g17/chats"
f_run 0 "clear"
f_rec
r <<'X'
jq -c '.filmed_fresh_runs["film-v1b-8k"].stale_values' ../results.json
X
f_clear 0
r <<'X'
jq .checker.spacing film-v2-32k/summary.json
X
r <<'X'
jq .checker.spacing film-v3-sum16k/summary.json
X
r <<'X'
jq -r .turn20_text film-v3-sum16k/summary.json | grep -o '24mm spacing[^.]*36mm' | fold -s -w 44
X
f_clear 0
r <<'X'
jq -c .fix.b_ctx_32k.reps_turn1_gone ../results.json
X
r <<'X'
jq -c '.fix.a_pin_16k|[.right_total,.recall8_chats]' ../results.json
X
r <<'X'
jq -c '.fix.c_summary_16k|[.right_total,.recall8_chats]' ../results.json
X
f_end
