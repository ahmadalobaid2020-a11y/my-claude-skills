"""We Viral transcriber: word-level timestamps from a media file.

Extracts 16 kHz mono audio, then transcribes with ElevenLabs Scribe (default when
ELEVENLABS_API_KEY is set) or a local faster-whisper model, and writes a Words JSON:
  {"engine": "scribe|whisper", "language": "ar", "duration": 12.3,
   "words": [{"text": "...", "start": 0.12, "end": 0.48}, ...]}

Always overwrites the output file (no stale cache) — per cutting.md, a stale word-times
cache is the #1 source of "word ends past file duration" bugs after a re-cut.

Usage:
  python transcribe.py input.mp4 -o words.json
  python transcribe.py input.mp4 -o words.json --engine whisper --lang ar --model small
  python transcribe.py input.mp4 -o words.json --clip 12.0 18.5   # slice-transcribe a window
  python transcribe.py input.mov -o words.json --engine scribe    # force ElevenLabs Scribe

--clip START END slice-transcribes only that window of the source (for hunting hidden
retakes cheaply) and offsets all returned word times back to source time, so the output
words.json can be spliced directly against a full-file transcript.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

SCRIBE_MODEL = "scribe_v1"
SCRIBE_URL = "https://api.elevenlabs.io/v1/speech-to-text"


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(str(c) for c in cmd)}\n{r.stderr[-2000:]}")
    return r


def extract_wav(src: Path, clip, dst: Path):
    """Extract 16 kHz mono PCM wav, optionally sliced to [clip_start, clip_end] of source time."""
    cmd = ["ffmpeg", "-y", "-v", "error"]
    if clip:
        cmd += ["-ss", str(clip[0]), "-to", str(clip[1])]
    cmd += ["-i", str(src), "-ac", "1", "-ar", "16000", "-vn", "-c:a", "pcm_s16le", str(dst)]
    run(cmd)


def transcribe_scribe(wav_path: Path, lang: str | None):
    import requests  # lazy: only needed for this engine

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise RuntimeError("ELEVENLABS_API_KEY is not set")
    with open(wav_path, "rb") as f:
        files = {"file": (wav_path.name, f, "audio/wav")}
        data = {"model_id": SCRIBE_MODEL, "timestamps_granularity": "word"}
        if lang:
            data["language_code"] = lang
        resp = requests.post(
            SCRIBE_URL,
            headers={"xi-api-key": api_key},
            files=files,
            data=data,
            timeout=300,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Scribe API error {resp.status_code}: {resp.text[:500]}")
    payload = resp.json()
    words = []
    for w in payload.get("words", []):
        # Scribe emits word + spacing/punctuation pseudo-tokens; keep only real words.
        wtype = w.get("type", "word")
        if wtype not in ("word",):
            continue
        text = (w.get("text") or "").strip()
        if not text:
            continue
        words.append({"text": text, "start": float(w["start"]), "end": float(w["end"])})
    language = payload.get("language_code") or lang or "unknown"
    return words, language


def transcribe_whisper(wav_path: Path, lang: str | None, model_size: str):
    from faster_whisper import WhisperModel  # lazy: heavy import

    model = WhisperModel(model_size, device="auto", compute_type="auto")
    segments, info = model.transcribe(
        str(wav_path),
        language=lang,
        word_timestamps=True,
        vad_filter=True,
    )
    words = []
    for seg in segments:
        for w in seg.words or []:
            text = (w.word or "").strip()
            if not text:
                continue
            words.append({"text": text, "start": float(w.start), "end": float(w.end)})
    language = info.language or lang or "unknown"
    return words, language


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media", help="input media file (video or audio)")
    ap.add_argument("-o", "--out", required=True, help="output words.json path")
    ap.add_argument("--engine", choices=["auto", "scribe", "whisper"], default="auto",
                     help="auto = Scribe if ELEVENLABS_API_KEY set, else faster-whisper")
    ap.add_argument("--lang", default=None, help="language code hint, e.g. ar, en, tr")
    ap.add_argument("--model", default="small", help="faster-whisper model size (default: small)")
    ap.add_argument("--clip", nargs=2, type=float, metavar=("START", "END"),
                     help="slice-transcribe only this window of source time (seconds)")
    args = ap.parse_args()

    src = Path(args.media)
    if not src.exists():
        print(f"error: input file not found: {src}", file=sys.stderr)
        sys.exit(1)

    out_path = Path(args.out)
    if out_path.exists():
        out_path.unlink()  # never trust a stale cache

    engine = args.engine
    if engine == "auto":
        engine = "scribe" if os.environ.get("ELEVENLABS_API_KEY") else "whisper"

    clip = tuple(args.clip) if args.clip else None
    if clip and clip[1] <= clip[0]:
        print("error: --clip END must be greater than START", file=sys.stderr)
        sys.exit(1)

    tmp_dir = Path(tempfile.mkdtemp(prefix="we_viral_transcribe_"))
    wav_path = tmp_dir / "audio16k.wav"
    try:
        extract_wav(src, clip, wav_path)

        if engine == "scribe":
            try:
                words, language = transcribe_scribe(wav_path, args.lang)
            except Exception as e:
                print(f"warning: Scribe failed ({e}); falling back to faster-whisper", file=sys.stderr)
                words, language = transcribe_whisper(wav_path, args.lang, args.model)
                engine = "whisper"
        else:
            words, language = transcribe_whisper(wav_path, args.lang, args.model)

        offset = clip[0] if clip else 0.0
        for w in words:
            w["start"] = round(w["start"] + offset, 3)
            w["end"] = round(w["end"] + offset, 3)

        if clip:
            duration = clip[1] - clip[0] + offset
        else:
            pr = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=noprint_wrappers=1:nokey=1", str(src)])
            duration = float(pr.stdout.strip() or 0.0)

        payload = {
            "engine": engine,
            "language": language,
            "duration": round(duration, 3),
            "words": words,
        }
        out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        span = f" (window {clip[0]:.2f}-{clip[1]:.2f}s)" if clip else ""
        print(f"transcribe.py: {engine} · {language} · {len(words)} words · "
              f"{duration:.2f}s{span} -> {out_path}")
    finally:
        for p in tmp_dir.glob("*"):
            try:
                p.unlink()
            except OSError:
                pass
        try:
            tmp_dir.rmdir()
        except OSError:
            pass


if __name__ == "__main__":
    main()
