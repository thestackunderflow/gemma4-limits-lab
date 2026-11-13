# C10b (F12): E4B, date in the system prompt (lab: Tuesday)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -c '.messages[0]' /film/date-sys.json | fold -w 44"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/date-sys.json | jq -r .message.content" 180
f_end
