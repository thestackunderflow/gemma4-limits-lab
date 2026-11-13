# V1 (F0, F20): the OCR card in Firefox (full window 3 s), then E4B reads it through the API (lab body, ocr00 row).
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu
LOAD_WAIT=6 ff_open file:///lab/out/p15/images/ocr_00.png
sl_record "$O"; sl_mark "recording started"; sl_nap 3.5
f_term
r <<'X'
jq -r .model /film/ocr00.json
X
r 300 <<'X'
curl -s $OLLAMA_HOST/api/chat -d @/film/ocr00.json | tee /tmp/o.json | jq -r .message.content
X
cp /tmp/o.json "$O/reply.json"
f_end
