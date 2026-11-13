# V7b (F7): the pair01 row (want, answer), the question from lab/images.py, the pairs count lines.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="e4b" and .item=="pair01" and .temperature==0) | .want, .answer' can.jsonl
X
sl_nap 2
r <<'X'
grep -n "WORD-NUMBER" /lab/lab/images.py | fold -w 44
X
sl_nap 3
f_clear 0
r <<'X'
jq -c 'select(.section=="pairs") | [.model, .seed, .result]' can-summary.jsonl
X
sl_nap 3
f_end
