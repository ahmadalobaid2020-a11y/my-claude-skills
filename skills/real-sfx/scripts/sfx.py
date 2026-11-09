#!/usr/bin/env python3
"""Real (recorded, not synthesised) sound effects for videos and audio.

  sfx.py search QUERY [--max 3] [--n 10] [--any-license]
      Search Freesound (CC0 only by default). Needs FREESOUND_API_KEY.
  sfx.py get ID [ID ...] [--dir ~/.claude/sfx]
      Download the HQ preview of each Freesound sound, plus a credits line.
  sfx.py mix INPUT --cue TIME=FILE[@DB][>FADE] [--cue ...] [--cues FILE] [--out OUT]
      Place sound files at timestamps and mix them under the original audio.

Cue syntax: 00:12.5=whoosh.mp3@-8>0.3  -> at 12.5 s, whoosh.mp3, -8 dB, 0.3 s fade-out.
TIME is SS, MM:SS or HH:MM:SS (decimals allowed). FILE is a path, or a name/ID
looked up in the sfx dir. --cues reads one cue per line (# comments allowed).
"""
import argparse, glob, json, os, re, subprocess, sys, urllib.error, urllib.parse, urllib.request

API = "https://freesound.org/apiv2"
DIR = os.path.expanduser("~/.claude/sfx")


def secs(t):
    parts = [float(p) for p in t.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def api(path, **params):
    # Key goes in the Authorization header (Freesound's "Token" scheme). In a sandbox whose
    # proxy injects the key, FREESOUND_API_KEY can be unset: the placeholder gets replaced.
    key = os.environ.get("FREESOUND_API_KEY", "proxy-injected")
    req = urllib.request.Request(f"{API}{path}?{urllib.parse.urlencode(params)}",
                                 headers={"Authorization": f"Token {key}"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            sys.exit("Freesound refused the key: set FREESOUND_API_KEY "
                     "(free key: https://freesound.org/apiv2/apply)")
        raise


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "sound"


def cmd_search(a):
    flt = f"duration:[0 TO {a.max}]"
    if not a.any_license:
        flt += ' license:"Creative Commons 0"'
    r = api("/search/text/", query=a.query, filter=flt, page_size=a.n, sort="score",
            fields="id,name,duration,license,username,avg_rating,num_downloads")
    if not r["results"]:
        print("no results; try a broader word or --max 6")
    for s in r["results"]:
        lic = "CC0" if "publicdomain/zero" in s["license"] else s["license"]
        print(f'{s["id"]:>8}  {s["duration"]:5.2f}s  {s["num_downloads"]:>7} dl  '
              f'{s.get("avg_rating") or 0:.1f}*  {lic}  {s["name"]}  (by {s["username"]})')


def cmd_get(a):
    os.makedirs(a.dir, exist_ok=True)
    for sid in a.ids:
        s = api(f"/sounds/{sid}/", fields="id,name,license,username,url,previews")
        dst = os.path.join(a.dir, f'{s["id"]}-{slug(os.path.splitext(s["name"])[0])}.mp3')
        urllib.request.urlretrieve(s["previews"]["preview-hq-mp3"], dst)
        lic = "CC0" if "publicdomain/zero" in s["license"] else s["license"]
        with open(os.path.join(a.dir, "CREDITS.txt"), "a") as f:
            f.write(f'{os.path.basename(dst)}\t"{s["name"]}" by {s["username"]}\t{lic}\t{s["url"]}\n')
        print(dst)


def resolve(name, d):
    if os.path.isfile(name):
        return os.path.abspath(name)
    hits = sorted(glob.glob(os.path.join(d, f"{name}*")) + glob.glob(os.path.join(d, f"*{name}*")))
    hits = [h for h in hits if not h.endswith(".txt")]
    if not hits:
        sys.exit(f"sound not found: {name} (looked in . and {d})")
    return hits[0]


def parse_cue(c, d):
    m = re.fullmatch(r"\s*([\d:.]+)\s*=\s*(.+?)(?:@(-?[\d.]+))?(?:>([\d.]+))?\s*", c)
    if not m:
        sys.exit(f"bad cue: {c!r}  (want TIME=FILE[@DB][>FADE])")
    t, f, db, fade = m.groups()
    return secs(t), resolve(f, d), float(db) if db else -6.0, float(fade) if fade else 0.0


def probe(path, what):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", what, "-show_entries",
                           "stream=codec_type:format=duration", "-of", "json", path],
                          capture_output=True, text=True, check=True).stdout


def cmd_mix(a):
    src = os.path.abspath(a.input)
    lines = list(a.cue or [])
    if a.cues:
        lines += [l.split("#")[0] for l in open(a.cues, encoding="utf-8")]
    cues = [parse_cue(l, a.dir) for l in lines if l.strip()]
    if not cues:
        sys.exit("no cues given")
    has_video = bool(json.loads(probe(src, "v")).get("streams"))
    has_audio = bool(json.loads(probe(src, "a")).get("streams"))
    dur = float(json.loads(probe(src, "a" if has_audio else "v"))["format"]["duration"])
    out = a.out or f"{os.path.splitext(src)[0]}.sfx{os.path.splitext(src)[1]}"

    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-nostdin", "-i", src]
    parts, labels, placed = [], [], []
    if has_audio:
        parts.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,volume={a.base}dB[base]")
    else:
        parts.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{dur}[base]")
    labels.append("[base]")
    for i, (t, f, db, fade) in enumerate(cues, 1):
        if t >= dur:
            print(f"skip cue at {t:.2f}s: past the end ({dur:.2f}s)", file=sys.stderr)
            continue
        cmd += ["-i", f]
        placed.append((t, f, db))
        chain = f"[{len(labels)}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB"
        if fade > 0:
            flen = float(json.loads(probe(f, "a"))["format"]["duration"])
            chain += f",afade=t=out:st={max(0.0, flen - fade):.3f}:d={fade}"
        ms = int(round(t * 1000))
        parts.append(f"{chain},adelay={ms}|{ms}[s{i}]")
        labels.append(f"[s{i}]")
    # normalize=0 keeps every input at its own level; the limiter catches peaks
    parts.append(f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
                 "alimiter=limit=0.89:attack=3:release=50:level=false[mix]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[mix]"]
    ext = os.path.splitext(out)[1].lower()
    if has_video and ext not in (".wav", ".mp3", ".m4a"):
        cmd += ["-map", "0:v", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k"]
    elif ext == ".wav":
        cmd += ["-c:a", "pcm_s16le"]
    elif ext == ".mp3":
        cmd += ["-c:a", "libmp3lame", "-q:a", "2"]
    else:
        cmd += ["-c:a", "aac", "-b:a", "192k"]
    subprocess.run(cmd + [out], check=True)
    for t, f, db in placed:
        print(f"{t:8.2f}s  {db:+.1f} dB  {os.path.basename(f)}")
    print(f"output: {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query")
    s.add_argument("--max", type=float, default=3, help="max duration in seconds")
    s.add_argument("--n", type=int, default=10); s.add_argument("--any-license", action="store_true")
    g = sub.add_parser("get"); g.add_argument("ids", nargs="+"); g.add_argument("--dir", default=DIR)
    m = sub.add_parser("mix"); m.add_argument("input")
    m.add_argument("--cue", action="append"); m.add_argument("--cues")
    m.add_argument("--base", type=float, default=0.0, help="gain on the original audio in dB")
    m.add_argument("--dir", default=DIR); m.add_argument("--out")
    a = p.parse_args()
    {"search": cmd_search, "get": cmd_get, "mix": cmd_mix}[a.cmd](a)


if __name__ == "__main__":
    main()
