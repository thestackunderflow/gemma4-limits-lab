. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "grep -n 'FLASH_ATTENTION\|KV_CACHE_TYPE' /lab/compose.yaml"
sl_nap 2
f_run 0 "grep -m1 'K (q8_0)' /lab/out/logs/server-20261111T052301Z.log | fold -w 44"
sl_nap 2
f_clear 0
f_run 0 "jq -r 'select(.model==\"e4b\" and .kind==\"max-fill\" and .num_ctx==131072) | [.kv_type,.prefill_s,.write_tok_s,(.offload|tostring)] | @tsv' /lab/out/p13/fit.jsonl"
sl_nap 3
f_run 0 "jq -r 'select(.model==\"e4b\" and .kind==\"speed\" and .num_ctx==131072) | [.kv_type,.write_tok_s,.prefill_tok_s] | @tsv' /lab/out/p13/fit.jsonl"
sl_nap 3
f_end
