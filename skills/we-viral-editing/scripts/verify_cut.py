"""We Viral cut verifier: sanity-checks a final-cut transcript before graphics work.

Reads a Words JSON (see transcribe.py) and reports, per cutting.md section 4:
  - gaps > 0.30s between consecutive words (with times)
  - zero-width words (start == end) - a splice artifact, flashes on screen
  - kept fragments < 0.8s between two gaps > 0.25s - reads as a double jump-cut
  - words longer than 14 chars with 2+ hyphens - a merged/mega-word token
  - last word end vs media duration - a clipped ending if the gap is too large
  - repeated 5-word n-grams - a retake that survived the cut
  - doubled sentence openers ("Well... well...", "يعني... يعني...")
  - with --script: script sentences missing or duplicated (fuzzy match)

Exits 1 if any ERROR-level finding was printed (WARN-level findings do not fail the run).

Usage:
  python verify_cut.py words.json
  python verify_cut.py words.json --media cut.mp4
  python verify_cut.py words.json --media cut.mp4 --script script.txt
"""
import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

GAP_WARN_S = 0.30
FRAGMENT_GAP_S = 0.25
FRAGMENT_MIN_S = 0.8
MEGA_WORD_MIN_LEN = 14
NGRAM_N = 5


def probe_duration(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return float((r.stdout or "0").strip() or 0.0)


def find_gaps(words):
    findings = []
    for i in range(1, len(words)):
        gap = words[i]["start"] - words[i - 1]["end"]
        if gap > GAP_WARN_S:
            findings.append(("WARN", f"gap {gap:.2f}s between \"{words[i-1]['text']}\" "
                                       f"(ends {words[i-1]['end']:.2f}) and \"{words[i]['text']}\" "
                                       f"(starts {words[i]['start']:.2f})"))
    return findings


def find_zero_width(words):
    findings = []
    for w in words:
        if w["end"] <= w["start"]:
            findings.append(("ERROR", f"zero-width word \"{w['text']}\" at {w['start']:.2f}s "
                                        f"(start == end, splice artifact)"))
    return findings


def find_fragments(words):
    """A kept run of words shorter than FRAGMENT_MIN_S, bounded on both sides by a gap
    > FRAGMENT_GAP_S (or the clip edges), reads as a double jump-cut."""
    findings = []
    if not words:
        return findings
    runs = []
    run_start = 0
    for i in range(1, len(words) + 1):
        if i == len(words) or (words[i]["start"] - words[i - 1]["end"]) > FRAGMENT_GAP_S:
            runs.append((run_start, i - 1))
            run_start = i
    for a, b in runs:
        span = words[b]["end"] - words[a]["start"]
        if span < FRAGMENT_MIN_S:
            text = " ".join(w["text"] for w in words[a:b + 1])
            findings.append(("WARN", f"fragment \"{text}\" is only {span:.2f}s "
                                       f"({words[a]['start']:.2f}-{words[b]['end']:.2f}s), "
                                       f"reads as a double jump-cut"))
    return findings


def find_mega_words(words):
    findings = []
    for w in words:
        text = w["text"]
        if len(text) > MEGA_WORD_MIN_LEN and text.count("-") >= 2:
            findings.append(("WARN", f"mega-word \"{text}\" at {w['start']:.2f}s "
                                       f"({len(text)} chars, {text.count('-')} hyphens) - likely a merged token"))
    return findings


def find_clipped_ending(words, media_duration):
    if not words or media_duration is None:
        return []
    last = words[-1]
    tail = media_duration - last["end"]
    if tail < -0.05:
        return [("ERROR", f"last word \"{last['text']}\" ends at {last['end']:.2f}s, "
                            f"AFTER media duration {media_duration:.2f}s - clipped/stale transcript")]
    if tail < 0.05:
        return [("WARN", f"last word \"{last['text']}\" ends at {last['end']:.2f}s, only "
                           f"{tail*1000:.0f} ms before media ends {media_duration:.2f}s - possible clipped ending")]
    return []


def find_repeated_ngrams(words):
    findings = []
    norm = [re.sub(r"[^\w']+", "", w["text"]).lower() for w in words]
    seen = {}
    for i in range(len(norm) - NGRAM_N + 1):
        gram = tuple(norm[i:i + NGRAM_N])
        if not all(gram):
            continue
        if gram in seen:
            first_i = seen[gram]
            findings.append(("WARN", f"repeated {NGRAM_N}-word phrase \"{' '.join(gram)}\" "
                                       f"at {words[first_i]['start']:.2f}s and again at {words[i]['start']:.2f}s"))
        else:
            seen[gram] = i
    return findings


SENTENCE_END_RE = re.compile(r"[.!?؟。]$")
OPENER_STOPWORDS = {
    "well", "so", "ok", "okay", "and", "but", "um", "uh",
    "يعني", "طيب", "وبعدين", "خلاصة",
}


def find_doubled_openers(words):
    findings = []
    sentence_starts = [0]
    for i, w in enumerate(words[:-1]):
        if SENTENCE_END_RE.search(w["text"]):
            sentence_starts.append(i + 1)
    for a, b in zip(sentence_starts, sentence_starts[1:]):
        if a >= len(words) or b >= len(words):
            continue
        wa = re.sub(r"[^\w]+", "", words[a]["text"]).lower()
        wb = re.sub(r"[^\w]+", "", words[b]["text"]).lower()
        if wa and wa == wb and wa in OPENER_STOPWORDS:
            findings.append(("WARN", f"doubled sentence opener \"{words[a]['text']}\" at "
                                       f"{words[a]['start']:.2f}s and \"{words[b]['text']}\" at {words[b]['start']:.2f}s"))
    return findings


def normalize_for_match(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s.lower())).strip()


