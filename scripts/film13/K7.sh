# Live docs page (network). Full window first, then scroll to the VRAM note.
. /lab/scripts/film13/lib.sh
sl_display 1920 1080
mkdir -p /tmp/ffp
# fresh profile: skip the first-run Welcome / Terms of Use modal (attempt 1 was covered by it)
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
sl_app /tmp/ff.log firefox-esr --no-remote --profile /tmp/ffp --new-window https://docs.ollama.com/context-length
sl_wait_window "Firefox|Mozilla|Ollama|Context" 60 > /dev/null
sl_maximise "Firefox|Mozilla|Ollama|Context"
sleep ${K7_LOAD_WAIT:-12}
xdotool mousemove 1900 1000
sl_shot "$O/probe-loaded.png"
sl_record "$O"; sl_mark "recording started"; sl_nap 3
for i in $(seq 1 ${K7_SCROLLS:-0}); do xdotool click 5; sleep 0.25; done
sl_mark "scrolled ${K7_SCROLLS:-0}"
sl_nap 5
sl_stop
sl_shot "$O/end.png"
sl_display_stop
ffprobe -v error -show_entries format=duration -of csv=p=0 "$O/screen.mp4" > "$O/duration.txt"
