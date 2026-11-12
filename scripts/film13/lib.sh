# Part 13 filming helpers (inside film13:1). Reuses the screen-lab kit (/kit/lib/screenlab.sh): Xvfb 1920x1080,
# 30 fps CRF 14 recorder, T0 from -debug_ts. One xterm (DejaVu Sans Mono 30 = about 44 columns in a 1080 crop)
# running tmux (status bar off) so a take can read its own panes back as text (pane-N.txt = the verification copy).
set -eu
. /kit/lib/screenlab.sh
SHOT=$1
O=/film/$SHOT
rm -rf "$O"; mkdir -p "$O"
export OLLAMA_HOST=${OLLAMA_HOST:-http://gemma4-limits-ollama:11434}

cat > /tmp/rc <<'EOF'
PS1='$ '
PROMPT_COMMAND='touch /tmp/ready.${TMUX_PANE#%}'
export OLLAMA_HOST
EOF
cat > /tmp/tmux.conf <<'EOF'
set -g status off
set -g default-terminal "xterm-256color"
set -g default-command "bash --rcfile /tmp/rc"
set -g history-limit 20000
set -g pane-border-style fg=colour250
set -g pane-active-border-style fg=colour250
EOF

f_start() {      # f_start: display, xterm + tmux (pane %0), wait for the first prompt
  sl_display 1920 1080
  sl_app /tmp/xterm.log xterm -T film13 -fa "DejaVu Sans Mono" -fs ${FS:-30} -bg white -fg black \
    -e tmux -f /tmp/tmux.conf new -s f
  sl_wait_window film13 20 > /dev/null
  sl_maximise film13
  f_wait_ready 0 20
  xdotool mousemove 1910 1070
}

f_wait_ready() {  # f_wait_ready PANE TIMEOUT
  local i; for i in $(seq 1 $(( ${2:-60} * 10 ))); do [ -e /tmp/ready.$1 ] && return 0; sleep 0.1; done
  echo "pane $1 not ready after ${2:-60}s" >&2; return 1
}

f_wait_text() {   # f_wait_text PANE REGEX TIMEOUT
  local i; for i in $(seq 1 $(( ${3:-60} * 10 ))); do
    tmux capture-pane -p -J -t "%$1" | grep -E -q -- "$2" && return 0; sleep 0.1; done
  echo "pane $1: no /$2/ after ${3:-60}s" >&2; return 1
}

f_pane() { tmux select-pane -t "%$1"; sleep 0.3; }

f_run() {         # f_run PANE "command" [TIMEOUT]: type it, Enter, wait for the prompt to come back
  f_pane "$1"; rm -f /tmp/ready.$1
  sl_type "$2" "pane $1: $2" 45
  sl_key Return
  f_wait_ready "$1" "${3:-60}"
  sl_nap 1.5
}

f_clear() {       # f_clear PANE: keep the pane's text so far (pane-N.before-clear-K.txt), then clear it on screen
  local k=$(ls "$O" | grep -c "pane-$1.before-clear" || true)
  tmux capture-pane -p -J -S - -t "%$1" > "$O/pane-$1.before-clear-$k.txt"
  f_run "$1" "clear"
}

f_rec() { sl_record "$O"; sl_mark "recording started"; sl_nap 2.5; }

f_end() {         # f_end: hold 2 s, stop, keep every pane's text, end frame
  sl_nap 2.0; sl_stop
  local p; for p in $(tmux list-panes -a -F '#{pane_id}' | tr -d '%'); do
    tmux capture-pane -p -J -S - -t "%$p" > "$O/pane-$p.txt"; done
  sl_shot "$O/end.png"
  tmux kill-server 2>/dev/null || true
  sl_display_stop
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$O/screen.mp4" > "$O/duration.txt"
}

f_gpu() { nvidia-smi --query-gpu=memory.used,memory.total --format=csv > "$O/nvidia-start.txt" 2>&1 || true; }
