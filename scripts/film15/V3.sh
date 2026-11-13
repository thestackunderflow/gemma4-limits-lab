# V3 (F5, S1): the 10 e4b OCR items at temp 0, the one miss (seed 1005, OOMKilled vs 00MKilled), the 12B count lines.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select(.model=="e4b" and .section=="ocr" and .temperature==0) | "\(.item)  \(.passed)"' can.jsonl
X
sl_nap 3
f_clear 0
r <<'X'
jq -c 'select(.model=="e4b" and .section=="ocr" and .passed==false) | {seed, want: .want[-12:], answer: .answer[-12:]}' can.jsonl
X
sl_nap 3
r <<'X'
jq -c 'select(.model=="12b-qat" and .section=="ocr") | [.temperature, .seed, .result]' can-summary.jsonl
X
sl_nap 3
f_end
