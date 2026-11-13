# V7 (F7): the two pair images in Firefox, 3 s+ each (full window). No model.
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
LOAD_WAIT=6 ff_open file:///lab/out/p15/images/pair_01_a.png
sl_record "$O"; sl_mark "recording started"; sl_nap 4
sl_key ctrl+l "address bar"; sl_nap 0.5
sl_type "file:///lab/out/p15/images/pair_01_b.png" "url: pair_01_b.png" 45
sl_key Return "open"; sl_nap 4.5
ff_end
