# V14 (F16): the LibriVox clip, e2b + e4b on both routes (answer tails), then the no-clip control replies.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start; f_rec
r <<'X'
cd /lab/out/p15
X
r <<'X'
jq -r 'select((.model=="e2b" or .model=="e4b") and .item=="librivox") | "\(.model) \(.route[0:12]): \(.answer[-40:])"' aud.jsonl | fold -w 44
X
sl_nap 3
f_clear 0
r <<'X'
jq -r 'select(.item=="no-clip-control" and (.model=="e2b" or .model=="e4b")) | .answer[0:80]' aud.jsonl | fold -w 44
X
sl_nap 3
f_end
