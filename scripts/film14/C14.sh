# C14 (F16): the e4b citation rows (DOI checked by code), the Reformer row's real DOI title, counts per row; no model
. /lab/scripts/film13/lib.sh
FS=${FS:-24}
f_start; f_rec
f_run 0 "cd /lab/out/p14"
f_run 0 "jq -r 'select(.model==\"e4b\" and .section==\"cite\" and .temperature==0) | .citations[] | [(.line[:24]), .doi_resolves, .title_matches] | @tsv' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -r 'select(.model==\"e4b\" and .section==\"cite\" and .temperature==0) | .citations[1] | .line, .doi_title' cant.jsonl"
sl_nap 2
f_clear 0
f_run 0 "jq -c 'select(.section==\"cite\") | {model, temperature, n_listed, n_doi_resolves, n_title_matches}' cant.jsonl"
sl_nap 2
f_end
