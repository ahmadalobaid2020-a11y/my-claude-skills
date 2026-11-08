---
name: video-shorts
description: Turn a long video into vertical 9:16 shorts (1080x1920) for YouTube Shorts, TikTok and Reels - pick the best moments, reframe, burn Arabic/English captions and a title. Use for "شورتس", "ريلز", "قص مقاطع قصيرة", "shorts", "clips".
---

# video-shorts

Script: `python3 ~/.claude/skills/video-shorts/scripts/shorts.py INPUT --clip START-END [--clip ...] [options]`

| Option | Use |
| --- | --- |
| `--clip 01:10-01:45` | One short per `--clip`; times as `SS`, `MM:SS` or `HH:MM:SS` |
| `--mode blur` | Default. Whole frame centred over a blurred copy; safe for any footage |
| `--mode crop --x 0.5` | Fills the screen; `--x` is the subject's horizontal position (0 left, 1 right) |
| `--subs` | Captions burned in (uses the `subtitles` skill; `--model medium` for Arabic) |
| `--title "..."` | Text box near the top |
| `--out DIR` | Default `shorts/` next to the input |

Outputs `NAME.shortN.mp4`, H.264, `+faststart`, ready to upload.

## Workflow

1. If the user did not give timestamps, transcribe first:
   `python3 ~/.claude/skills/subtitles/scripts/subtitles.py VIDEO --model small`
   and read the SRT to choose moments: a strong hook in the first 2 seconds, one complete idea, 15–60 s, ending on a payoff.
   Propose the clips (time range + one-line reason) and let the user pick before rendering many.
2. Choose framing: one centred speaker → `--mode crop` (find `--x` from a frame: `ffmpeg -ss T -i VIDEO -frames:v 1 f.jpg`, then Read it); screen recordings, slides or two people → `--mode blur`.
3. Render, extract a frame from each short and Read it to check framing, caption position and title.
4. Report paths and durations. Captions are machine transcripts: mention that names and numbers should be checked.
