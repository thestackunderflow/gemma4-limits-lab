# Fallback path (SHOTLIST §3): /save failed in K8, so the 16K window goes in the request, as the lab did.
. /lab/scripts/film13/lib.sh
f_gpu
jq -c 'del(.truncate) | .options.num_ctx = 16384' /film/req-trunc-false.json > /film/req-16k.json
f_start; f_rec
f_run 0 "jq -c .options /film/req-16k.json"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/req-16k.json | jq '.prompt_eval_count, .message.content'" 180
sl_nap 2
f_clear 0
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/req-16k.json | jq '.prompt_eval_count, .message.content'" 180
sl_nap 2
f_end
