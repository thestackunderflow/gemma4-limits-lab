# C8 (F9) + C9a: the real tokenizer pieces, then the e4b bookkeeper row, from the lab files; no model
. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "cd /lab/out/p14"
for w in bookkeeper strawberry "4821 × 7293"; do
  f_run 0 "jq -r 'first(.items[] | select(.text==\"$w\")) | .text + \" → \" + ([.tokens[].piece] | join(\" · \"))' tokenizer-dump.json"
  sl_nap 1.5
done
f_clear 0
f_run 0 "jq -c 'select(.model==\"e4b\" and .item==\"let_bookkeeper\" and .temperature==0 and .fix==null) | {answer, want, passed}' cant.jsonl"
sl_nap 2
f_end
