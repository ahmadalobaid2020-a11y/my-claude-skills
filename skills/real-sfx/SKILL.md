---
name: real-sfx
description: Add real recorded sound effects (whoosh, pop, click, swoosh, impact, ding, camera shutter, typing, applause...) to a video or audio at exact timestamps - the user's own files or CC0 recordings from Freesound, mixed under the voice without clipping. Never synthesised tones. Use for "مؤثرات صوتية", "اصوات", "أضف صوت", "sfx", "sound effects", "whoosh on the cut".
---

# real-sfx

Script: `python3 ~/.claude/skills/real-sfx/scripts/sfx.py {search|get|mix} ...`

Only real recordings: the user's own files or Freesound sounds. Never generate tones or noise with ffmpeg/Web Audio as a stand-in for an effect.

| Command | Use |
| --- | --- |
| `search whoosh --max 2` | Freesound search, CC0 only by default, max duration in seconds; prints ID, length, downloads, rating, author |
| `get 60013 51147` | Downloads the HQ preview MP3 of each ID to `~/.claude/sfx/ID-name.mp3` and appends to `CREDITS.txt` |
| `mix VIDEO --cue 00:12.5=whoosh@-8>0.3` | Places sounds and mixes them in; video stream copied untouched |

Cue: `TIME=FILE[@DB][>FADE]`. TIME is `SS`, `MM:SS` or `HH:MM:SS` with decimals; FILE is a path, a Freesound ID or a word matched against file names in `~/.claude/sfx`; `@DB` is the effect gain (default −6); `>FADE` fades out the last N seconds. Repeat `--cue`, or put one per line in a file and pass `--cues FILE` (`#` comments allowed).
Other `mix` options: `--out FILE` (default `NAME.sfx.EXT`; `.wav`/`.mp3`/`.m4a` gives audio only), `--base -2` lowers the original audio, `--dir` for another sound folder. Cues past the end are skipped with a warning. A limiter keeps peaks under −1 dBFS.

Search and get need `FREESOUND_API_KEY` (free: https://freesound.org/apiv2/apply). Without one, ask the user for their own sound files.

## Workflow

1. Find the moments. If the user did not give times, transcribe with `python3 ~/.claude/skills/subtitles/scripts/subtitles.py VIDEO --model small`, and for cuts use
   `ffmpeg -i VIDEO -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*'`.
   Propose a short cue list (time, sound, why) before rendering. Less is more: an effect every few seconds gets tiring; keep them for cuts, text pop-ins, punchlines and transitions.
2. Get sounds: search, pick short, well-rated, much-downloaded results, then `get` them. Reuse what is already in `~/.claude/sfx`.
3. Levels: under speech start at −10 to −6 dB; on silence or music-only parts −6 to 0. Start whooshes ~0.2 s before the cut so the peak lands on it.
4. Mix, then check by measurement since you cannot hear it: `ffmpeg -ss T -t 0.5 -i OUT -af volumedetect -f null -` around a cue versus just before it. Offer a 10 s excerpt for the user to listen to.
5. Report the cue list and output path. For non-CC0 sounds (`--any-license`), give the user the lines from `~/.claude/sfx/CREDITS.txt` for the video description.
