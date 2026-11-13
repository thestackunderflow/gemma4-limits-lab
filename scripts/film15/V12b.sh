# V12b (F14): 12b-qat thinking rows (eval_count near 8192, ~450 s each) and its off/on summary.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="12b-qat" and .section=="thinking") | "\(.item)  \(.think)  \(.eval_count)  \(.passed)  \(.seconds)"' can.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
jq -c 'select(.model=="12b-qat" and .section=="thinking") | .result' can-summary.jsonl
X
sl_nap 3
f_end
