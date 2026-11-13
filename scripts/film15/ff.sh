# Firefox ESR prelude, as scripts/film13/K7.sh (fresh profile, no first-run modal). ff_open URL
ff_open() {
  sl_display 1920 1080
  mkdir -p /tmp/ffp
  cat > /tmp/ffp/user.js <<'JS'
user_pref("browser.preonboarding.enabled", false);
user_pref("termsofuse.bypassNotification", true);
user_pref("termsofuse.acceptedVersion", 999);
user_pref("termsofuse.acceptedDate", "1735689600000");
user_pref("datareporting.policy.dataSubmissionPolicyBypassNotification", true);
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("trailhead.firstrun.didSeeAboutWelcome", true);
user_pref("browser.shell.checkDefaultBrowser", false);
JS
  sl_app /tmp/ff.log firefox-esr --no-remote --profile /tmp/ffp --new-window "$1"
  sl_wait_window "Firefox|Mozilla" 60 > /dev/null
  sl_maximise "Firefox|Mozilla"
  sleep ${LOAD_WAIT:-12}
  xdotool mousemove 1900 1000
  sl_shot "$O/probe-loaded.png"
}
ff_end() { sl_stop; sl_shot "$O/end.png"; sl_display_stop
  ffprobe -v error -show_entries format=duration -of csv=p=0 "$O/screen.mp4" > "$O/duration.txt"; }

# Part 15 additions. f_term: the film13 xterm + tmux (f_start without a new display), opened over the browser in the same
# recording; full window 2.5 s before the first command. r [TIMEOUT]: type the command read from stdin (a quoted
# heredoc, so jq's quotes and \( stay literal) in pane 0, Enter, wait for the prompt.
f_term() {
  sl_app /tmp/xterm.log xterm -T film13 -fa "DejaVu Sans Mono" -fs ${FS:-30} -bg white -fg black \
    -e tmux -f /tmp/tmux.conf new -s f
  sl_wait_window film13 20 > /dev/null
  sl_maximise film13
  f_wait_ready 0 20
  xdotool mousemove 1910 1070
  sl_mark "terminal up"; sl_nap 2.5
}
r() { local c; c=$(cat); f_run 0 "$c" "${1:-60}"; }
