. /lab/scripts/film13/lib.sh
FS=20
f_start; f_rec
f_run 0 "ollama ps"
f_run 0 "nvidia-smi"
sl_nap 3
f_end