def find_script_mismatches(words, script_text):
    findings = []
    cut_text = normalize_for_match(" ".join(w["text"] for w in words))
    sentences = [s.strip() for s in re.split(r"[.!?؟\n]+", script_text) if s.strip()]
    for sent in sentences:
        norm_sent = normalize_for_match(sent)
        if not norm_sent:
            continue
        sm = difflib.SequenceMatcher(None, norm_sent, cut_text)
        match = sm.find_longest_match(0, len(norm_sent), 0, len(cut_text))
        coverage = match.size / max(1, len(norm_sent))
        count = cut_text.count(norm_sent) if len(norm_sent) > 6 else 0
        if coverage < 0.6:
            findings.append(("ERROR", f"script line likely MISSING from cut: \"{sent[:80]}\" "
                                        f"(best match coverage {coverage*100:.0f}%)"))
        elif count > 1:
            findings.append(("WARN", f"script line appears {count}x in cut (possible duplicate retake): "
                                       f"\"{sent[:80]}\""))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words", help="words.json to verify (the FINAL cut's transcript)")
    ap.add_argument("--media", default=None, help="the cut media file, to check the ending isn't clipped")
    ap.add_argument("--script", default=None, help="plain-text script to check coverage/duplicates against")
    args = ap.parse_args()

    words_path = Path(args.words)
    if not words_path.exists():
        print(f"error: words file not found: {words_path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(words_path.read_text(encoding="utf-8"))
    words = data.get("words", [])
    if not words:
        print("error: no words in transcript", file=sys.stderr)
        sys.exit(1)

    media_duration = None
    if args.media:
        media_path = Path(args.media)
        if not media_path.exists():
            print(f"error: media file not found: {media_path}", file=sys.stderr)
            sys.exit(1)
        media_duration = probe_duration(media_path)
    else:
        media_duration = data.get("duration")

    findings = []
    findings += find_zero_width(words)
    findings += find_gaps(words)
    findings += find_fragments(words)
    findings += find_mega_words(words)
    findings += find_clipped_ending(words, media_duration)
    findings += find_repeated_ngrams(words)
    findings += find_doubled_openers(words)
    if args.script:
        script_path = Path(args.script)
        if not script_path.exists():
            print(f"error: script file not found: {script_path}", file=sys.stderr)
            sys.exit(1)
        findings += find_script_mismatches(words, script_path.read_text(encoding="utf-8"))

    n_errors = sum(1 for level, _ in findings if level == "ERROR")
    n_warns = sum(1 for level, _ in findings if level == "WARN")

    print(f"verify_cut.py: {len(words)} words checked, {n_errors} error(s), {n_warns} warning(s)")
    for level, msg in findings:
        print(f"  [{level}] {msg}")
    if not findings:
        print("  clean - no issues found")

    sys.exit(1 if n_errors else 0)


if __name__ == "__main__":
    main()
