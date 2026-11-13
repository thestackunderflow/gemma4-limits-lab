# C13 (F14): the Gemma 4 model card, live; full window, then Find "cutoff date"
. /lab/scripts/film13/lib.sh
. /lab/scripts/film14/ff.sh
ff_open https://ai.google.dev/gemma/docs/core/model_card_4
sl_record "$O"; sl_mark "recording started"; sl_nap 3
sl_key ctrl+f "find bar"; sl_nap 0.8
sl_type "cutoff date" "find: cutoff date" 90; sl_key Return; sl_nap 5
ff_end
