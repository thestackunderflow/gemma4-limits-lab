. /lab/scripts/film13/lib.sh
FS=24
f_gpu
f_start
tmux split-window -h -t %0; f_wait_ready 1 20; f_pane 0
f_rec
f_run 0 "ollama show gemma4:e4b-it-q4_K_M"
f_run 0 "ollama show gemma4:e4b-it-q4_K_M | grep -i context"
f_run 1 "ollama run gemma4:e4b-it-q4_K_M --keepalive 2m --think=false \"Say OK.\"" 120
f_run 1 "ollama ps"
sl_nap 2
f_end
ollama stop gemma4:e4b-it-q4_K_M || true
