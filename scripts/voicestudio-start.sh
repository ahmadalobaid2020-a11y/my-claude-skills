#!/usr/bin/env bash
# Start the headless VoiceStudio backend on 127.0.0.1:3900 (CPU) and wait until /health answers.
# The checkout and its Python environment come from install.sh (~/VoiceStudio).
set -e
dir="${VOICESTUDIO_DIR:-$HOME/VoiceStudio}"
log="${VOICESTUDIO_LOG:-$HOME/.voicestudio-backend.log}"
health() { curl -s --noproxy 127.0.0.1 -o /dev/null -w '%{http_code}' http://127.0.0.1:3900/health; }

if [ "$(health)" = 200 ]; then echo "VoiceStudio backend already running on http://127.0.0.1:3900"; exit 0; fi
[ -x "$dir/.venv/bin/python" ] || { echo "No VoiceStudio environment in $dir: run install.sh first" >&2; exit 1; }

cd "$dir"
OMNIVOICE_DEVICE=cpu HF_HUB_DISABLE_XET=1 OMNIVOICE_DATA_DIR="$HOME/.voicestudio-data" \
  nohup .venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 3900 >"$log" 2>&1 &
for _ in $(seq 1 60); do
  [ "$(health)" = 200 ] && { echo "VoiceStudio backend running on http://127.0.0.1:3900 (log: $log)"; exit 0; }
  sleep 3
done
echo "VoiceStudio backend did not answer /health within 3 minutes; see $log" >&2
exit 1
