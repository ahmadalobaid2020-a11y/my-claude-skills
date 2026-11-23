"""mix_audio.py -- clean the voice, lay a music bed, duck it, and two-pass
loudnorm the mix to a broadcast target. Video stream is copied untouched.

Usage:
    python mix_audio.py --voice cut.mp4 -o out.mp4
    python mix_audio.py --voice cut.mp4 --music bed.mp3 -o out.mp4 --duck
    python mix_audio.py --voice cut.mp4 --music bed.mp3 -o out.mp4 --clean --duck --target -14 --tp -1
    python mix_audio.py --voice cut.mp4 -o out.mp4 --clean   # voice-only clients (no bed)

Chain:
    voice [--clean: highpass 80Hz -> afftdn denoise -> +2.5dB @ ~4kHz presence]
      -> (music bed, looped/trimmed to voice length, 1s fade-in / 2s fade-out,
          sidechaincompress duck keyed by voice if --duck, else static --music-db gain)
      -> amix
      -> alimiter (level=false, safety ceiling before loudnorm pass 2)
      -> two-pass loudnorm (measure JSON, then apply linear=true with the
          measured values) to --target LUFS / --tp dBTP

Prints the measured input/output LUFS and true peak after the run.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def ffprobe_duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)])
    data = json.loads(r.stdout or "{}")
    return float(data.get("format", {}).get("duration", 0) or 0)


def has_audio_stream(path: Path) -> bool:
    r = run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "json", str(path)])
    data = json.loads(r.stdout or "{}")
    return bool(data.get("streams"))


def measure_loudnorm(input_args: list[str], filter_chain: str, target: float, tp: float, lra: float = 11.0) -> dict:
    """First pass: measure. Returns the loudnorm JSON stats dict."""
    f = f"{filter_chain}loudnorm=I={target}:TP={tp}:LRA={lra}:print_format=json"
    cmd = ["ffmpeg", "-hide_banner", "-y", *input_args, "-filter_complex", f, "-f", "null", "-"]
    r = run(cmd)
    text = r.stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", text, re.DOTALL)
    if not m:
        raise RuntimeError(f"loudnorm measure pass produced no stats:\n{text[-2000:]}")
    return json.loads(m.group(0))


def build_voice_filter(clean: bool) -> str:
    if not clean:
        return "[0:a]anull[voice]"
    # highpass 80Hz -> denoise -> presence boost ~4kHz -> label voice
    return (
        "[0:a]highpass=f=80,"
        "afftdn=nf=-25,"
        "equalizer=f=4000:t=q:w=1.2:g=2.5"
        "[voice]"
    )


def build_music_filter(duration: float, music_db: float, duck: bool, has_music: bool) -> tuple[str, str]:
    """Returns (filter_fragment, final_mix_label_of_music_or_none)."""
    if not has_music:
        return "", ""
    fade_out_start = max(0.0, duration - 2.0)
    gain_linear_note = f"volume={music_db}dB"
    frag = (
        f"[1:a]aloop=loop=-1:size=2147483647,atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        f"{gain_linear_note},"
        f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start:.3f}:d=2"
        f"[music_raw]"
    )
    if duck:
        frag += (
            ";[music_raw][voice]sidechaincompress=threshold=0.05:ratio=8:attack=20:release=400[music]"
        )
    else:
        frag += ";[music_raw]anull[music]"
    return frag, "music"


def main() -> int:
    ap = argparse.ArgumentParser(description="Clean voice, mix music bed, two-pass loudnorm.")
    ap.add_argument("--voice", required=True, type=Path, help="video/audio with the voice track")
    ap.add_argument("--music", type=Path, default=None, help="optional music bed file")
    ap.add_argument("-o", "--out", required=True, type=Path)
    ap.add_argument("--target", type=float, default=-14.0, help="LUFS target (house: -14 vertical, -16 long-form)")
    ap.add_argument("--tp", type=float, default=-1.0, help="true peak dBTP target")
    ap.add_argument("--music-db", type=float, default=-22.0, help="static music gain in dB when not ducking")
    ap.add_argument("--duck", action="store_true", help="sidechain-duck music by the voice instead of a flat gain")
    ap.add_argument("--clean", action="store_true", help="highpass 80Hz + denoise + presence boost on the voice")
    args = ap.parse_args()

    if not args.voice.exists():
        print(f"error: voice file not found: {args.voice}", file=sys.stderr)
        return 1
    if args.music and not args.music.exists():
        print(f"error: music file not found: {args.music}", file=sys.stderr)
        return 1
    if not has_audio_stream(args.voice):
        print(f"error: {args.voice} has no audio stream", file=sys.stderr)
        return 1

    duration = ffprobe_duration(args.voice)
    if duration <= 0:
        print(f"error: could not determine duration of {args.voice}", file=sys.stderr)
        return 1

    voice_frag = build_voice_filter(args.clean)
    music_frag, music_label = build_music_filter(duration, args.music_db, args.duck, args.music is not None)

    parts = [voice_frag]
    if music_frag:
        parts.append(music_frag)
        mix_inputs = f"[voice][{music_label}]"
        n_inputs = 2
    else:
        mix_inputs = "[voice]"
        n_inputs = 1

    if n_inputs > 1:
        parts.append(f"{mix_inputs}amix=inputs={n_inputs}:normalize=0:duration=first[premix]")
    else:
        parts.append("[voice]anull[premix]")

    parts.append("[premix]alimiter=limit=0.891:level=false[limited]")
    pre_chain = ";".join(parts) + ";"

    input_args = ["-i", str(args.voice)]
    if args.music:
        input_args += ["-stream_loop", "-1", "-i", str(args.music)]

    print("mix_audio.py: measuring loudness (pass 1)...")
    try:
        stats = measure_loudnorm(input_args, f"{pre_chain}[limited]", args.target, args.tp)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    measured_i = stats["input_i"]
    measured_tp = stats["input_tp"]
    measured_lra = stats["input_lra"]
    measured_thresh = stats["input_thresh"]
    offset = stats.get("target_offset", "0")

    loudnorm2 = (
        f"loudnorm=I={args.target}:TP={args.tp}:LRA=11:"
        f"measured_I={measured_i}:measured_TP={measured_tp}:measured_LRA={measured_lra}:"
        f"measured_thresh={measured_thresh}:offset={offset}:linear=true:print_format=json"
    )
    final_filter = f"{pre_chain}[limited]{loudnorm2}[aout]"

    args.out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y", *input_args,
        "-filter_complex", final_filter,
        "-map", "0:v?", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        str(args.out),
    ]
    print("mix_audio.py: rendering (pass 2)...")
    r = run(cmd)
    if r.returncode != 0:
        print(f"error: ffmpeg mix failed:\n{r.stderr[-3000:]}", file=sys.stderr)
        return 1

    tail = r.stderr
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", tail, re.DOTALL)
    final_stats = json.loads(m.group(0)) if m else {}

    print(f"mix_audio.py: done -> {args.out}")
    print(f"  measured input:  {measured_i} LUFS, TP {measured_tp} dBTP")
    print(f"  final output:    ~{final_stats.get('output_i', 'n/a')} LUFS, TP {final_stats.get('output_tp', 'n/a')} dBTP (target {args.target} LUFS / {args.tp} dBTP)")
    print(f"  clean={args.clean} duck={args.duck} music={'yes' if args.music else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
