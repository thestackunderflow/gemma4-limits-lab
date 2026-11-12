. /lab/scripts/film13/lib.sh
f_gpu
f_start; f_rec
f_run 0 "wc -w /film/vault-start.txt"
f_run 0 "head -c 40 /film/vault-start.txt"
f_run 0 "tail -1 /film/vault-start.txt; echo"
f_run 0 "ollama run gemma4:e4b-it-q4_K_M --verbose --think=false < /film/vault-start.txt" 240
sl_nap 2
f_end
