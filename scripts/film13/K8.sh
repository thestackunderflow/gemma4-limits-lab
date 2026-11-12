. /lab/scripts/film13/lib.sh
f_gpu
f_start; f_rec
f_pane 0; rm -f /tmp/ready.0
sl_type "ollama run gemma4:e4b-it-q4_K_M --think=false" "pane 0: ollama run" 45; sl_key Return
f_wait_text 0 '^>>> ' 120; sl_nap 1.5
sl_type "/set parameter num_ctx 16384" "set num_ctx" 45; sl_key Return
f_wait_text 0 "Set parameter" 20; sl_nap 1.5
sl_type "/save gemma4-e4b-16k" "save" 45; sl_key Return
f_wait_text 0 "(Created new model|save|Save|rror)" 60; sl_nap 1.5
sl_type "/bye" "bye" 45; sl_key Return
f_wait_ready 0 30; sl_nap 1.5
f_end
