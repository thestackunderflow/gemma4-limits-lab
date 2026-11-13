# V14b (F17, S3): the 12B LibriVox tails ("must be in want of a wife"), the e4b tail beside it, the 12B eSpeak lines.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select((.model=="12b-qat" or .model=="12b-q4") and .item=="librivox") | "\(.model) \(.route[0:12]):", .answer[-60:]' aud.jsonl | fold -w 44
X
sl_nap 2
r <<'X'
jq -r 'select(.model=="e4b" and .item=="librivox" and .route=="/api/chat images field") | "e4b \(.route[0:12]):", .answer[-60:]' aud.jsonl | fold -w 44
X
sl_nap 3
f_clear 0
r <<'X'
jq -r 'select((.model=="12b-qat" or .model=="12b-q4") and .item=="espeak") | "\(.model) \(.route[0:12]): \(.answer)"' aud.jsonl | fold -w 44
X
sl_nap 3
f_end
