. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "jq -c 'select(.model==\"26b\") | {kv_type,num_ctx,write_tok_s,error}' /lab/out/p13/fit.jsonl"
sl_nap 3
f_run 0 "grep STOP /lab/out/logs/safety.log | tail -3"
sl_nap 3
f_end
