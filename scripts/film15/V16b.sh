# V16b (F20 fix): V16 exactly, but `ollama run --think=false` (0.40.16 CLI default turns thinking on), then diff -wB.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_gpu; f_start; f_rec
r <<'X'
cp /lab/out/p15/images/ocr_00.png /tmp/my.png
X
r <<'X'
cat /film/want-ocr00.txt
X
r 300 <<'X'
ollama run --think=false gemma4:e4b-it-q4_K_M "Transcribe all the text in this image exactly as written, keeping the line breaks. Output only the text. /tmp/my.png" | tee /tmp/got.txt
X
r <<'X'
diff -wB /film/want-ocr00.txt /tmp/got.txt
X
cp /tmp/got.txt "$O/got.txt"
sl_nap 1.5
f_end
