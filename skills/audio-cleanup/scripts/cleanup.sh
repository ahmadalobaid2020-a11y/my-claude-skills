#!/usr/bin/env bash
# Clean a voice recording: remove rumble and hiss, tame harsh "s", even out the level,
# and normalise loudness (two-pass loudnorm). Works on audio files and on videos
# (the video stream is copied untouched).
#
# Usage: cleanup.sh INPUT [OUTPUT] [--target -14] [--denoise 12] [--no-denoise]
#   --target   integrated loudness in LUFS: -14 YouTube/social (default), -16 podcasts, -23 broadcast
#   --denoise  noise reduction strength in dB (afftdn nr), default 12; raise for noisy rooms
set -euo pipefail

in="${1:?usage: cleanup.sh INPUT [OUTPUT] [--target -14] [--denoise 12] [--no-denoise]}"; shift
out=""
if [ $# -gt 0 ] && [ "${1#--}" = "$1" ]; then out="$1"; shift; fi
target=-14; nr=12; denoise=1
while [ $# -gt 0 ]; do
  case "$1" in
    --target) target="$2"; shift 2 ;;
    --denoise) nr="$2"; shift 2 ;;
    --no-denoise) denoise=0; shift ;;
    *) echo "unknown option $1" >&2; exit 1 ;;
  esac
done
if [ -z "$out" ]; then out="${in%.*}.clean.${in##*.}"; fi

chain="highpass=f=80,lowpass=f=16000"
[ "$denoise" = 1 ] && chain="$chain,afftdn=nr=${nr}:nf=-40:tn=1"
chain="$chain,deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2"

lufs() { ffmpeg -hide_banner -nostdin -i "$1" -vn -af "${2:-anull},ebur128=framelog=quiet" -f null - 2>&1 \
  | awk '/I:/{v=$2} END{print v}'; }

# pass 1: measure the original and the cleaned signal (EBU R128 integrated loudness)
mi=$(lufs "$in")
mc=$(lufs "$in" "$chain")
gain=$(python3 -c "print(round(${target} - (${mc}), 2))")

# pass 2: exact gain to the target, then a limiter so peaks stay below -1.5 dBFS
has_video=$(ffprobe -v error -select_streams v -show_entries stream=codec_type -of csv=p=0 "$in" | head -1)
case "${out##*.}" in
  wav) acodec=(-c:a pcm_s16le) ;;
  mp3) acodec=(-c:a libmp3lame -q:a 2) ;;
  *)   acodec=(-c:a aac -b:a 192k) ;;
esac
render() {
  local ln="volume=${1}dB,alimiter=limit=0.84:attack=3:release=50:level=false"
  if [ -n "$has_video" ]; then
    ffmpeg -y -hide_banner -loglevel error -nostdin -i "$in" -af "$chain,$ln" -ar 48000 -c:v copy -c:a aac -b:a 192k "$out"
  else
    ffmpeg -y -hide_banner -loglevel error -nostdin -i "$in" -af "$chain,$ln" -ar 48000 "${acodec[@]}" "$out"
  fi
}

# the limiter trims peaks and costs some loudness, so measure and correct (max 3 rounds)
for _ in 1 2 3; do
  render "$gain"
  after=$(lufs "$out")
  miss=$(python3 -c "print(round(${target} - (${after}), 2))")
  python3 -c "import sys; sys.exit(0 if abs(${miss}) <= 0.5 else 1)" && break
  gain=$(python3 -c "print(round(${gain} + ${miss}, 2))")
done
echo "before: ${mi} LUFS  after: ${after} LUFS  (target ${target}, gain ${gain} dB)"
echo "output: $out"
