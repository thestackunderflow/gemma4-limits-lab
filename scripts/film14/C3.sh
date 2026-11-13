# C3 (F0, F3, F4, F8, F9, F10, F12, F15, S1): the lab's saved rows, no model. Count lines cut to 44 columns.
. /lab/scripts/film13/lib.sh
f_start; f_rec
cd_lab="cd /lab/out/p14"
f_run 0 "$cd_lab"
f_run 0 "jq -r 'select(.model==\"e4b\" and .section==\"mul\" and .think==false and .temperature==0) | [.answer, .want, .passed] | @tsv' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -c 'select(.model==\"e4b\" and .section==\"mul\") | {think, fix, temp, passed}' cant-summary.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -s '[.[] | select(.model==\"e4b\" and .section==\"mul\" and .temperature==0 and .fix==null)] | group_by(.think) | map({think: .[0].think, median_s: (map(.seconds) | sort | .[length/2|floor])})' -c cant.jsonl"
f_run 0 "jq -s '[.[] | select(.model==\"e4b\" and .fix==\"calculator tool\")] | {rows: length, used: map(select(.used_tool)) | length}' -c cant.jsonl"
f_run 0 "jq -s '[.[] | select(.model==\"e4b\" and (.item==\"mul1\" or .item==\"mul2\"))] | {rows: length, multiply: map(select(.calls[0].name==\"multiply\")) | length}' -c ../p15/can.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -c 'select(.model==\"e4b\" and .section!=\"mul\" and .section!=\"cite\" and .temp==0) | {section, fix, passed, total}' cant-summary.jsonl"
sl_nap 2
f_end
