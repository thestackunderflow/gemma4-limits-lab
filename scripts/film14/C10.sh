# C10 (F11): E4B, no date given (lab: a decline)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r '.messages[-1].content' /film/date-none.json | fold -w 44"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/date-none.json | jq -r .message.content | fold -w 44" 180
f_end
