# C6 (F7, S2): 12B tool call, then our code runs it and sends the result back (lab tool_loop)
. /lab/scripts/film13/lib.sh
f_gpu; f_start; f_rec
f_run 0 "jq -c '.model, .tools[0].function.name' /film/tool-12b.json"
f_run 0 "curl -s \$OLLAMA_HOST/api/chat -d @/film/tool-12b.json | tee /tmp/r1.json | jq -c '.message.tool_calls[0].function'" 240
f_run 0 'echo $((2824 * 1409))'
f_clear 0
f_run 0 "cat /film/send-result.sh"
f_run 0 "/film/send-result.sh 3979016" 240
cp /tmp/r1.json "$O/reply1.json"
f_end
