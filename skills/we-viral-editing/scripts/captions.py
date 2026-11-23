"""captions.py -- build burned-in style captions (ASS) from a Words JSON transcript.

Groups words into short on-screen cues (house rule: 2-4 words, ~1.2s max,
break on inter-word gaps >= ~0.25s or sentence punctuation), writes an ASS
subtitle file sized to the target video canvas, a matching cues JSON next to
it, and optionally burns the result into a video with ffmpeg (libass).

Words JSON format (see references/captions.md / SCRIPTS-SPEC.md):
    {"engine": "scribe|whisper", "language": "en", "duration": 12.3,
     "words": [{"text": "...", "start": 0.12, "end": 0.48}, ...]}

Cues JSON format (written next to the .ass, same basename):
    {"cues": [{"start": 0.0, "end": 1.1, "text": "SO WE BUILT",
               "words": [{"text": "SO", "start": 0.0, "end": 0.3, "key": false}, ...]}]}

Usage:
    python captions.py words.json -o captions.ass
    python captions.py words.json -o captions.ass --style pill --accent "#FFD400"
    python captions.py words.json -o captions.ass --style keyword --keywords "50%,free,AI"
    python captions.py words.json -o captions.ass --style karaoke --burn in.mp4 out.mp4
    python captions.py words.json -o captions.ass --style word-build --size 72 --y 0.7

Styles:
    pill         opaque rounded-ish box (BorderStyle 3) in accent colour, white text
    keyword      white text + soft shadow; numbers/prices/percentages (or --keywords)
                 highlighted in the accent colour
    white-label  dark text on a white/light box
    karaoke      per-word \\kf fill sweep to the accent colour
    word-build   words appear one at a time as they are spoken (reveal)

Notes:
    - Arabic/RTL text is passed through untouched; libass + HarfBuzz/FriBidi
      (this ffmpeg build has --enable-libass --enable-libfribidi
      --enable-libharfbuzz) shape and reorder it correctly. Do not reverse or
      re-order the string yourself.
    - --burn escapes the input path for the ffmpeg subtitles filter (Windows
      drive-letter colons and backslashes) and copies audio.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Cue grouping
# ---------------------------------------------------------------------------

SENTENCE_END = re.compile(r"[.!?\u061F\u06D4]\s*$")  # incl. Arabic question mark / full stop


def load_words(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "words" not in data or not isinstance(data["words"], list):
        raise ValueError("words.json missing a 'words' list")
    for w in data["words"]:
        if "text" not in w or "start" not in w or "end" not in w:
            raise ValueError(f"malformed word entry: {w}")
    return data


def group_cues(words: list[dict], max_words: int, max_dur: float, gap_break: float) -> list[dict]:
    """Break the word stream into cues. First trigger to fire wins:
    (a) max_words reached, (b) adding the word would exceed max_dur,
    (c) inter-word gap >= gap_break, (d) previous word ends a sentence.
    One line only; cues never overlap.
    """
    cues: list[dict] = []
    cur: list[dict] = []

    def flush():
        if not cur:
            return
        text = " ".join(w["text"] for w in cur).strip()
        cues.append({
            "start": cur[0]["start"],
            "end": cur[-1]["end"],
            "text": text,
            "words": [dict(w) for w in cur],
        })
        cur.clear()

    prev_end = None
    for w in words:
        text = (w.get("text") or "").strip()
        if not text:
            continue
        start, end = float(w["start"]), float(w["end"])
        if end < start:
            end = start
        gap = (start - prev_end) if prev_end is not None else 0.0

        if cur:
            would_span = end - cur[0]["start"]
            if gap >= gap_break or len(cur) >= max_words or would_span > max_dur:
                flush()

        cur.append({"text": text, "start": start, "end": end})
        prev_end = end

        if SENTENCE_END.search(text):
            flush()
            prev_end = None

    flush()

    # Guard against overlaps introduced by lead-shift later; keep raw here.
    return cues


def apply_lead(cues: list[dict], lead: float, duration: float | None) -> None:
    """Shift every cue's display window `lead` seconds earlier, clamped to
    not run before 0 or overlap the previous cue's (already shifted) end."""
    prev_end = 0.0
    for i, c in enumerate(cues):
        shifted_start = max(0.0, c["start"] - lead)
        shifted_end = max(shifted_start, c["end"] - lead)
        if shifted_start < prev_end:
            shifted_start = prev_end
        if shifted_end <= shifted_start:
            shifted_end = shifted_start + 0.05
        c["start"], c["end"] = shifted_start, shifted_end
        prev_end = c["end"]
    if duration:
        for c in cues:
            c["end"] = min(c["end"], duration)
            c["start"] = min(c["start"], c["end"])


