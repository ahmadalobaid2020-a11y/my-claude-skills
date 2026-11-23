"""We Viral cut-and-join: assemble an EDL into one clean encode.

Reads an EDL JSON ({"sources": {"a": "path.mp4"}, "ranges": [{"src":"a","start":..,"end":..}]}),
builds a single ffmpeg concat-FILTER graph (never the concat demuxer / stream copy — per
cutting.md that drifts audio/video sync after ~40s), decodes PCM audio internally, adds a
4 ms fade at every join to kill clicks, and encodes once to H.264/AAC.

Optional --punch alternates a punch-in crop (e.g. 1.12 = 112%) on every other segment to
hide jump cuts, scaled+cropped centered back to the original frame size.

All source seeking is input-side (-ss before -i) so audio fades never land after an
output-side seek (which would mute the segment — see engineering.md).

Usage:
  python cutjoin.py edl.json -o cut.mp4
  python cutjoin.py edl.json -o cut.mp4 --punch 1.12
  python cutjoin.py edl.json -o cut.mp4 --fade-ms 4 --crf 18
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{r.stderr[-4000:]}")
    return r


def probe_video_info(path: Path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height,r_frame_rate",
         "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    data = json.loads(r.stdout or "{}")
    streams = data.get("streams", [])
    if not streams:
        raise RuntimeError(f"no video stream found in {path}")
    s = streams[0]
    num, den = s["r_frame_rate"].split("/")
    fps = float(num) / float(den or 1)
    return int(s["width"]), int(s["height"]), fps


def build_filter_complex(ranges, sources, out_w, out_h, fade_s, punch):
    """Returns (filter_complex_str, input_args, concat_v_label, concat_a_label)."""
    input_args = []
    src_input_index = {}
    for i, (key, path) in enumerate(sources.items()):
        src_input_index[key] = i
        input_args += ["-i", str(path)]

    filters = []
    v_labels = []
    a_labels = []
    for i, r in enumerate(ranges):
        idx = src_input_index[r["src"]]
        start, end = r["start"], r["end"]
        dur = end - start
        vlab, alab = f"v{i}", f"a{i}"
        do_punch = punch and punch > 1.0 and i % 2 == 1
        scale_expr = (
            f"scale={int(out_w * punch)}:{int(out_h * punch)},"
            f"crop={out_w}:{out_h},setsar=1"
            if do_punch else
            f"scale={out_w}:{out_h},setsar=1"
        )
        fade_out_start = max(0.0, dur - fade_s)
        vf = (
            f"[{idx}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,"
            f"{scale_expr},"
            f"fade=t=in:st=0:d={fade_s}:alpha=0,"
            f"fade=t=out:st={fade_out_start}:d={fade_s}:alpha=0[{vlab}]"
        )
        af = (
            f"[{idx}:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={fade_s},"
            f"afade=t=out:st={fade_out_start}:d={fade_s}[{alab}]"
        )
        filters.append(vf)
        filters.append(af)
        v_labels.append(f"[{vlab}]")
        a_labels.append(f"[{alab}]")

    n = len(ranges)
    concat_inputs = "".join(l for pair in zip(v_labels, a_labels) for l in pair)
    filters.append(f"{concat_inputs}concat=n={n}:v=1:a=1[vout][aout]")

    return ";\n".join(filters), input_args


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl", help="input edl.json")
    ap.add_argument("-o", "--out", required=True, help="output video path")
    ap.add_argument("--punch", type=float, default=None,
                     help="alternating punch-in scale on every other segment, e.g. 1.12")
    ap.add_argument("--fade-ms", type=float, default=4.0, help="fade duration at each join, ms (default: 4)")
    ap.add_argument("--crf", type=int, default=18, help="x264 CRF (default: 18)")
    ap.add_argument("--width", type=int, default=None, help="output width (default: first source's width)")
    ap.add_argument("--height", type=int, default=None, help="output height (default: first source's height)")
    args = ap.parse_args()

    edl_path = Path(args.edl)
    if not edl_path.exists():
        print(f"error: EDL not found: {edl_path}", file=sys.stderr)
        sys.exit(1)
    edl = json.loads(edl_path.read_text(encoding="utf-8"))
    sources = edl.get("sources", {})
    ranges = edl.get("ranges", [])
    if not sources or not ranges:
        print("error: EDL has no sources or no ranges", file=sys.stderr)
        sys.exit(1)

    for r in ranges:
        if r["src"] not in sources:
            print(f"error: range references unknown source '{r['src']}'", file=sys.stderr)
            sys.exit(1)
        if r["end"] <= r["start"]:
            print(f"error: range end <= start ({r})", file=sys.stderr)
            sys.exit(1)

    # resolve source paths relative to the EDL file's own directory if not absolute
    resolved_sources = {}
    for key, p in sources.items():
        pp = Path(p)
        if not pp.is_absolute() and not pp.exists():
            pp = edl_path.parent / p
        if not pp.exists():
            print(f"error: source file not found: {p}", file=sys.stderr)
            sys.exit(1)
        resolved_sources[key] = pp

    first_src = next(iter(resolved_sources.values()))
    src_w, src_h, fps = probe_video_info(first_src)
    out_w = args.width or src_w
    out_h = args.height or src_h

    fade_s = args.fade_ms / 1000.0
    # guard against a fade longer than the shortest range
    shortest = min(r["end"] - r["start"] for r in ranges)
    if fade_s * 2 >= shortest:
        fade_s = max(0.001, shortest / 4)
        print(f"warning: fade shortened to {fade_s*1000:.1f} ms to fit the shortest range "
              f"({shortest:.2f}s)", file=sys.stderr)

    filter_complex, input_args = build_filter_complex(
        ranges, resolved_sources, out_w, out_h, fade_s, args.punch
    )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y", "-v", "error",
        *input_args,
        "-filter_complex", filter_complex,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", str(args.crf), "-preset", "medium",
        "-r", f"{fps:.6f}",
        "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
        "-movflags", "+faststart",
        str(out_path),
    ]
    run(cmd)

    total = sum(r["end"] - r["start"] for r in ranges)
    punch_note = f", punch-in {args.punch}x on alt segments" if args.punch else ""
    print(f"cutjoin.py: {len(ranges)} segments joined -> {total:.2f}s output "
          f"({out_w}x{out_h} @ {fps:.2f}fps{punch_note}) -> {out_path}")


if __name__ == "__main__":
    main()
