# V9b (F10): same question, 6 tools vs P14's 1; P15 multiply counts vs P14 calculator-tool counts. No model.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
jq -r '.messages[0].content' /film/tools-e4b.json
X
r <<'X'
jq '.tools | length' /film/tools-e4b.json
X
r <<'X'
jq '.tools | length' /lab/out/p14-film/tool-e4b.json
X
sl_nap 2
f_clear 0
r <<'X'
jq -s '[.[] | select(.model=="e4b" and (.item=="mul1" or .item=="mul2"))] | {rows: length, multiply: map(select(.calls[0].name=="multiply")) | length}' -c /lab/out/p15/can.jsonl
X
r <<'X'
jq -s '[.[] | select(.model=="e4b" and .fix=="calculator tool")] | {rows: length, used: map(select(.used_tool)) | length}' -c /lab/out/p14/cant.jsonl
X
sl_nap 3
f_end