# ---------------------------------------------------------------------------
# Keyword detection
# ---------------------------------------------------------------------------

KEYWORD_RE = re.compile(
    r"^\$?\d[\d,.]*%?$"            # 50, 50%, $300, 1,000.50
    r"|^\d[\d,.]*(k|m|x)$"         # 10k 3m 2x
    , re.IGNORECASE,
)


def is_auto_keyword(word: str) -> bool:
    w = word.strip().strip(".,!?").replace(",", "")
    if not w:
        return False
    return bool(KEYWORD_RE.match(w))


def mark_keywords(cues: list[dict], keyword_list: set[str] | None) -> None:
    for c in cues:
        for w in c["words"]:
            token = w["text"].strip().strip(".,!?").lower()
            if keyword_list is not None:
                w["key"] = token in keyword_list
            else:
                w["key"] = is_auto_keyword(w["text"])


# ---------------------------------------------------------------------------
# ASS writing
# ---------------------------------------------------------------------------

def hex_to_ass_bgr(hexcolor: str) -> str:
    """'#RRGGBB' -> ASS '&HBBGGRR&' (no alpha)."""
    h = hexcolor.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"bad hex colour: {hexcolor}")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{b}{g}{r}&".upper()


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}").replace("\n", "\\N")


def ts(t: float) -> str:
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    cs = int(round((s - int(s)) * 100))
    if cs == 100:
        cs = 0
        s += 1
    return f"{h:01d}:{m:02d}:{int(s):02d}.{cs:02d}"


