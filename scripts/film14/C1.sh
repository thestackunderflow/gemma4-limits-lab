# C1 (F0, S0): E4B, think off, temperature 0 (lab row e4b mul00 = 3978816)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r '.model, .messages[0].content' /film/mul00.json"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/mul00.json | jq -r .message.content" 180
f_run 0 'echo $((2824 * 1409))'
f_end
