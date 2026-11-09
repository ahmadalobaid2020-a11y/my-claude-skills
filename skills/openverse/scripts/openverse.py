#!/usr/bin/env python3
"""Search and download openly licensed audio and images from Openverse (no API key).

  openverse.py audio QUERY [--license cc0] [--max 3] [--source freesound] [--n 10]
  openverse.py image QUERY [--license cc0] [--commercial] [--modify] [--n 10]
  openverse.py get audio|image ID [ID ...] [--dir DIR]

audio --max is the longest clip in seconds (filtered here; 0 = any length).
--license takes Openverse codes: cc0, pdm, by, by-sa, by-nd, by-nc, by-nc-sa, by-nc-nd
(comma separated). --commercial / --modify keep only licences that allow that use.
get saves the file and appends its attribution to CREDITS.txt in the same folder.
Default folders: audio -> ~/.claude/sfx (where real-sfx looks), image -> ./openverse.
"""
import argparse, json, os, re, sys, urllib.error, urllib.parse, urllib.request

API = "https://api.openverse.org/v1"
EP = {"audio": "audio", "image": "images"}
# Identifies this tool honestly, as Openverse and Wikimedia ask automated clients to do.
UA = "my-claude-skills-openverse/1.0 (https://github.com/ahmadalobaid2020-a11y/my-claude-skills)"


def fetch(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read() if raw else json.load(r)


def query(kind, q, a):
    p = {"q": q, "page_size": min(a.n * (4 if kind == "audio" and a.max else 1), 50)}
    if a.license:
        p["license"] = a.license
    if getattr(a, "source", None):
        p["source"] = a.source
    lt = [x for x, on in (("commercial", a.commercial), ("modification", a.modify)) if on]
    if lt:
        p["license_type"] = ",".join(lt)
    return fetch(f"{API}/{EP[kind]}/?{urllib.parse.urlencode(p)}")


def lic(r):
    l = r["license"]
    return l.upper() if l in ("cc0", "pdm") else f'CC {l.upper()} {r.get("license_version") or ""}'.strip()


def cmd_search(kind, a):
    d = query(kind, a.query, a)
    rows = d["results"]
    if kind == "audio" and a.max:
        rows = [r for r in rows if r.get("duration") and r["duration"] <= a.max * 1000]
    rows = rows[: a.n]
    print(f'{d["result_count"]} matches on Openverse, showing {len(rows)}')
    for r in rows:
        if kind == "audio":
            size = f'{(r.get("duration") or 0) / 1000:5.2f}s'
        else:
            size = f'{r.get("width") or "?"}x{r.get("height") or "?"}'
        print(f'{r["id"]}  {size:>10}  {lic(r):<14} {r["source"]:<16} '
              f'{r["title"][:50]}  (by {r.get("creator") or "unknown"})')


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:40] or "file"


def cmd_get(a):
    d = os.path.expanduser(a.dir or ("~/.claude/sfx" if a.kind == "audio" else "./openverse"))
    os.makedirs(d, exist_ok=True)
    failed = 0
    for i in a.ids:
        r = fetch(f"{API}/{EP[a.kind]}/{i}/")
        ext = (r.get("filetype") or os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1][1:] or "bin").lower()
        dst = os.path.join(d, f'{i[:8]}-{slug(r["title"])}.{ext}')
        try:
            data = fetch(r["url"], raw=True)
        except urllib.error.URLError as e:
            if a.kind != "image":
                failed += 1
                print(f'FAILED {i}: host refused the download ({e}). '
                      f'Download it by hand from {r["foreign_landing_url"]}', file=sys.stderr)
                continue
            # images: Openverse serves its own copy, smaller than the original
            data = fetch(f"{API}/images/{i}/thumb/?full_size=true", raw=True)
            dst = os.path.splitext(dst)[0] + ".thumb.jpg"
            print(f"original refused ({e}); saved Openverse's resized copy", file=sys.stderr)
        with open(dst, "wb") as f:
            f.write(data)
        with open(os.path.join(d, "CREDITS.txt"), "a", encoding="utf-8") as f:
            f.write(f'{os.path.basename(dst)}\t{r.get("attribution") or r["title"]}\t{r["foreign_landing_url"]}\n')
        print(dst)
    if failed:
        sys.exit(1)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for kind in ("audio", "image"):
        s = sub.add_parser(kind)
        s.add_argument("query")
        s.add_argument("--license", default=None)
        s.add_argument("--commercial", action="store_true")
        s.add_argument("--modify", action="store_true")
        s.add_argument("--n", type=int, default=10)
        s.add_argument("--source", default=None)
        if kind == "audio":
            s.add_argument("--max", type=float, default=0)
        s.set_defaults(func=lambda a, k=kind: cmd_search(k, a), max=0)
    g = sub.add_parser("get")
    g.add_argument("kind", choices=["audio", "image"])
    g.add_argument("ids", nargs="+")
    g.add_argument("--dir", default=None)
    g.set_defaults(func=cmd_get)
    a = p.parse_args()
    try:
        a.func(a)
    except urllib.error.HTTPError as e:
        if not e.url.startswith(API):
            raise
        if e.code == 404:
            sys.exit("Openverse: not found (check the ID and that audio/image matches it)")
        sys.exit(f"Openverse API error {e.code}: {e.read()[:300].decode(errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"cannot reach Openverse: {e.reason}")


if __name__ == "__main__":
    main()
