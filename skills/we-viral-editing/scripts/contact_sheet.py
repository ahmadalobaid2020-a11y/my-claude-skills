"""Make a 12-frame study sheet of a video (hook frames, body, ending) with specs, cut rate and loudness.

Usage: python contact_sheet.py <video> [out.jpg]
Needs ffmpeg/ffprobe on PATH and Pillow. Open the jpg to review hook, captions, CTA and end card.
"""
import json, os, re, subprocess, sys, tempfile
from PIL import Image, ImageDraw


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def main(p, out):
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", p]).stdout)
    d = float(pr["format"]["duration"])
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    w, h = v["width"], v["height"]
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-an", "-vf", "scale=160:-2,select='gt(scene,0.28)',showinfo", "-f", "null", "-"])
    cuts = len(re.findall(r"pts_time:", r.stderr))
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-vn", "-af", "ebur128", "-f", "null", "-"])
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", r.stderr[-1500:])
    lufs = m.group(1) if m else "n/a"
    times = [0.1, 1.0, 2.5] + [3.5 + (d - 5) * i / 6 if d > 8 else d * (i + 1) / 9 for i in range(7)] + [max(d - 1.2, 0), max(d - 0.15, 0)]
    times = [min(max(t, 0), max(d - 0.05, 0)) for t in times]
    vert = h >= w
    tw, th = (216, 384) if vert else (384, 216)
    tmp = tempfile.mkdtemp()
    sheet = Image.new("RGB", (6 * tw, 2 * (th + 16) + 22), (20, 20, 20))
    dr = ImageDraw.Draw(sheet)
    dr.text((4, 4), f"{os.path.basename(p)} | {d:.1f}s {w}x{h} | {cuts/d*60:.1f} cuts/min | {lufs} LUFS", fill=(255, 255, 0))
    for i, t in enumerate(times):
        fp = os.path.join(tmp, f"{i}.jpg")
        run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", p, "-frames:v", "1", "-vf",
             f"scale={tw}:{th}:force_original_aspect_ratio=decrease,pad={tw}:{th}:(ow-iw)/2:(oh-ih)/2", fp])
        if os.path.exists(fp):
            x, y = (i % 6) * tw, 22 + (i // 6) * (th + 16)
            sheet.paste(Image.open(fp), (x, y + 16))
            dr.text((x + 3, y + 2), f"{t:.1f}s", fill=(0, 255, 255))
    sheet.save(out, quality=85)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    src = sys.argv[1]
    main(src, sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(src)[0] + "_sheet.jpg")
