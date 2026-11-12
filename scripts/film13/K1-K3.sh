. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "ollama --version"
f_run 0 "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"
f_clear 0
f_run 0 "ollama list"
sl_nap 1.5
f_run 0 "ollama list | grep gemma4"
f_end
