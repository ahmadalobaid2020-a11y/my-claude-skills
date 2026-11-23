"""We Viral silence-based EDL builder: turns ffmpeg silencedetect into kept speech ranges.

Runs ffmpeg's silencedetect filter over the audio, inverts the found silences into the
speech ranges to KEEP, pads each range, and writes an EDL JSON:
  {"sources": {"a": "path.mp4"}, "ranges": [{"src": "a", "start": 1.20, "end": 4.85, "note": "..."}]}

Per cutting.md: default gate is -40 dB / min gap 0.35s / pad 0.12s (0.45s on the last
range's tail, to catch the final word's release). Thresholds above -32 dB eat soft word
releases and are refused unless --force.

Usage:
  python silence_edl.py input.mp4 -o edl.json
  python silence_edl.py input.mp4 -o edl.json --db -35 --min-gap 0.3
  python silence_edl.py input.mp4 -o edl.json --db -28 --force   # dangerous, needs --force
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

MAX_SAFE_DB = -32.0


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def probe_duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float((r.stdout or "0").strip() or 0.0)


def detect_silences(path: Path, db: float, min_gap: float):
    """Returns list of (silence_start, silence_end) in seconds."""
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
           "-af", f"silencedetect=noise={db}dB:d={min_gap}", "-f", "null", "-"]
    r = run(cmd)
    log = r.stderr
    starts = [float(m) for m in re.findall(r"silence_start:\s*(-?[\d.]+)", log)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", log)]
    # ffmpeg may report a silence_start with no matching silence_end if it runs to EOF.
    silences = []
    for i, s in enumerate(starts):
        if i < len(ends):
            silences.append((max(0.0, s), ends[i]))
        else:
            silences.append((max(0.0, s), None))  # open to end of file
    return silences


def invert_to_speech(silences, duration, pad, pad_last):
    """Speech = complement of silences, each end padded by `pad` (or pad_last for the
    final kept range), clamped to [0, duration]."""
    speech = []
    cursor = 0.0
    for i, (s_start, s_end) in enumerate(silences):
        if s_start > cursor:
            speech.append([cursor, s_start])
        cursor = s_end if s_end is not None else duration
        if s_end is None:
            break
    if cursor < duration:
        speech.append([cursor, duration])

    # pad range ends into the following silence (or clamp at duration), pad range starts
    # back slightly too so onsets aren't clipped.
    for i, rng in enumerate(speech):
        is_last = i == len(speech) - 1
        end_pad = pad_last if is_last else pad
        rng[0] = max(0.0, rng[0] - pad)
        rng[1] = min(duration, rng[1] + end_pad)

    # merge any ranges that now overlap because of padding
    merged = []
    for rng in speech:
        if merged and rng[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], rng[1])
        else:
            merged.append(rng)
    return merged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", help="input media file")
    ap.add_argument("-o", "--out", required=True, help="output edl.json path")
    ap.add_argument("--db", type=float, default=-40.0, help="silence threshold in dB (default: -40)")
    ap.add_argument("--min-gap", type=float, default=0.35, help="minimum silence duration to count (default: 0.35s)")
    ap.add_argument("--pad", type=float, default=0.12, help="pad added at each kept-range end (default: 0.12s)")
    ap.add_argument("--pad-last", type=float, default=0.45, help="pad added at the FINAL kept range's end (default: 0.45s)")
    ap.add_argument("--force", action="store_true", help="allow thresholds above -32 dB (eats soft word tails)")
    ap.add_argument("--source-key", default="a", help="key name for this source in the EDL 'sources' dict")
    args = ap.parse_args()

    src = Path(args.media)
    if not src.exists():
        print(f"error: input file not found: {src}", file=sys.stderr)
        sys.exit(1)

    if args.db > MAX_SAFE_DB and not args.force:
        print(f"error: --db {args.db} is above the safe ceiling of {MAX_SAFE_DB} dB "
              f"(eats soft word tails). Re-run with --force if you really mean it.", file=sys.stderr)
        sys.exit(1)

    duration = probe_duration(src)
    if duration <= 0:
        print("error: could not read media duration via ffprobe", file=sys.stderr)
        sys.exit(1)

    silences = detect_silences(src, args.db, args.min_gap)
    if not silences:
        suggestion = args.db + 5.0
        print(f"warning: no silences found at {args.db} dB / min-gap {args.min_gap}s. "
              f"Try a looser threshold, e.g. --db {suggestion:.0f}", file=sys.stderr)

    speech = invert_to_speech(silences, duration, args.pad, args.pad_last)
    # drop degenerate/negative ranges that can appear from aggressive padding
    speech = [r for r in speech if r[1] - r[0] > 0.01]

    ranges = [
        {"src": args.source_key, "start": round(s, 3), "end": round(e, 3),
         "note": f"speech range {i + 1}/{len(speech)}"}
        for i, (s, e) in enumerate(speech)
    ]
    edl = {"sources": {args.source_key: str(src)}, "ranges": ranges}

    out_path = Path(args.out)
    out_path.write_text(json.dumps(edl, ensure_ascii=False, indent=2), encoding="utf-8")

    total_kept = sum(r["end"] - r["start"] for r in ranges)
    print(f"silence_edl.py: {len(silences)} silences found · {len(ranges)} speech ranges kept "
          f"({total_kept:.2f}s of {duration:.2f}s, {100*total_kept/duration:.0f}%) -> {out_path}")


if __name__ == "__main__":
    main()