def build_header(width: int, height: int, style: str, font: str, size: int, accent: str, y_frac: float) -> str:
    accent_bgr = hex_to_ass_bgr(accent)
    margin_v = max(0, int(round(height * (1.0 - y_frac))))

    # Default palette per style. White/label styles differ in fill/outline.
    if style == "white-label":
        primary = "&H00141414&"     # near-black text (BGR, alpha 00 = opaque)
        outline = "&H00FFFFFF&"     # white
        back = "&H00FFFFFF&"
        border_style = 3
        outline_w = 0
        shadow = 0
    elif style == "pill":
        primary = "&H00FFFFFF&"     # white text
        outline = accent_bgr
        back = accent_bgr
        border_style = 3
        outline_w = 18
        shadow = 0
    elif style == "karaoke":
        primary = "&H00FFFFFF&"
        outline = "&H00000000&"
        back = "&H80000000&"
        border_style = 1
        outline_w = 3
        shadow = 2
    else:  # keyword, word-build
        primary = "&H00FFFFFF&"
        outline = "&H00000000&"
        back = "&H80000000&"
        border_style = 1
        outline_w = 3
        shadow = 2

    return f"""[Script Info]
Title: We Viral captions ({style})
ScriptType: v4.00+
WrapStyle: 2
ScaledBorderAndShadow: yes
PlayResX: {width}
PlayResY: {height}
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{size},{primary},&H000000FF&,{outline},{back},1,0,0,0,100,100,0,0,{border_style},{outline_w},{shadow},2,80,80,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def render_line_plain(cue: dict, accent_override: str | None) -> str:
    text = ass_escape(cue["text"].upper() if cue["text"].isascii() else cue["text"])
    return text


def render_line_keyword(cue: dict, accent: str) -> str:
    parts = []
    for w in cue["words"]:
        t = w["text"]
        disp = t.upper() if t.isascii() else t
        disp = ass_escape(disp)
        if w.get("key"):
            parts.append(f"{{\\c{accent}}}{disp}{{\\c&HFFFFFF&}}")
        else:
            parts.append(disp)
    return " ".join(parts)


def render_line_karaoke(cue: dict, accent: str) -> str:
    parts = []
    for w in cue["words"]:
        dur_cs = max(1, int(round((w["end"] - w["start"]) * 100)))
        t = w["text"]
        disp = t.upper() if t.isascii() else t
        disp = ass_escape(disp)
        parts.append(f"{{\\kf{dur_cs}\\1c{accent}}}{disp} ")
    return "".join(parts).strip()


def write_ass(cues: list[dict], out_path: Path, width: int, height: int, style: str,
              font: str, size: int, accent: str, y_frac: float) -> None:
    accent_ass = hex_to_ass_bgr(accent)
    lines = [build_header(width, height, style, font, size, accent, y_frac)]

    if style == "word-build":
        # Emit one event per word, cumulative text up to that word, each event
        # spans until the cue ends so later words simply extend the line.
        for cue in cues:
            words = cue["words"]
            for i, w in enumerate(words):
                seg_start = w["start"]
                seg_end = words[i + 1]["start"] if i + 1 < len(words) else cue["end"]
                if seg_end <= seg_start:
                    continue
                partial = " ".join(x["text"] for x in words[: i + 1])
                disp = partial.upper() if partial.isascii() else partial
                lines.append(f"Dialogue: 0,{ts(seg_start)},{ts(seg_end)},Default,,0,0,0,,{ass_escape(disp)}\n")
        out_path.write_text("".join(lines), encoding="utf-8")
        return

    for cue in cues:
        if style == "keyword":
            text = render_line_keyword(cue, accent_ass)
        elif style == "karaoke":
            text = render_line_karaoke(cue, accent_ass)
        else:  # pill, white-label
            text = render_line_plain(cue, None)
        lines.append(f"Dialogue: 0,{ts(cue['start'])},{ts(cue['end'])},Default,,0,0,0,,{text}\n")

    out_path.write_text("".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# Burn-in
# ---------------------------------------------------------------------------

def escape_ffmpeg_filter_path(p: Path) -> str:
    """Escape a Windows path for use inside an ffmpeg filtergraph string.
    Drive-letter colons and backslashes both need escaping inside the
    subtitles= filter argument."""
    s = str(p.resolve())
    s = s.replace("\\", "/")   # forward slashes avoid backslash-escaping entirely
    s = s.replace(":", "\\:")
    return s


def burn(ass_path: Path, src: Path, dst: Path, fontsdir: Path | None) -> None:
    filt = f"subtitles='{escape_ffmpeg_filter_path(ass_path)}'"
    if fontsdir:
        fd = escape_ffmpeg_filter_path(fontsdir)
        filt += f":fontsdir='{fd}'"
    cmd = [
        "ffmpeg", "-y", "-i", str(src),
        "-vf", filt,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(dst),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg burn failed:\n{proc.stderr[-3000:]}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Build ASS captions from a Words JSON transcript.")
    ap.add_argument("words_json", type=Path)
    ap.add_argument("-o", "--out", required=True, type=Path, help="output .ass path")
    ap.add_argument("--style", choices=["pill", "keyword", "white-label", "karaoke", "word-build"], default="keyword")
    ap.add_argument("--accent", default="#FFD400", help="accent hex colour, e.g. #FFD400")
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--fontsdir", type=Path, default=None)
    ap.add_argument("--size", type=int, default=64)
    ap.add_argument("--y", type=float, default=0.67, help="fraction of height where the line sits (house 0.62-0.72)")
    ap.add_argument("--keywords", default=None, help="comma-separated keyword list; default is auto (numbers/prices/percentages)")
    ap.add_argument("--lead", type=float, default=0.13, help="seconds to shift display earlier than speech")
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--max-dur", type=float, default=1.2)
    ap.add_argument("--gap-break", type=float, default=0.25)
    ap.add_argument("--canvas", default="1080x1920", help="WxH, default 1080x1920")
    ap.add_argument("--burn", nargs=2, metavar=("IN_VIDEO", "OUT_VIDEO"), default=None)
    args = ap.parse_args()

    try:
        width, height = (int(x) for x in args.canvas.lower().split("x"))
    except ValueError:
        print(f"error: --canvas must be WxH, got {args.canvas!r}", file=sys.stderr)
        return 1

    try:
        data = load_words(args.words_json)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    words = data["words"]
    if not words:
        print("error: no words in input", file=sys.stderr)
        return 1

    cues = group_cues(words, args.max_words, args.max_dur, args.gap_break)
    apply_lead(cues, args.lead, data.get("duration"))

    keyword_set = None
    if args.keywords:
        keyword_set = {k.strip().lower() for k in args.keywords.split(",") if k.strip()}
    mark_keywords(cues, keyword_set)

    # overlap sanity check
    for i in range(1, len(cues)):
        if cues[i]["start"] < cues[i - 1]["end"] - 1e-6:
            cues[i]["start"] = cues[i - 1]["end"]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    write_ass(cues, args.out, width, height, args.style, args.font, args.size, args.accent, args.y)

    cues_json_path = args.out.with_suffix(".cues.json")
    cues_json_path.write_text(json.dumps({"cues": cues}, ensure_ascii=False, indent=2), encoding="utf-8")

    total_dur = sum(c["end"] - c["start"] for c in cues)
    print(f"captions.py: {len(cues)} cues, style={args.style}, canvas={width}x{height}")
    print(f"  wrote {args.out}")
    print(f"  wrote {cues_json_path}")

    if args.burn:
        src, dst = Path(args.burn[0]), Path(args.burn[1])
        if not src.exists():
            print(f"error: burn input not found: {src}", file=sys.stderr)
            return 1
        try:
            burn(args.out, src, dst, args.fontsdir)
        except Exception as e:
            print(f"error: {e}", file=sys.stderr)
            return 1
        print(f"  burned -> {dst}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
