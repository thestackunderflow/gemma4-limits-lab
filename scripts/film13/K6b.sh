. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "jq -c 'select(.endpoint==\"chat\" and .position==\"start\")' /lab/out/p13/trunc.jsonl | head -1 | jq -c '{status, reply_keys}'"
sl_nap 3
f_end
