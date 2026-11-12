# REUSE: the lab's archived server log (11 Nov rows), then the same WARN from this shoot's K5 take (docker logs copy).
. /lab/scripts/film13/lib.sh
f_start; f_rec
f_run 0 "grep -m1 'vram-based default context' /lab/out/logs/server-20261111T040329Z.log | fold -w 44"
sl_nap 2
f_run 0 "grep -m1 'truncating input prompt' /lab/out/logs/server-20261111T040329Z.log | fold -w 44"
sl_nap 2
f_clear 0
f_run 0 "grep -m1 'truncating input prompt' /film/server-live-K5.log | fold -w 44"
sl_nap 2
f_end
