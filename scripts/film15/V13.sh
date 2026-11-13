# V13 (F15, F16): E4B's capabilities, the eSpeak script line, one transcription of the lab's espeak.wav (as p15.aud).
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu; f_start; f_rec
r <<'X'
curl -s $OLLAMA_HOST/api/show -d '{"model":"gemma4:e4b-it-q4_K_M"}' | jq -c .capabilities
X
r <<'X'
grep -n "ESPEAK_TEXT =" /lab/lab/p15.py | fold -w 44
X
sl_nap 1.5
r 300 <<'X'
curl -s -F model=gemma4:e4b-it-q4_K_M -F "file=@/lab/out/p15/audio/espeak.wav;type=audio/wav" $OLLAMA_HOST/v1/audio/transcriptions | jq -r .text | fold -w 44
X
f_end
