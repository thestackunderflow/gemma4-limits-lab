# V8b (F9, S1): tool-call count lines, both models, 6 seeds each.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -c 'select(.section=="tools") | [.model, .seed, .result]' can-summary.jsonl
X
sl_nap 4
f_end
