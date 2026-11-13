# C9 (F10): E4B spell-first prompt (lab: Answer: 3)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r '.messages[0].content' /film/let-bookkeeper-spell.json | fold -w 44"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/let-bookkeeper-spell.json | jq -r .message.content" 180
f_end
