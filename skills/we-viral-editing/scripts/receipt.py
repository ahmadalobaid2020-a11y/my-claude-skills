"""receipt.py -- write a delivery receipt for one or more final videos.

For each <name>.mp4 writes <name>.receipt.json next to it containing:
sha256, file size, duration, a streams summary (video/audio codec, size,
fps, sample rate, channels), the qc.py PASS/WARN/FAIL result, an ISO-8601
timestamp, and a cover JPG (first frame) written as <name>.cover.jpg.

Usage:
    python receipt.py final.mp4
    python receipt.py final1.mp4 final2.mp4 final3.mp4
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe_summary(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    data = json.loads(r.stdout or "{}")
    fmt = data.get("format", {})
    streams = []
    for s in data.get("streams", []):
        entry = {"codec_type": s.get("codec_type"), "codec_name": s.get("codec_name")}
        if s.get("codec_type") == "video":
            num, den = s.get("r_frame_rate", "0/1").split("/")
            fps = round(float(num) / float(den or 1), 3) if float(den or 1) else 0
            entry.update({
                "width": s.get("width"), "height": s.get("height"),
                "fps": fps, "pix_fmt": s.get("pix_fmt"),
            })
        elif s.get("codec_type") == "audio":
            entry.update({
                "sample_rate": s.get("sample_rate"),
                "channels": s.get("channels"),
                "channel_layout": s.get("channel_layout"),
            })
        streams.append(entry)
    return {
        "duration": float(fmt.get("duration", 0) or 0),
        "bit_rate": int(fmt.get("bit_rate", 0) or 0),
        "format_name": fmt.get("format_name"),
        "streams": streams,
    }


def write_cover(path: Path, cover_path: Path) -> bool:
    cmd = ["ffmpeg", "-y", "-i", str(path), "-frames:v", "1", "-q:v", "2", str(cover_path)]
    r = run(cmd)
    return r.returncode == 0 and cover_path.exists()


def run_qc(path: Path) -> dict:
    qc_script = SCRIPT_DIR / "qc.py"
    if not qc_script.exists():
        return {"error": f"qc.py not found at {qc_script}"}
    r = run([sys.executable, str(qc_script), str(path)])
    lines = [ln.strip() for ln in r.stdout.splitlines() if ln.strip().startswith("[")]
    worst = "PASS"
    for ln in lines:
        if ln.startswith("[FAIL"):
            worst = "FAIL"
            break
        if ln.startswith("[WARN") and worst != "FAIL":
            worst = "WARN"
    return {"overall": worst, "checks": lines, "exit_code": r.returncode}


def build_receipt(path: Path) -> dict:
    stat = path.stat()
    return {
        "file": str(path.resolve()),
        "sha256": sha256_of(path),
        "size_bytes": stat.st_size,
        "media": ffprobe_summary(path),
        "qc": run_qc(path),
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    worst_exit = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"error: not found: {path}", file=sys.stderr)
            worst_exit = 1
            continue

        print(f"receipt.py: {path.name}")
        receipt = build_receipt(path)

        cover_path = path.with_suffix("").with_name(path.stem + ".cover.jpg")
        cover_ok = write_cover(path, cover_path)
        receipt["cover"] = str(cover_path.resolve()) if cover_ok else None

        receipt_path = path.with_suffix("").with_name(path.stem + ".receipt.json")
        receipt_path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"  sha256   {receipt['sha256'][:16]}...")
        print(f"  size     {receipt['size_bytes']/1e6:.2f} MB")
        print(f"  duration {receipt['media']['duration']:.1f}s")
        print(f"  qc       {receipt['qc'].get('overall', 'n/a')}")
        print(f"  wrote    {receipt_path}")
        print(f"  cover    {'yes -> ' + str(cover_path) if cover_ok else 'FAILED'}")

        if receipt["qc"].get("overall") == "FAIL":
            worst_exit = 1

    return worst_exit


if __name__ == "__main__":
    sys.exit(main())
