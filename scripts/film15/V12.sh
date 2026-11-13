# V12 (F13): e4b thinking rows (off / on), the remainder row that ran out at 1024, the count and seconds lines.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="e4b" and .section=="thinking" and .temperature==0) | "\(.item)  \(.think)  \(.passed)  \(.seconds)"' can.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
jq -c 'select(.model=="e4b" and .item=="remainder" and .think==false and .temperature==0) | {eval_count, passed}' can.jsonl
X
r <<'X'
jq -c 'select(.model=="e4b" and .section=="thinking" and .temperature==0) | .result' can-summary.jsonl
X
sl_nap 2
r <<'X'
jq -c 'select(.model=="e4b" and .section=="thinking") | [.temperature, .seed, .result.off.passed, .result.on.passed]' can-summary.jsonl
X
sl_nap 3
f_end
