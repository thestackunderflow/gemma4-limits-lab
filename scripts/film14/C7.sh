# C7 (F8, S3): E4B with the same tool (lab: no call, 3978816)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -r .model /film/tool-e4b.json"
f_run 0 "jq -r '.messages[0].content' /film/tool-e4b.json | fold -w 44"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/tool-e4b.json | jq -c '.message.tool_calls, .message.content'" 180
f_end
