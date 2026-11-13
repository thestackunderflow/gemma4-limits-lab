# V6 (F0, F6, S2): chart count lines, both models; rows within 5; the worst-off value over all 60 chart rows.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -c 'select(.section=="charts") | [.model, .temperature, .seed, .result]' can-summary.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
jq -s '[.[] | select(.section=="charts")] | {rows: length, within5: map(select(.within_5[0]==.within_5[1])) | length}' -c can.jsonl
X
sl_nap 2
r <<'X'
jq -s '[.[] | select(.section=="charts") | .answer as $a | ($a | gsub("```(json)?"; "") | fromjson) as $g | .want | to_entries[] | (($g[.key] - .value) | fabs)] | max' can.jsonl
X
sl_nap 3
f_end
