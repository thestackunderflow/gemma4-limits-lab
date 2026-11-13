# C12b (F15): 12B with the release page pasted (lab: v0.40.16)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r '.messages[0].content' /film/cut-ollama-paste.json | head -3"
f_run 0 "jq -r '.messages[0].content' /film/cut-ollama-paste.json | wc -l"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/cut-ollama-paste.json | jq -r .message.content" 240
f_end
