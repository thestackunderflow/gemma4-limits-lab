# C15 (F17): doi.org has no resolver box on its home page (12 Nov), so the DOI is typed by hand into the
# address bar after doi.org/, then Enter: the DOI the model gave for "Reformer" lands on another paper
. /lab/scripts/film13/lib.sh
. /lab/scripts/film14/ff.sh
ff_open https://doi.org
sl_record "$O"; sl_mark "recording started"; sl_nap 3
sl_key ctrl+l "address bar"; sl_nap 0.6
sl_type "doi.org/10.48550/arXiv.2001.01210" "type the DOI" 90; sl_nap 0.8
sl_key Return "enter"; sleep ${LAND_WAIT:-10}; sl_mark "landed"; sl_nap 4
ff_end
