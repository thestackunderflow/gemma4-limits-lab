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
