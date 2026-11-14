# T3 (F9, F10, F11): the three fixes from results.json, one line each; the 15-line check script in three 5-line
# chunks, then run on E4B (prediction card is the render's).
. /lab/scripts/film13/lib.sh
. /lab/scripts/film15/ff.sh
f_start
f_run 0 "cd /lab/out/g17"
f_run 0 "clear"
f_rec
for a in a_pin_8k b_ctx_32k c_summary_8k; do
r <<X
jq -c '.fix.$a|[.right_total,.chats,.mean_tokens_per_turn_all]' results.json
X
done
r <<'X'
jq -r .winner.arm results.json
X
f_clear 0
r <<'X'
cd /lab/check
X
r <<'X'
sed -n 1,5p g17_reuse.py
X
sl_nap 3; f_clear 0
r <<'X'
sed -n 6,10p g17_reuse.py | cut -c1-44
X
sl_nap 3; f_clear 0
r <<'X'
sed -n 11,15p g17_reuse.py | cut -c1-44
X
sl_nap 3; f_clear 0
r 300 <<'X'
python3 g17_reuse.py | head -3
X
f_end
