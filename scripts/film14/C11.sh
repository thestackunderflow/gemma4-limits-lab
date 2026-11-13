# C11 (F11, F14) + C11b + C12a: 12B date rows, the e4b year row, 12B cutoff rows, the release file; no model
. /lab/scripts/film13/lib.sh
FS=${FS:-24}
f_start; f_rec
f_run 0 "cd /lab/out/p14"
f_run 0 "jq -r 'select(.model==\"12b-qat\" and .section==\"dates\" and .fix==null) | [.item, .answer[-24:]] | @tsv' cant.jsonl"
f_run 0 "jq -r 'select(.model==\"e4b\" and .item==\"year\" and .temperature==0 and .fix==null) | [.item, .answer[-24:]] | @tsv' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -r 'select(.model==\"12b-qat\" and .section==\"cutoff\" and .fix==null) | [.item, .answer[-20:], .want] | @tsv' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -r '.ollama.tag, .ollama.fetched' sources/releases.json"
sl_nap 2
f_end
