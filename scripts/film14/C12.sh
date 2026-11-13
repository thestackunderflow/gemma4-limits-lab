# C12 (F14): 12B, latest Ollama from memory (lab: 0.5.7)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r '.messages[0].content' /film/cut-ollama.json | fold -w 44"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/cut-ollama.json | jq -r .message.content" 240
f_end
