# C4 (F4): E4B think on (lab row 3979016, eval_count 488)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/mul00-think.json | tee /tmp/t.json | jq -r .message.thinking | head -3" 400
f_run 0 "jq -r .message.thinking /tmp/t.json | wc -l"
f_run 0 "jq -r '.message.content, .eval_count' /tmp/t.json"
cp /tmp/t.json "$O/reply.json"
f_end
