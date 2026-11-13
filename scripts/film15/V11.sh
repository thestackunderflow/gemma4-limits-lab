# V11 (F12): multilingual rows (language code, want, answer, passed; numbers only, no hi/ja text), es2, counts.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="e4b" and .section=="multilingual" and .temperature==0) | "\(.lang)  \(.want)  \(.answer)  \(.passed)"' can.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
grep -n "Tengo 3 cajas" /lab/lab/tasks.py | fold -w 44
X
r <<'X'
jq -r 'select(.model=="e4b" and .item=="es2" and .temperature==0) | .answer' can.jsonl
X
sl_nap 2
f_clear 0
r <<'X'
jq -c 'select(.section=="multilingual") | [.model, .seed, .result]' can-summary.jsonl
X
sl_nap 3
f_end
