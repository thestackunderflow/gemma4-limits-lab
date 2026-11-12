. /lab/scripts/film13/lib.sh
f_start; f_rec
for m in e2b e4b; do
  f_run 0 "jq -r 'select(.model==\"$m\" and .kind==\"speed\") | [.kv_type,.num_ctx,(.offload|tostring),.write_tok_s] | @tsv' /lab/out/p13/fit.jsonl"
  sl_nap 3
  [ $m = e2b ] && f_clear 0
done
f_end
