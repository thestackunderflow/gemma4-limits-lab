. /lab/scripts/film13/lib.sh
f_gpu
f_start; f_rec
f_run 0 "jq -c '.options, .truncate' /film/req-trunc-false.json"
f_run 0 "curl -s -o /tmp/r.json -w '%{http_code}\n' \$OLLAMA_HOST/api/chat -d @/film/req-trunc-false.json" 120
f_run 0 "jq -r .error /tmp/r.json"
sl_nap 2
f_end
cp /tmp/r.json "$O/response.json"
