# V5 (F0, F6, S0): the chart in Firefox (full window 3 s), E4B reads the bars (lab body, chart04 row), the drawn values.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu
LOAD_WAIT=6 ff_open file:///lab/out/p15/images/chart_04.png
sl_record "$O"; sl_mark "recording started"; sl_nap 3.5
f_term
r 300 <<'X'
curl -s $OLLAMA_HOST/api/chat -d @/film/chart04.json | tee /tmp/c.json | jq -r .message.content
X
sl_nap 1.5
r <<'X'
jq -c 'select(.model=="e4b" and .item=="chart04" and .temperature==0) | .want' /lab/out/p15/can.jsonl
X
cp /tmp/c.json "$O/reply.json"
sl_nap 1.5
f_end
