# Fallback path: the 16K window set per request (no saved gemma4-e4b-16k model, see K8).
. /lab/scripts/film13/lib.sh
FS=24
f_gpu
f_start; f_rec
f_run 0 "curl -s \$OLLAMA_HOST/api/generate -d '{\"model\":\"gemma4:e4b-it-q4_K_M\",\"prompt\":\"Say OK.\",\"stream\":false,\"think\":false,\"keep_alive\":\"2m\",\"options\":{\"num_ctx\":16384}}' | jq -r .response" 120
f_run 0 "ollama ps"
sl_nap 2
f_end
ollama stop gemma4:e4b-it-q4_K_M || true
