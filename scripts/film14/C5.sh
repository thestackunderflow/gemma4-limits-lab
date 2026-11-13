# C5 (F5, F7): 12B thinking rows and tool rows from the lab file, no model
. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "cd /lab/out/p14"
f_run 0 "jq -r 'select(.model==\"12b-qat\" and .section==\"mul\" and .think==true) | [.item, .eval_count, .passed, .seconds] | @tsv' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -s '[.[] | select(.model==\"12b-qat\" and .think==true and .eval_count==8156)] | length' cant.jsonl"
f_run 0 "jq -s '[.[] | select(.model==\"12b-qat\" and .fix==\"calculator tool\")] | {rows: length, used: map(select(.used_tool)) | length, right: map(select(.passed)) | length}' -c cant.jsonl"
sl_nap 2
f_end
