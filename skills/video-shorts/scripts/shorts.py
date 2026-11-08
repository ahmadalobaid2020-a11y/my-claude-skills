#!/usr/bin/env python3
"""Cut vertical 9:16 shorts (1080x1920) from a long video, optionally with burned subtitles.

Usage:
  shorts.py INPUT --clip 00:01:10-00:01:45 [--clip 00:05:00-00:05:40 ...]
            [--mode blur|crop] [--x 0.5] [--subs] [--lang auto] [--model small]
            [--title "text on top"] [--out DIR]

--mode blur  (default) fits the whole frame in the middle over a blurred, zoomed copy.
--mode crop  fills the screen by cropping; --x picks the horizontal centre (0=left, 1=right).
--subs       transcribes each clip with the subtitles skill and burns the captions in.
"""
import argparse, os, subprocess, sys

SUBS = os.path.expanduser("~/.claude/skills/subtitles/scripts/subtitles.py")
FONT = "DejaVu Sans"


def secs(t):
    parts = [float(p) for p in t.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def esc(path):
    return path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("input")
    p.add_argument("--clip", action="append", required=True, help="START-END, e.g. 01:10-01:45")
    p.add_argument("--mode", choices=["blur", "crop"], default="blur")
    p.add_argument("--x", type=float, default=0.5)
    p.add_argument("--subs", action="store_true")
    p.add_argument("--lang", default="auto")
    p.add_argument("--model", default="small")
    p.add_argument("--title", default=None)
    p.add_argument("--out", default=None)
    a = p.parse_args()

    src = os.path.abspath(a.input)
    out = os.path.abspath(a.out or os.path.join(os.path.dirname(src), "shorts"))
    os.makedirs(out, exist_ok=True)
    base = os.path.splitext(os.path.basename(src))[0]

    for n, spec in enumerate(a.clip, 1):
        start, end = (secs(x) for x in spec.split("-"))
        if end <= start:
            sys.exit(f"bad clip {spec}")
        dur = end - start
        raw = os.path.join(out, f"{base}.short{n}.raw.mp4")
        # accurate cut first (re-encode), so subtitles and framing use clip-relative time
        run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-i", src, "-t", str(dur),
             "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", raw])

        if a.mode == "blur":
            graph = ("[0:v]split[a][b];"
                     "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:2,eq=brightness=-0.08[bg];"
                     "[b]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
                     "[bg][fg]overlay=(W-w)/2:(H-h)/2")
        else:
            graph = (f"[0:v]scale=-2:1920,crop=1080:1920:"
                     f"'max(0,min(iw-1080,iw*{a.x}-540))':0")

        if a.title:
            tfile = os.path.join(out, f"{base}.short{n}.title.txt")
            with open(tfile, "w", encoding="utf-8") as f:
                f.write(a.title)
            graph += (f",drawtext=textfile='{esc(tfile)}':font='{FONT}':fontcolor=white:fontsize=64:"
                      "box=1:boxcolor=black@0.55:boxborderw=24:x=(w-text_w)/2:y=170")

        if a.subs:
            cmd = [sys.executable, SUBS, raw, "--model", a.model, "--lang", a.lang,
                   "--max-chars", "22", "--out", out]
            res = subprocess.run(cmd, check=True, capture_output=True, text=True)
            srt = next(l.split(":", 1)[1].strip() for l in res.stdout.splitlines() if l.startswith("srt:"))
            style = (f"FontName={FONT},FontSize=13,Bold=1,PrimaryColour=&H00FFFFFF,"
                     "OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginV=70")
            graph += f",subtitles='{esc(srt)}':original_size=1080x1920:force_style='{style}'"

        final = os.path.join(out, f"{base}.short{n}.mp4")
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-filter_complex", graph,
             "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
             "-c:a", "copy", "-movflags", "+faststart", final])
        os.remove(raw)
        print(f"short {n}: {final} ({dur:.1f}s)")


if __name__ == "__main__":
    main()
