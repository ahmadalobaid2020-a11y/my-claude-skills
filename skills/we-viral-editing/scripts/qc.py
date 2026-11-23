"""We Viral export QC. Usage: python qc.py <video> [<video> ...]

Checks each file against the house spec (see references/pipeline.md) and prints PASS/WARN/FAIL lines.
Needs ffmpeg + ffprobe on PATH.
"""
import json, re, subprocess, sys

OK_SIZES = {(1080, 1920), (2160, 3840), (1920, 1080), (3840, 2160), (1080, 1350), (1080, 1080)}
OK_FPS = {24, 25, 30, 50, 60}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def moov_first(path):
    """True if the moov atom precedes mdat (+faststart), None if not an MP4/MOV we can walk."""
    import struct
    try:
        with open(path, "rb") as f:
            while True:
                hdr = f.read(8)
                if len(hdr) < 8:
                    return None
                size, kind = struct.unpack(">I4s", hdr)
                if kind == b"moov":
                    return True
                if kind == b"mdat":
                    return False
                if size == 1:
                    size = struct.unpack(">Q", f.read(8))[0] - 8
                elif size == 0:
                    return None
                f.seek(size - 8, 1)
    except OSError:
        return None


def check(path):
    out = []
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", path]).stdout or "{}")
    v = next((s for s in pr.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in pr.get("streams", []) if s["codec_type"] == "audio"), None)
    if not v:
        return [("FAIL", "no video stream")]
    w, h = v["width"], v["height"]
    rot = 0
    for sd in v.get("side_data_list", []):
        if "rotation" in sd:
            rot = abs(int(sd["rotation"]))
    if rot in (90, 270):
        out.append(("FAIL", f"rotation metadata {rot} deg - re-export with rotation baked in"))
        w, h = h, w
    if (w, h) not in OK_SIZES:
        out.append(("FAIL", f"frame size {w}x{h} - house spec is 1080x1920 (or 2160x3840 / 1920x1080 / 1080x1350)"))
    else:
        out.append(("PASS", f"frame size {w}x{h}"))
    num, den = v.get("r_frame_rate", "0/1").split("/")
    fps = float(num) / float(den or 1)
    (out.append(("PASS", f"fps {fps:.3f}")) if round(fps) in OK_FPS and abs(fps - round(fps)) < 0.05 or abs(fps - 29.97) < 0.01 or abs(fps - 59.94) < 0.01
     else out.append(("WARN", f"unusual fps {fps:.3f}")))
    if v.get("codec_name") != "h264":
        out.append(("WARN" if v.get("codec_name") in ("prores", "qtrle") else "FAIL", f"video codec {v.get('codec_name')} (deliverables are H.264; .mov alpha assets excepted)"))
    if v.get("pix_fmt") not in ("yuv420p", None) and v.get("codec_name") == "h264":
        out.append(("WARN", f"pix_fmt {v.get('pix_fmt')} - use yuv420p for social"))
    dur = float(pr.get("format", {}).get("duration", 0) or 0)
    br = int(pr.get("format", {}).get("bit_rate", 0) or 0) / 1e6
    out.append(("PASS" if 5 <= dur <= 180 else "WARN", f"duration {dur:.1f}s"))
    if w * h >= 1080 * 1920 and br < 8:
        out.append(("WARN", f"bitrate {br:.1f} Mbps is low for {w}x{h} (house ~16-20 Mbps at 1080p)"))
    if not a:
        out.append(("WARN", "no audio stream (OK only for alpha assets)"))
        return out
    fs = moov_first(path)
    if fs is False:
        out.append(("WARN", "moov atom at end - re-mux with -movflags +faststart (IG/QuickTime)"))
    elif fs:
        out.append(("PASS", "faststart"))
    vd, ad = float(v.get("duration", 0) or 0), float(a.get("duration", 0) or 0)
    if vd and ad and fps:
        drift = abs(vd - ad)
        out.append(("PASS" if drift <= 1.0 / fps else ("WARN" if drift <= 0.1 else "FAIL"),
                    f"A/V stream duration diff {drift*1000:.0f} ms (max 1 frame)"))
    if a.get("sample_rate") != "48000":
        out.append(("WARN", f"audio sample rate {a.get('sample_rate')} (house 48000)"))
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[-1500:]
    m = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    lufs = float(m.group(1)) if m else None
    m = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", tail)
    tp = float(m.group(1)) if m and m.group(1) != "-inf" else None
    if lufs is None or lufs < -60:
        out.append(("WARN", "audio is silent - fine only for a deliberate 'No Music' export"))
    elif -15.5 <= lufs <= -12.5:
        out.append(("PASS", f"loudness {lufs} LUFS"))
    elif lufs < -18 or lufs > -10:
        out.append(("FAIL", f"loudness {lufs} LUFS - target -14 LUFS"))
    else:
        out.append(("WARN", f"loudness {lufs} LUFS - target -14 LUFS"))
    if tp is not None:
        out.append(("PASS" if tp <= -1.0 else ("WARN" if tp <= 0 else "FAIL"), f"true peak {tp} dBTP (max -1)"))
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    worst = 0
    for p in sys.argv[1:]:
        print(f"== {p}")
        for level, msg in check(p):
            worst = max(worst, {"PASS": 0, "WARN": 1, "FAIL": 2}[level])
            print(f"  [{level}] {msg}")
    sys.exit(1 if worst == 2 else 0)
