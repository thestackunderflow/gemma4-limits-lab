# V10 (F11): the merge_intervals answer (first 8 lines), the 10 e4b coding items at temp 0, the one failing row, counts.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="e4b" and .item=="code_merge_intervals" and .temperature==0) | .answer' can.jsonl | head -8
X
sl_nap 3
f_clear 0
r <<'X'
jq -r 'select(.model=="e4b" and .section=="coding" and .temperature==0) | "\(.item[5:])  \(.tests_passed)/\(.tests_total)"' can.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
jq -c 'select(.section=="coding" and .passed==false) | {model, seed, item, tests_passed, tests_total, last_error}' can.jsonl
X
sl_nap 2
r <<'X'
jq -c 'select(.section=="coding") | [.model, .seed, .result]' can-summary.jsonl
X
sl_nap 3
f_end
