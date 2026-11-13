# V8 (F9): E4B with all 6 lab tools asks for multiply; our code runs it; the result goes back (lab tool_loop, mul1 row).
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu; f_start; f_rec
r <<'X'
jq -c '.model, [.tools[].function.name]' /film/tools-e4b.json
X
r 300 <<'X'
curl -s $OLLAMA_HOST/api/chat -d @/film/tools-e4b.json | tee /tmp/r1.json | jq -c '.message.tool_calls[0].function'
X
r <<'X'
echo $((4821 * 7293))
X
r 300 <<'X'
/film/send-result.sh 35159553 | fold -w 44
X
cp /tmp/r1.json "$O/reply1.json"
f_end
