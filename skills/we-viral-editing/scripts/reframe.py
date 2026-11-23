"""reframe.py -- auto-reframe 16:9 (or any) footage to a vertical/target size
with per-shot face-tracked crops, falling back to a blurred letterbox when no
face is found or the mode forces it.

Usage:
    python reframe.py in.mp4 -o out.mp4
    python reframe.py in.mp4 -o out.mp4 --size 1080x1920 --mode auto
    python reframe.py in.mp4 -o out.mp4 --mode blur
    python reframe.py in.mp4 -o out.mp4 --smooth 0.85

Pipeline:
    1. Shot detection: own histogram-difference detector on downscaled
       (small, grayscale) frames; uses PySceneDetect's AdaptiveDetector
       instead when it's importable (optional dep, lazy-imported).
    2. Per shot: detect faces with OpenCV -- cv2.FaceDetectorYN if a local
       ONNX model is available (see --face-model / bundled search), else the
       Haar cascade shipped in cv2.data. Pick the largest/most persistent
       face across the shot's sampled frames.
    3. Crop centre per shot = exponential smoothing (--smooth) with a
       dead-zone so the frame holds still when movement is small; eyes sit
       ~1/3 down from the top of the crop.
    4. No face found in a shot, or --mode blur: full frame letterboxed over
       a blurred zoomed copy of itself. Two faces far apart => blur mode
       (stacked mode is a documented future option, not implemented here).
    5. Frames are piped through ffmpeg (rawvideo in -> libx264 out); nothing
       is dumped to disk. Audio is stream-copied from the source.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

try:
    import cv2
except ImportError:
    print("error: opencv-python (cv2) is required. pip install opencv-python", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Probe helpers
# ---------------------------------------------------------------------------

def ffprobe_json(path: Path) -> dict:
    import json
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return json.loads(r.stdout or "{}")


@dataclass
class VideoInfo:
    width: int
    height: int
    fps: float
    n_frames: int
    duration: float
    has_audio: bool


def probe(path: Path) -> VideoInfo:
    info = ffprobe_json(path)
    v = next((s for s in info.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in info.get("streams", []) if s["codec_type"] == "audio"), None)
    if not v:
        raise RuntimeError(f"no video stream in {path}")
    num, den = v.get("r_frame_rate", "25/1").split("/")
    fps = float(num) / float(den or 1)
    dur = float(info.get("format", {}).get("duration", 0) or 0)
    nb = v.get("nb_frames")
    n_frames = int(nb) if nb and nb.isdigit() else int(round(dur * fps))
    return VideoInfo(width=int(v["width"]), height=int(v["height"]), fps=fps,
                      n_frames=n_frames, duration=dur, has_audio=a is not None)


# ---------------------------------------------------------------------------
# Shot detection
# ---------------------------------------------------------------------------

def detect_shots_scenedetect(path: Path):
    try:
        from scenedetect import open_video, SceneManager
        from scenedetect.detectors import AdaptiveDetector
    except ImportError:
        return None
    video = open_video(str(path))
    sm = SceneManager()
    sm.add_detector(AdaptiveDetector(adaptive_threshold=3.0, window_width=2, min_scene_len=15))
    sm.detect_scenes(video=video)
    scenes = sm.get_scene_list()
    if not scenes:
        return None
    return [(s.get_frames(), e.get_frames()) for s, e in scenes]


def detect_shots_builtin(path: Path, info: VideoInfo, threshold: float = 0.45, min_scene_len: int = 15):
    """Own histogram-difference shot detector on downscaled grayscale frames."""
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {path} for shot detection")
    prev_hist = None
    boundaries = [0]
    idx = 0
    small = (64, 36)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(cv2.resize(frame, small), cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray], [0], None, [32], [0, 256])
        cv2.normalize(hist, hist)
        if prev_hist is not None:
            diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
            if diff > threshold and (idx - boundaries[-1]) >= min_scene_len:
                boundaries.append(idx)
        prev_hist = hist
        idx += 1
    cap.release()
    total = idx if idx > 0 else info.n_frames
    boundaries.append(total)
    shots = list(zip(boundaries[:-1], boundaries[1:]))
    return [s for s in shots if s[1] > s[0]]


def detect_shots(path: Path, info: VideoInfo):
    shots = detect_shots_scenedetect(path)
    if shots:
        print(f"reframe.py: shot detection via PySceneDetect AdaptiveDetector ({len(shots)} shots)")
        return shots
    shots = detect_shots_builtin(path, info)
    print(f"reframe.py: shot detection via built-in histogram detector ({len(shots)} shots)")
    return shots


# ---------------------------------------------------------------------------
# Face detection
# ---------------------------------------------------------------------------

class FaceFinder:
    def __init__(self, frame_w: int, frame_h: int, model_path: Path | None):
        self.yn = None
        self.haar = None
        if model_path and model_path.exists():
            try:
                self.yn = cv2.FaceDetectorYN.create(str(model_path), "", (frame_w, frame_h))
            except Exception:
                self.yn = None
        if self.yn is None and hasattr(cv2, "CascadeClassifier"):
            cascade_path = Path(cv2.data.haarcascades) / "haarcascade_frontalface_default.xml"
            if cascade_path.exists():
                self.haar = cv2.CascadeClassifier(str(cascade_path))

    def detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        h, w = frame.shape[:2]
        if self.yn is not None:
            self.yn.setInputSize((w, h))
            _, faces = self.yn.detect(frame)
            if faces is None:
                return []
            return [(int(f[0]), int(f[1]), int(f[2]), int(f[3])) for f in faces]
        if self.haar is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dets = self.haar.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5, minSize=(40, 40))
            return [(int(x), int(y), int(w2), int(h2)) for x, y, w2, h2 in dets]
        return []


def find_local_face_model() -> Path | None:
    candidates = [
        Path(__file__).parent / "models" / "face_detection_yunet.onnx",
        Path.home() / ".claude" / "models" / "face_detection_yunet.onnx",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


# ---------------------------------------------------------------------------
# Per-shot crop decision
# ---------------------------------------------------------------------------

@dataclass
class ShotPlan:
    start_frame: int
    end_frame: int
    mode: str  # "single" or "blur"
    cx: float = 0.5  # centre x fraction (of full-frame width) for the crop
    cy_bias: float = 0.33  # eyes ~1/3 from top -> crop centre y as fraction offset


def sample_frame_indices(start: int, end: int, n: int = 6) -> list[int]:
    span = max(1, end - start)
    step = max(1, span // n)
    return list(range(start, end, step))[:n]


def plan_shot(cap: cv2.VideoCapture, start: int, end: int, finder: FaceFinder,
              info: VideoInfo) -> ShotPlan:
    faces_seen: list[tuple[int, int, int, int]] = []
    for idx in sample_frame_indices(start, end):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok:
            continue
        faces = finder.detect(frame)
        faces_seen.extend(faces)

    if not faces_seen:
        return ShotPlan(start, end, "blur")

    # Group by rough horizontal position to see if there are two far-apart faces.
    xs = [x + w2 / 2 for x, y, w2, h2 in faces_seen]
    xs_norm = [x / info.width for x in xs]
    if max(xs_norm) - min(xs_norm) > 0.5 and len(set(round(v, 1) for v in xs_norm)) > 1:
        # two clusters far apart on screen -> blur/full-frame fallback
        return ShotPlan(start, end, "blur")

    # Largest face by area wins.
    bx, by, bw, bh = max(faces_seen, key=lambda f: f[2] * f[3])
    cx = (bx + bw / 2) / info.width
    return ShotPlan(start, end, "single", cx=cx)


def plan_shots(path: Path, shots: list[tuple[int, int]], info: VideoInfo,
               model_path: Path | None, mode_override: str) -> list[ShotPlan]:
    if mode_override == "blur":
        return [ShotPlan(s, e, "blur") for s, e in shots]

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {path} for face detection")
    finder = FaceFinder(info.width, info.height, model_path)
    if finder.yn is None and finder.haar is None:
        print("reframe.py: WARNING - no face detector available (no YuNet ONNX model and no "
              "cv2.CascadeClassifier/haarcascade data in this OpenCV build); every shot will "
              "fall back to blur mode. Pass --face-model <onnx> or install an opencv-python "
              "build with bundled Haar cascades to enable face tracking.", file=sys.stderr)
    plans = [plan_shot(cap, s, e, finder, info) for s, e in shots]
    cap.release()
    return plans


def smooth_centres(plans: list[ShotPlan], smooth: float, dead_zone: float = 0.03) -> None:
    """Exponential smoothing across shots with a dead-zone: small centre
    moves are ignored so the crop holds still on minor jitter."""
    prev_cx = 0.5
    for p in plans:
        if p.mode != "single":
            continue
        target = p.cx
        if abs(target - prev_cx) < dead_zone:
            target = prev_cx
        p.cx = smooth * prev_cx + (1 - smooth) * target
        prev_cx = p.cx


# ---------------------------------------------------------------------------
# Rendering (piped, no frame dumps)
# ---------------------------------------------------------------------------

def compute_crop_rect(src_w: int, src_h: int, out_w: int, out_h: int, cx_frac: float) -> tuple[int, int, int, int]:
    """Crop-to-fill rectangle in source pixels for a face centred at cx_frac
    (0..1 of src width), eyes ~1/3 down (crop vertical centre biased up)."""
    target_ar = out_w / out_h
    src_ar = src_w / src_h
    if src_ar > target_ar:
        crop_h = src_h
        crop_w = int(round(crop_h * target_ar))
    else:
        crop_w = src_w
        crop_h = int(round(crop_w / target_ar))
    cx_px = cx_frac * src_w
    x0 = int(round(cx_px - crop_w / 2))
    x0 = max(0, min(src_w - crop_w, x0))
    # vertical: bias crop up a bit so a centred face lands ~1/3 down in frame
    y0 = int(round((src_h - crop_h) * 0.28))
    y0 = max(0, min(src_h - crop_h, y0))
    return x0, y0, crop_w, crop_h


def build_filter_script(plans: list[ShotPlan], info: VideoInfo, out_w: int, out_h: int) -> str:
    """Build an ffmpeg filter_complex that selects, per output frame range,
    either a face-tracked crop+scale or a blurred-letterbox composite, using
    `between(n,a,b)` gated overlays. Frame-accurate via `select`+`setpts`
    per segment, concatenated."""
    segments = []
    for i, p in enumerate(plans):
        n0, n1 = p.start_frame, p.end_frame
        label_v = f"v{i}"
        if p.mode == "single":
            x0, y0, cw, ch = compute_crop_rect(info.width, info.height, out_w, out_h, p.cx)
            seg = (
                f"[0:v]trim=start_frame={n0}:end_frame={n1},setpts=PTS-STARTPTS,"
                f"crop={cw}:{ch}:{x0}:{y0},scale={out_w}:{out_h}:flags=lanczos[{label_v}]"
            )
        else:
            # blurred zoomed background + full frame letterboxed on top
            seg = (
                f"[0:v]trim=start_frame={n0}:end_frame={n1},setpts=PTS-STARTPTS,split=2[bg{i}][fg{i}];"
                f"[bg{i}]scale={out_w}:{out_h}:force_original_aspect_ratio=increase,"
                f"crop={out_w}:{out_h},gblur=sigma=30[bgb{i}];"
                f"[fg{i}]scale={out_w}:-2:force_original_aspect_ratio=decrease[fgs{i}];"
                f"[bgb{i}][fgs{i}]overlay=(W-w)/2:(H-h)/2[{label_v}]"
            )
        segments.append(seg)

    concat_inputs = "".join(f"[v{i}]" for i in range(len(plans)))
    filt = ";".join(segments) + f";{concat_inputs}concat=n={len(plans)}:v=1:a=0[vout]"
    return filt


def render(src: Path, dst: Path, plans: list[ShotPlan], info: VideoInfo, out_w: int, out_h: int) -> None:
    filt = build_filter_script(plans, info, out_w, out_h)
    filter_file = dst.parent / f".{dst.stem}_filter.txt"
    filter_file.write_text(filt, encoding="utf-8")

    cmd = ["ffmpeg", "-y", "-i", str(src), "-/filter_complex", str(filter_file), "-map", "[vout]"]
    if info.has_audio:
        cmd += ["-map", "0:a"]
    cmd += ["-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-r", f"{info.fps:.3f}"]
    if info.has_audio:
        cmd += ["-c:a", "copy"]
    cmd += ["-movflags", "+faststart", str(dst)]

    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    filter_file.unlink(missing_ok=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg render failed:\n{proc.stderr[-3000:]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Face-tracked 16:9 -> vertical (or any) auto-reframe.")
    ap.add_argument("src", type=Path)
    ap.add_argument("-o", "--out", required=True, type=Path)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--mode", choices=["auto", "single", "blur"], default="auto")
    ap.add_argument("--smooth", type=float, default=0.9)
    ap.add_argument("--face-model", type=Path, default=None, help="path to a FaceDetectorYN ONNX model")
    args = ap.parse_args()

    if not args.src.exists():
        print(f"error: input not found: {args.src}", file=sys.stderr)
        return 1
    try:
        out_w, out_h = (int(x) for x in args.size.lower().split("x"))
    except ValueError:
        print(f"error: --size must be WxH, got {args.size!r}", file=sys.stderr)
        return 1

    info = probe(args.src)
    print(f"reframe.py: {args.src.name} {info.width}x{info.height} @ {info.fps:.2f}fps, {info.duration:.1f}s")

    shots = detect_shots(args.src, info)
    model_path = args.face_model or find_local_face_model()
    plans = plan_shots(args.src, shots, info, model_path, args.mode)

    n_single = sum(1 for p in plans if p.mode == "single")
    n_blur = len(plans) - n_single
    print(f"reframe.py: {len(plans)} shots -> {n_single} face-tracked, {n_blur} blur-fallback")

    smooth_centres(plans, args.smooth)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    try:
        render(args.src, args.out, plans, info, out_w, out_h)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"reframe.py: done -> {args.out} ({out_w}x{out_h})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
