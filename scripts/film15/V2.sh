# V2 (F4): the lab's ocr00 row (want = answer, passed) and the e4b OCR count lines. No model.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -c 'select(.model=="e4b" and .section=="ocr" and .temperature==0 and .item=="ocr00") | {want, answer, passed}' can.jsonl | fold -w 44
X
sl_nap 3
r <<'X'
jq -c 'select(.model=="e4b" and .section=="ocr") | {temperature, seed, result}' can-summary.jsonl
X
sl_nap 3
f_end
