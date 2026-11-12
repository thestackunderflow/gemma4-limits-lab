. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "jq -r 'select(.model==\"12b-qat\" and .kind==\"speed\" and .kv_type==\"f16\") | [.num_ctx,(.offload|tostring),.write_tok_s] | @tsv' /lab/out/p13/fit.jsonl"
sl_nap 3
f_clear 0
f_run 0 "jq -r 'select(.model==\"12b-qat\" and .kind==\"max-fill\") | [.kv_type,.num_ctx,(.offload|tostring),.prefill_s,.write_tok_s] | @tsv' /lab/out/p13/fit.jsonl"
sl_nap 2
f_run 0 "jq -c 'select(.model==\"12b-qat\") | {model, offload}' /lab/out/p13/def.jsonl"
sl_nap 3
f_end
