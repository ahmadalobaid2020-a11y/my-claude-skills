---
name: openverse
description: Find and download openly licensed audio (sound effects, music) and images from Openverse - 800M+ CC0, public-domain and Creative Commons works from Freesound, Wikimedia, Jamendo, Flickr and more - with the licence and attribution kept for every file. No API key. Use for "صور مجانية", "صوت مجاني", "بدون حقوق", "royalty free", "creative commons", "CC0", "free sound effect", "free image", "openverse".
---

# openverse

Script: `python3 ~/.claude/skills/openverse/scripts/openverse.py {audio|image|get} ...`

| Command | Use |
| --- | --- |
| `audio whoosh --license cc0 --max 2` | Sound search; `--max` is the longest clip in seconds; `--source freesound` / `wikimedia_audio` / `jamendo` (music) |
| `image "desert dunes" --commercial --modify` | Image search; prints size, licence, source, creator |
| `get audio ID [ID ...]` | Downloads to `~/.claude/sfx`, where `real-sfx` finds them by ID prefix or name |
| `get image ID [ID ...] --dir DIR` | Downloads to `./openverse` by default |

Licence filters: `--license cc0,pdm` (codes: cc0 pdm by by-sa by-nd by-nc by-nc-sa by-nc-nd), or `--commercial` (allows commercial use) and `--modify` (allows edits).
Every download appends its attribution line and source page to `CREDITS.txt` in the target folder.

## Licences: pick before you search

- Monetised YouTube, ads, client work → `--commercial`, and `--modify` too if the file will be cut, mixed or cropped (sound effects in a video are modified).
- No credit wanted → `--license cc0,pdm`.
- Anything with `BY` needs the credit line in the video description or page; give the user the lines from `CREDITS.txt`. `NC` is never for monetised or client work; `ND` cannot be edited.
- Openverse indexes licences as published by the source; for important commercial use, tell the user to confirm on the source page (third column of `CREDITS.txt`).

## Workflow

1. Ask what it is for (monetised or not) unless obvious, and choose the licence filter from that.
2. Search, then pick: audio short and on-topic (titles from Freesound are usually descriptive); images large enough for the use (1920 wide for video backgrounds, 1280x720 for thumbnails). Show the user 3–5 options with licence and creator before downloading many.
3. `get` the chosen IDs. Read a downloaded image to check it; for audio, check duration with `ffprobe` and hand it to `real-sfx mix` by its ID prefix.
4. Some hosts refuse automated downloads or rate-limit shared cloud IPs. A refused image falls back to Openverse's own resized copy (`.thumb.jpg`, up to the original size Openverse holds); a refused sound fails with its source page link, so the user can download it there and give you the file. Do not retry with browser-imitating headers.
