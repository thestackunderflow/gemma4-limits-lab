# One 128K load. The offload line is read from /film/server-live-K12.log (docker logs of this take; see run.sh).
. /lab/scripts/film13/lib.sh
FS=22
f_gpu
f_start
tmux split-window -v -l 30% -t %0; f_wait_ready 1 20
tmux split-window -h -l 55% -t %0; f_wait_ready 2 20
f_rec
f_run 1 "nvidia-smi --query-gpu=memory.used,memory.total --format=csv -l 1" 1 || true
f_run 0 "curl -s \$OLLAMA_HOST/api/generate -d '{\"model\":\"gemma4:e4b-it-q4_K_M\",\"prompt\":\"Say OK.\",\"stream\":false,\"think\":false,\"keep_alive\":\"2m\",\"options\":{\"num_ctx\":131072}}' | jq -r .response" 300
f_run 2 "ollama ps"
f_run 0 "grep offloaded /film/server-live-K12.log | tail -2"
sl_nap 3
f_end
ollama stop gemma4:e4b-it-q4_K_M || true
