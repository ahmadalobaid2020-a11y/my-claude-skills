#!/usr/bin/env python3
"""Transcribe a video/audio file to SRT/VTT with faster-whisper, optionally burn them in.

Usage:
  subtitles.py INPUT [--lang ar|en|auto] [--translate] [--model small]
               [--max-chars 42] [--burn] [--font "DejaVu Sans"] [--size 22] [--out DIR]
"""
import argparse, os, subprocess, sys, textwrap


def ts(t, sep=","):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02}{sep}{ms:03}"


def cues(segments, max_chars):
    """Split long segments into readable cues of at most two lines."""
    for seg in segments:
        text = seg.text.strip()
        if not text:
            continue
        words = list(seg.words or [])
        if len(text) <= max_chars * 2 or not words:
            yield seg.start, seg.end, "\n".join(textwrap.wrap(text, max_chars)[:2]) or text
            continue
        chunk, start = [], words[0].start
        for w in words:
            chunk.append(w)
            line = "".join(x.word for x in chunk).strip()
            if len(line) >= max_chars * 2 - 6 or line.endswith((".", "?", "!", "؟", "،")):
                yield start, w.end, "\n".join(textwrap.wrap(line, max_chars)[:2])
                chunk, start = [], w.end
        if chunk:
            line = "".join(x.word for x in chunk).strip()
            yield start, chunk[-1].end, "\n".join(textwrap.wrap(line, max_chars)[:2])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--lang", default="auto", help="spoken language code, or auto")
    p.add_argument("--translate", action="store_true", help="output English subtitles")
    p.add_argument("--model", default="small", help="tiny|base|small|medium|large-v3")
    p.add_argument("--max-chars", type=int, default=42)
    p.add_argument("--burn", action="store_true", help="also render subtitles onto the video")
    p.add_argument("--font", default="DejaVu Sans")
    p.add_argument("--size", type=int, default=22)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    from faster_whisper import WhisperModel

    src = os.path.abspath(a.input)
    out = os.path.abspath(a.out or os.path.dirname(src))
    os.makedirs(out, exist_ok=True)
    base = os.path.splitext(os.path.basename(src))[0]
    # Decode with ffmpeg (16 kHz mono float32) instead of PyAV, which varies by version.
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", src, "-vn",
                          "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         check=True, capture_output=True).stdout
    audio = np.frombuffer(pcm, dtype=np.float32)
    model = WhisperModel(a.model, device="auto", compute_type="int8")
    segs, info = model.transcribe(
        audio,
        language=None if a.lang == "auto" else a.lang,
        task="translate" if a.translate else "transcribe",
        vad_filter=True,
        word_timestamps=True,
    )
    lang = "en" if a.translate else info.language
    items = list(cues(segs, a.max_chars))
    if not items:
        sys.exit("No speech found.")

    srt = os.path.join(out, f"{base}.{lang}.srt")
    vtt = os.path.join(out, f"{base}.{lang}.vtt")
    with open(srt, "w", encoding="utf-8") as f:
        for i, (s, e, t) in enumerate(items, 1):
            f.write(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n")
    with open(vtt, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for s, e, t in items:
            f.write(f"{ts(s, '.')} --> {ts(e, '.')}\n{t}\n\n")
    print(f"language: {info.language} (p={info.language_probability:.2f}), cues: {len(items)}")
    print("srt:", srt)
    print("vtt:", vtt)

    if a.burn:
        dst = os.path.join(out, f"{base}.{lang}.subtitled.mp4")
        esc = srt.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        style = (f"FontName={a.font},FontSize={a.size},PrimaryColour=&H00FFFFFF,"
                 "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,MarginV=28")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src,
                        "-vf", f"subtitles='{esc}':force_style='{style}'",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                        "-c:a", "copy", dst], check=True)
        print("video:", dst)


if __name__ == "__main__":
    main()
